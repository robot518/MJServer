# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

import kbe
import Async

class GameDdz(KBEngine.Entity, kbe.Base):
  """
  一个可操控cellapp上真正space的实体
  注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
  """
  def __init__(self):
    KBEngine.Entity.__init__(self)

    self.ddzPlayers = {}

    DEBUG_MSG("GameDdz::__init__: %d" % (self.id))

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
    self.ddzPlayers[entityCall.id] = entityCall

    if self.cell is not None:
      self.cell.onEnter(entityCall, entityCall.seatIdx)

  def onLeave(self, entityID):
    """
    defined method.
    离开场景
    """
    if entityID in self.ddzPlayers:
      del self.ddzPlayers[entityID]

    if self.cell is not None:
      self.cell.onLeave(entityID)

  @Async.async_func
  def initCell(self):
      ''' 初始化房间 cell '''
      DEBUG_MSG("GameDdz::initCell: %i" % self.id)
      assert not self.cell
      self.createCellEntityInNewSpace(None)
      yield self.whenGetCell()
      DEBUG_MSG("GameDdz::whenGetCell: %i" % self.id)
      return self.cell
