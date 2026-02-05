# -*- coding: utf-8 -*-
import KBEngine
import SCDefine
from KBEDebug import *

class GameObject:
  """
  服务端游戏对象的基础接口类
  """
  def __init__(self):
    pass

  def initEntity(self):
    """
    virtual method.
    """
    pass

  def isPlayer(self):
    """
    virtual method.
    """
    return False

  def getScriptName(self):
    return self.__class__.__name__

  def getCurrSpaceBase(self):
    """
    获得当前space的entity baseEntityCall
    """
    return KBEngine.globalData["space_%i" % self.spaceID]

  #应该不能用了
  def getCurrSpace(self):
    """
    获得当前space的entity
    """
    spaceBase = self.getCurrSpaceBase()
    return KBEngine.entities.get(spaceBase.id, None)

  def getSpaces(self):
    """
    获取场景管理器
    """
    return KBEngine.globalData["Spaces"]

  def startDestroyTimer(self):
    """
    virtual method.

    启动销毁entitytimer
    """
    pass
    # if self.isState(GlobalDefine.ENTITY_STATE_DEAD):
    # 	self.addTimer(5, 0, SCDefine.TIMER_TYPE_DESTROY)
      # DEBUG_MSG("%s::startDestroyTimer: %i running." % (self.getScriptName(), self.id))

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
      self.onDestroyEntityTimer()

  # def onStateChanged_(self, oldstate, newstate):
  # 	"""
  # 	virtual method.
  # 	entity状态改变了
  # 	"""
  # 	self.startDestroyTimer()

  def onRestore(self):
    """
    KBEngine method.
    entity的cell部分实体被恢复成功
    """
    DEBUG_MSG("%s::onRestore: %s" % (self.getScriptName(), self.base))

  def onDestroyEntityTimer(self):
    """
    entity的延时销毁timer
    """
    self.destroy()
