# -*- coding: utf-8 -*-
import KBEngine
import random
import SCDefine
import time
from KBEDebug import *
from interfaces.GameObject import GameObject

import importlib
import kbe
import Async
importlib.reload(kbe)
importlib.reload(Async)

class Avatar(KBEngine.Proxy, GameObject, kbe.Base):
  """
  角色实体
  """
  def __init__(self):
    KBEngine.Proxy.__init__(self)
    GameObject.__init__(self)

    self.accountEntity = None
    self.cellData["dbid"] = self.databaseID
    self.nameB = self.cellData["name"]
    self.goldB = self.cellData["gold"]
    self.seatIdx = 0
    self.poker = []
    self.discards = []

    self._destroyTimer = 0

  def reset(self):
    self.poker = []
    self.discards = []

  def onClientEnabled(self):
    """
    KBEngine method.
    该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
    cell部分。
    """
    INFO_MSG("Avatar[%i-%s] entities enable. entityCall:%s" % (self.id, self.nameB, self.client))
    KBEngine.globalData["Spaces"].loginToSpaces(self, 1, {})

    if self._destroyTimer > 0:
      self.delTimer(self._destroyTimer)
      self._destroyTimer = 0

  def onGetCell(self):
    """
    KBEngine method.
    entity的cell部分实体被创建成功
    """
    DEBUG_MSG('Avatar::onGetCell: %s' % self.cell)

  def createCell(self, space):
    """
    defined method.
    创建cell实体
    """
    self.createCellEntity(space)

  def destroySelf(self):
    """
    """
    if self.client is not None:
      return

    if self.cell is not None:
      # 销毁cell实体
      self.destroyCellEntity()
      return

    # 如果帐号ENTITY存在 则也通知销毁它
    if self.accountEntity != None:
      if time.time() - self.accountEntity.relogin > 1:
        self.accountEntity.destroy()
      else:
        DEBUG_MSG("Avatar[%i].destroySelf: relogin =%i" % (self.id, time.time() - self.accountEntity.relogin))

    # 销毁base
    if not self.isDestroyed:
      self.destroy()

  #--------------------------------------------------------------------------------------------
  #                              Callbacks
  #--------------------------------------------------------------------------------------------
  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
    if SCDefine.TIMER_TYPE_DESTROY == userArg:
      self.onDestroyTimer()

    GameObject.onTimer(self, tid, userArg)

  def onClientDeath(self):
    """
    KBEngine method.
    entity丢失了客户端实体
    """
    DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
    # 防止正在请求创建cell的同时客户端断开了， 我们延时一段时间来执行销毁cell直到销毁base
    # 这段时间内客户端短连接登录则会激活entity
    self._destroyTimer = self.addTimer(10, 0, SCDefine.TIMER_TYPE_DESTROY)

  def onClientGetCell(self):
    """
    KBEngine method.
    客户端已经获得了cell部分实体的相关数据
    """
    INFO_MSG("Avatar[%i].onClientGetCell:%s" % (self.id, self.client))

  def onDestroyTimer(self):
    DEBUG_MSG("Avatar::onDestroyTimer: %i" % (self.id))
    self.destroySelf()

  def onDestroy(self):
    """
    KBEngine method.
    entity销毁
    """
    DEBUG_MSG("Avatar::onDestroy: %i." % self.id)

    if self.accountEntity != None:
      self.accountEntity.activeAvatar = None
      self.accountEntity = None

  # @Async.async_func
  # def doJoinRoom(self, roomCell):
  #     ''' 加入房间 '''
  #     assert not self.cell
  #     self.createCell(roomCell)
  #     yield self.whenGetCell()
  #     # 通知 cell 部分
  #     self.cell.joinRoom(roomCell.id)

  # @Async.async_func
  # def doLeaveRoom(self):
  #     ''' 离开房间, 保证 cell 被销毁 '''
  #     account = self.getAccount()
  #     if account and self.hasClient:
  #         # 把客户端还给 Acount
  #         self.giveClientTo(account)
  #     if self.cell:
  #         self.destroyCellEntity()
  #         yield self.whenLoseCell()

  def reqCreateRoom(self, gameName, level, maxRound, playerCount):
      '''
      请求创建房间, def 中定义, 客户端请求
      @param gameName : 游戏名称
      @param level    : 房间等级
      '''
      DEBUG_MSG("Avatar[%i].reqCreateRoom name=%s, lv=%i maxRound=%i, playerCount=%i." % (self.id, gameName, level, maxRound, playerCount))
      self.getSpaces().doMatchGame(self, gameName, level, maxRound, playerCount)

  def reqJoinRoom(self, roomId):
      '''
      请求加入房间, def 中定义, 客户端请求
      @param roomId : 房间 id
      '''
      DEBUG_MSG("Avatar[%i].reqJoinRoom roomId=%s." % (self.id, roomId))
      self.getSpaces().doPlayerJoinSpace(self, roomId)

  def reqLeaveRoom(self, roomId):
      '''
      请求离开房间, def 中定义, 客户端请求
      @param roomId : 房间号
      '''
      DEBUG_MSG("Avatar[%i].reqLeaveRoom roomId=%s." % (self.id, roomId))
      if self.cell:
          self.destroyCellEntity()
      self.getSpaces().logoutSpace(self.id, roomId)

  def reqPrepare(self, roomId, isReady):
      '''
      请求准备, def 中定义, 客户端请求
      @param roomId : 房间号
      @param isReady : 是否准备
      '''
      DEBUG_MSG("Avatar[%i].reqPrepare roomId=%s, isReady=%s." % (self.id, roomId, isReady))
      self.getSpaces().reqPrepare(self, roomId, isReady)

  def reqMJFinalResult(self, roomId):
      '''
      请求最终结果, def 中定义, 客户端请求
      @param roomId : 房间号
      '''
      DEBUG_MSG("Avatar[%i].reqMJFinalResult roomId=%s." % (self.id, roomId))
      self.getSpaces().reqMJFinalResult(self, roomId)
