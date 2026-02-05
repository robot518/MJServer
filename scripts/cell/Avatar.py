# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.GameObject import GameObject

class Avatar(KBEngine.Entity,
      GameObject,):
  def __init__(self):
    KBEngine.Entity.__init__(self)
    GameObject.__init__(self)
    DEBUG_MSG("Avatar::cell __init__: %d self.isRobot=%i" % (self.id, self.isRobot))

  def isPlayer(self):
    """
    virtual method.
    """
    return True

  def startDestroyTimer(self):
    """
    virtual method.

    启动销毁entitytimer
    """
    pass

  #--------------------------------------------------------------------------------------------
  #                              Callbacks
  #--------------------------------------------------------------------------------------------
  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
    GameObject.onTimer(self, tid, userArg)

  def onDestroy(self):
    """
    KBEngine method.
    entity销毁
    """
    DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
    self.getCurrSpace().reqOffline(self)

  def joinRoom(self, roomid):
    ''' 加入房间 '''
    room = KBEngine.entities.get(roomid)
    room.onJoin(self)

  def reqBeLandLord(self, isLandLord):
    ''' 请求当地主 '''
    self.getCurrSpace().reqBeLandLord(self, isLandLord)

  def reqOutputCards(self, cards):
    ''' 请求出牌 '''
    self.getCurrSpace().reqOutputCards(self, cards)

  def reqPass(self):
    ''' 请求过牌 '''
    self.getCurrSpace().reqPass(self)


  # mj
  def reqOutputMjTile(self, strTile):
    ''' 请求打牌 '''
    self.getCurrSpace().reqOutputMjTile(self, strTile)

  def reqNewTile(self):
    ''' 请求摸牌 '''
    self.getCurrSpace().reqNewTile(self)

  def reqMeldEvent(self, strMeldType, meldTile):
    ''' 请求碰杠 '''
    self.getCurrSpace().reqMeldEvent(self, strMeldType, meldTile)
