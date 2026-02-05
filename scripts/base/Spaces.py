# -*- coding: utf-8 -*-
import KBEngine
import SCDefine
from KBEDebug import *
from interfaces.GameObject import GameObject
import random

import importlib
import kbe
import Async
import cfg_room
from MJResultMgr import MJResultMgr
importlib.reload(cfg_room)

class Room:
    ''' 记录房间相关信息 '''
    def __init__(self, base, className, level, maxRound, playerCount):
        self.base = base
        self.className = className
        self.level = level
        self.players = []
        self.robots = []
        self.currentRound = 1
        self.maxRound = maxRound
        self.playerCount = playerCount
        self.isStarted = False

class Spaces(KBEngine.Entity, GameObject, kbe.Base):
  """
  这是一个脚本层封装的空间管理器
  KBEngine的space是一个抽象空间的概念，一个空间可以被脚本层视为游戏场景、游戏房间、甚至是一个宇宙。
  """
  def __init__(self):
    KBEngine.Entity.__init__(self)
    GameObject.__init__(self)

    # 初始化空间分配器
    # self.initAlloc()

    # 向全局共享数据中注册这个管理器的entityCall以便在所有逻辑进程中可以方便的访问
    KBEngine.globalData["Spaces"] = self
    self.mjResultMgr = MJResultMgr(self)

    self._rooms = {}

    self.addTimer(10, 10, SCDefine.TIMER_TYPE_SET_DDZ_ROBOT)

  def getRoomPlayers(self, foundRoomid):
    t = []
    room = self._rooms[foundRoomid]
    for p in room.players:
      t.append({"playerName": p.nameB, "seatIdx": p.seatIdx, "isReady": p.isReady, "winScore": p.winScore})
    return t

  def loginToSpaces(self, avatarEntity, spaceUType, context):
    """
    defined method.
    某个玩家请求登陆到某个space中
    """
    DEBUG_MSG("%s::loginToSpaces: %i avatarEntity.id=%i" % (self.getScriptName(), self.id, avatarEntity.id))
    for roomId, room in self._rooms.items():
      DEBUG_MSG("%s::loginToSpaces roomId=%i playerCount=%i" % (self.getScriptName(), roomId, len(room.players)))
      for player in room.players:
        DEBUG_MSG("%s::loginToSpaces player.id=%i" % (self.getScriptName(), player.id))
        if player.nameB == avatarEntity.nameB: # 重写登录时，旧的连接被踢掉，旧的avatar被删了
          avatarEntity.seatIdx = player.seatIdx
          avatarEntity.isReady = player.isReady
          room.players.remove(player)
          room.players.append(avatarEntity)
          if room.isStarted == False:
            DEBUG_MSG("%s::loginToSpaces onInitRoom: %i currentRound=%i" % (self.getScriptName(), self.id, room.currentRound))
            avatarEntity.client.onInitRoom(roomId, room.className, self.getRoomPlayers(roomId), room.currentRound, room.maxRound, room.playerCount)
          if not avatarEntity.cell:
            room.base.loginToSpace(avatarEntity, {})
          return
    DEBUG_MSG("%s::loginToSpaces onLoginSpacesCallback: %i" % (self.getScriptName(), self.id))
    if avatarEntity.client:
      avatarEntity.client.onLoginSpacesCallback()

  def loginToSpace(self, avatarEntity, spaceUType, context):
    """
    defined method.
    某个玩家请求登陆到某个space中
    """
    pass

  def logoutSpace(self, avatarID, spaceKey):
    """
    defined method.
    某个玩家请求登出这个space
    """
    DEBUG_MSG("%s::logoutSpace: avatarID=%i spaceKey=%i" % (self.getScriptName(), avatarID, spaceKey))
    if spaceKey in self._rooms:
      room = self._rooms[spaceKey]
      for p in room.players:
        DEBUG_MSG("%s::logoutSpace: p.id=%i" % (self.getScriptName(), p.id))
        if p.id == avatarID:
          for q in room.players:
            if not q.isDestroyed and q.id != avatarID and q.client:
              q.client.onReqLeaveRoom(p.seatIdx)
          self.disbandRoom(spaceKey, None)
          return

  def disbandRoom(self, roomId, mjFinalPlayerData):
    room = self._rooms[roomId]
    if mjFinalPlayerData:
      self.mjResultMgr.add_resultInfo(roomId, room.playerCount, room.currentRound, mjFinalPlayerData)
    for p in room.players:
      if p.cell:
        p.destroyCellEntity()
      room.base.logoutSpace(p.id)
    self._rooms[roomId] = None
    del self._rooms[roomId] # dict删除元素的方式 有延迟

  def reqMJFinalResult(self, avatarEntity, roomId):
    self.mjResultMgr.get_resultInfo(avatarEntity, roomId)

  #--------------------------------------------------------------------------------------------
  #                              Callbacks
  #--------------------------------------------------------------------------------------------
  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
    if SCDefine.TIMER_TYPE_SET_DDZ_ROBOT == userArg:
      self._onCheckRoomRobot()

    GameObject.onTimer(self, tid, userArg)

  def onSpaceLoseCell(self, spaceUType, spaceKey):
    """
    defined method.
    space的cell创建好了
    """
    pass

  def onSpaceGetCell(self, spaceUType, spaceEntityCall, spaceKey):
    """
    defined method.
    space的cell创建好了
    """
    pass

  @Async.async_func
  def doCreateSpace(self, gameName, level, maxRound, playerCount):
      ''' 创建房间并等待 initCell 获取到 room 的 cell '''
      room = yield kbe.createEntityAnywhere(gameName, {'level': level})
      DEBUG_MSG("Spaces[%i].doCreateSpace room=%s." % (self.id, room))
      if room:
          DEBUG_MSG("Spaces[%i].request." % (self.id))
          roomCell = yield self.request(room, 'initCell')
          if room.id < 1000:
            newId = (room.id+1000)*100+random.randint(1, 100)
          else:
            newId = room.id*100+random.randint(1, 100)
          DEBUG_MSG("Spaces[%i].doCreateRoom room=%s newId=%i." % (self.id, room.id, newId))
          self._rooms[newId] = Room(room, gameName, level, maxRound, playerCount)
          return newId

  @Async.async_func
  def doMatchGame(self, player, gameName, level, maxRound, playerCount):
      '''
      匹配游戏, 远程定义
      @param player : 玩家实体对象/Mailbox
      @param gameName : 匹配的游戏名称, 也就是类名
      @param level : 匹配的游戏等级
      @param filterRoomid : 筛除的房间id, 用于更换房间功能
      '''
      DEBUG_MSG("Spaces[%i] player[%i].doMatchGame gameName=%s maxRound=%i playerCount=%i." % (self.id, player.id, gameName, maxRound, playerCount))
      foundRoomid = yield self.doCreateSpace(gameName, level, maxRound, playerCount)
      room = self._rooms[foundRoomid]
      player.seatIdx = 0
      player.isReady = 0
      player.winScore = 0
      room.players.append(player)
      room.base.loginToSpace(player, {})
      player.client.onInitRoom(foundRoomid, gameName, self.getRoomPlayers(foundRoomid), 1, maxRound, playerCount)
      DEBUG_MSG("Spaces[%i].doMatchGame end foundRoomid=%s playerCount=%i." % (self.id, foundRoomid, len(room.players)))

  def getNextSeatIdx(self, roomId):
      room = self._rooms[roomId]
      for i in range(0, room.playerCount):
          found = False
          for p in room.players:
              if p.seatIdx == i:
                  found = True
                  break
          if not found:
              return i

  def doPlayerJoinSpace(self, player, roomId):
    ''' 玩家加入房间 '''
    DEBUG_MSG("Spaces[%i] player[%i].doPlayerJoinSpace roomId=%s." % (self.id, player.id, roomId))
    # check roomId
    if not roomId in self._rooms:
      DEBUG_MSG("Spaces[%i].doPlayerJoinSpace err=%s code=%s." % (self.id, "roomId not found", KBEngine.SERVER_ERR_USER1))
      player.client.onReqJoinRoomFailed(KBEngine.SERVER_ERR_USER1)
      return
    room = self._rooms[roomId]
    player.seatIdx = self.getNextSeatIdx(roomId)
    player.isReady = 0
    player.winScore = 0
    room.players.append(player)
    room.base.loginToSpace(player, {})
    if player.client:
      player.client.onInitRoom(roomId, room.className, self.getRoomPlayers(roomId), 1, room.maxRound, room.playerCount)
    for p in room.players:
      if p.id != player.id and p.client:
        p.client.onPlayerJoinRoom(roomId, room.className, player.nameB, player.goldB, player.seatIdx)
    DEBUG_MSG("Spaces[%i].doPlayerJoinSpace end seatIdx=%i." % (self.id, player.seatIdx))



  def reqPrepare(self, player, roomId, isReady):
    ''' 玩家准备 '''
    DEBUG_MSG("Spaces[%i].reqPrepare roomId=%s isReady=%s." % (self.id, roomId, isReady))
    if not roomId in self._rooms:
      DEBUG_MSG("Spaces[%i].reqPrepare err=%s code=%s." % (self.id, "roomId not found", KBEngine.SERVER_ERR_USER1))
      player.client.onReqJoinRoomFailed(KBEngine.SERVER_ERR_USER1)
      return
    room = self._rooms[roomId]
    player.isReady = isReady
    for p in room.players:
      if not p.isDestroyed and p.id != player.id and p.client:
        p.client.onReqPrepare(roomId, room.className, player.seatIdx, isReady)
    self.onCheckStart(roomId)

  def onNextRound(self, roomId, scorePlayers):
    ''' 游戏结束 '''
    room = self._rooms[roomId]
    for p in room.players:
      p.isReady = 0
      for scorePlayer in scorePlayers:
        if p.seatIdx == scorePlayer.get("seatIdx"):
          p.winScore = scorePlayer.get("score")
          break
      DEBUG_MSG("Spaces[%i].onNextRound roomId=%s player=%s winScore=%s." % (self.id, roomId, p.nameB, p.winScore))
    room.isStarted = False
    room.currentRound += 1

  def onCheckStart(self, roomId):
    ''' 检查是否开始游戏 '''
    room = self._rooms[roomId]
    # seatMin = cfg_room.game_seat_min[room.className]
    if len(room.players) == room.playerCount:
      for p in room.players:
        if p.isReady == 0:
          return
      # 开始游戏
      DEBUG_MSG("Spaces[%i].onCheckStart roomId=%s gameName=%s." % (self.id, roomId, room.className))
      # 重置准备状态
      room.isStarted = True
      for p in room.players:
        p.isReady = 0
      if room.className == "GameMJ":
        if room.currentRound > room.maxRound:
          ERROR_MSG("Spaces[%i].onCheckStart roomId=%s gameName=%s currentRound=%i maxRound=%i." % (self.id, roomId, room.className, room.currentRound, room.maxRound))
        room.base.cell.onGameStart(room.currentRound, room.maxRound, roomId, room.playerCount)
      elif room.className == "GameDdz":
        room.base.cell.onGameStart()

  def _onCheckRoomRobot(self):
    ''' 定时检查所有房间机器人添加或移除情况 '''
    return
    for roomId, room in self._rooms.items():
        playerCount = len(room.players)
        # seatMin = cfg_room.game_seat_min[room.className]
        if room.className == "GameDdz" and playerCount != room.playerCount:
            ''' 添加机器人 '''
            # goldMin = cfg_room.game_level[room.level]['goldMin']
            props = {
              "name"				: "bot" + str(random.randint(1, 500)),
              "roleType"			: 0,
              "gold"				: 100,
              "seatIdx"     : 0,
              "isReady"     : 0,
              "winScore"    : 0,
              "isRobot"     : 1,
            }

            avatar = KBEngine.createEntityLocally('Avatar', props)
            self.doPlayerJoinSpace(avatar, roomId)
            self.reqPrepare(avatar, roomId, 1)
        elif room.className == "GameMJ" and playerCount != room.playerCount:
            props = {
              "name"				: "bot" + str(random.randint(1, 500)),
              "roleType"			: 0,
              "gold"				: 100,
              "seatIdx"     : 0,
              "isReady"     : 0,
              "winScore"    : 0,
              "isRobot"     : 1,
            }

            avatar = KBEngine.createEntityLocally('Avatar', props)
            self.doPlayerJoinSpace(avatar, roomId)
            self.reqPrepare(avatar, roomId, 1)
