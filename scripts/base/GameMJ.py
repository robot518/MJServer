# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

import kbe
import Async
import SCDefine

class GameMJ(KBEngine.Entity, kbe.Base):
  """
  一个可操控cellapp上真正space的实体
  注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
  """
  def __init__(self):
    KBEngine.Entity.__init__(self)

    self.mjPlayers = {}

    DEBUG_MSG("GameMJ::__init__: %d" % (self.id))

  def loginToSpace(self, avatarEntityCall, context):
    """
    defined method.
    某个玩家请求登陆到这个space中
    """
    # 晚于onGetCell
    avatarEntityCall.createCell(self.cell)
    self.onEnter(avatarEntityCall)

  def logoutSpace(self, entityID):
    """
    defined method.
    某个玩家请求登出这个space
    """
    self.onLeave(entityID)

  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    pass

  def onEnter(self, entityCall):
    """
    defined method.
    进入场景
    """
    self.mjPlayers[entityCall.id] = entityCall

    if self.cell is not None:
      self.cell.onEnter(entityCall, entityCall.seatIdx)

  # 不先删除cell实体，先删除base回报错，删除cell有延迟，要分开删除
  def onLeave(self, entityID):
    """
    defined method.
    离开场景
    """
    if entityID in self.mjPlayers:
      del self.mjPlayers[entityID]

    if self.cell is not None:
      self.cell.onLeave(entityID)

    if len(self.mjPlayers) == 0:
      self._destroyTimer = self.addTimer(10, 0, SCDefine.TIMER_TYPE_DESTROY)

  @Async.async_func
  def initCell(self):
      ''' 初始化房间 cell '''
      DEBUG_MSG("GameMJ::initCell: %i" % self.id)
      assert not self.cell
      self.createCellEntityInNewSpace(None)
      yield self.whenGetCell()
      DEBUG_MSG("GameMJ::whenGetCell: %i" % self.id)
      return self.cell

  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
    if SCDefine.TIMER_TYPE_DESTROY == userArg:
      self.destroySelf()

  def destroySelf(self):
    """
    """
    if self.client is not None:
      return

    if self.cell is not None:
      # 销毁cell实体
      self.destroyCellEntity()
      DEBUG_MSG("GameMJ::destroySelf cell: %i" % self.id)
      return

    # 销毁base
    self.destroy()
    self.delTimer(self._destroyTimer)
    DEBUG_MSG("GameMJ::destroySelf: %i" % self.id)
