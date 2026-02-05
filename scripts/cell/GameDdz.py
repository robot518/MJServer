# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.GameObject import GameObject
import ddz_util
import SCDefine

from enum import Enum

class GameState(Enum):
    WAITING = 1
    STARTED = 2
    ENDED = 3

class DDZPlayer:
  def __init__(self, entityCall, seatIdx, playerName):
    self.entityCall = entityCall
    self.seatIdx = seatIdx
    self.playerName = playerName
    self.pokers = []
    self.ouputPokers = []
    self.isOffline = False
    self.winScore = 0

  def resetData(self):
    ''' 重置数据 '''
    self.pokers = []
    self.ouputPokers = []
    self.isOffline = False
    self.winScore = 0

  def initHandPokers(self, pokers):
    ''' 初始化手牌 '''
    self.pokers = pokers

  def beLandLord(self, pokers):
    ''' 当地主 '''
    self.pokers.extend(pokers)

  def removeHandPokers(self, pokers):
    ''' 移除手牌 '''
    for card in pokers:
      if card in self.pokers:
        self.pokers.remove(card)
      else:
        ERROR_MSG("DDZPlayer::removeHandPokers: card=%i not in pokers" % (card))

  def changeEntityCall(self, entityCall):
    ''' 重置实体 '''
    self.entityCall = entityCall
    self.client = entityCall.client

class GameDdz(KBEngine.Entity, GameObject):
  """
  游戏场景，在这里代表野外大地图
  """
  def __init__(self):
    KBEngine.Entity.__init__(self)
    GameObject.__init__(self)

    KBEngine.globalData["space_%i" % self.spaceID] = self.base

    self.ddzPlayers = {}
    self.lastDiscardSeat = -1
    self.gameState = GameState.WAITING

  #--------------------------------------------------------------------------------------------
  #                              Callbacks
  #--------------------------------------------------------------------------------------------
  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.getScriptName(), self.id, tid, userArg))
    # if SCDefine.TIMER_TYPE_CREATE_SPACES == userArg:
      # self.createSpaceOnTimer(tid)

    if SCDefine.TIMER_TYPE_NEXT_TURN == userArg:
      iNextSeatIdx = (self.lastDiscardSeat + 1) % 3
      DEBUG_MSG("GameDdz::onTimer: iNextSeatIdx=%i" % iNextSeatIdx)
      self.reqPass(self.ddzPlayers[iNextSeatIdx])

    GameObject.onTimer(self, tid, userArg)

  def onDestroy(self):
    """
    KBEngine method.
    """
    del KBEngine.globalData["space_%i" % self.spaceID]
    self.destroySpace()

  def getDDZPlayerBySeatIdx(self, seatIdx):
    ''' 获取玩家 '''
    for id, p in self.ddzPlayers.items():
      if p.seatIdx == seatIdx:
        return p
    return None

  # def resetDDZGamePlayers(self, iSeatIdx):
  #   ''' 获取游戏玩家 '''
  #   for id, p in self.ddzPlayers.items():
  #     player = TMJGamePlayer()
  #     seatIdx = p.seatIdx
  #     handTiles = iSeatIdx == seatIdx and p.tileStacks or []
  #     player.extend([p.huaScore, p.dictMelds, handTiles, p.outputTileStacks, len(p.tileStacks),
  #                    seatIdx, p.playerName, p.isOffline, p.winScore])
  #     self.gamePlayers[seatIdx] = player

  def onEnter(self, entityCall, iSeatIdx):
    """
    defined method.
    进入场景
    """
    DEBUG_MSG('GameDdz::onEnter space[%d] entityID = %i.' % (self.id, entityCall.id))
    # self.ddzPlayers[seatIdx] = entityCall

    # 重复登录
    if entityCall.id in self.ddzPlayers:
      return
    ddzPlayer = self.getDDZPlayerBySeatIdx(iSeatIdx)
    # 第一次登录
    if ddzPlayer == None:
      avatar = KBEngine.entities.get(entityCall.id)
      if avatar:
        ddzPlayer = DDZPlayer(entityCall, iSeatIdx, avatar.name)
        self.ddzPlayers[entityCall.id] = ddzPlayer
      else:
        ERROR_MSG("GameDdz::onEnter: %i entityCall.id=%i not found" % (self.id, entityCall.id))
    # 踢出离线玩家
    else:
      oldPlayer = self.getDDZPlayerBySeatIdx(iSeatIdx)
      if not oldPlayer.isOffline:
        ERROR_MSG("GameDdz::onEnter: %i seatIdx=%i oldPlayer=%s not offline" % (self.id, iSeatIdx, oldPlayer.isOffline))
        # return
      self.ddzPlayers[entityCall.id] = oldPlayer
      del self.ddzPlayers[oldPlayer.entityCall.id]
      oldPlayer.changeEntityCall(entityCall)
      oldPlayer.setOffline(False)
      for id, p in self.ddzPlayers.items():
        if p.client and id != entityCall.id:
          p.client.onOffline(iSeatIdx, 0)
    if self.gameState == GameState.STARTED:
      leftNum = len(self.leftTiles)
      # self.resetDDZGamePlayers(iSeatIdx)
      # for id, p in self.ddzPlayers.items():
      #   if p.client and p.seatIdx == iSeatIdx:
      #     DEBUG_MSG("GameDdz::onEnter: self.ghostTile=%s, seatIdx=%i, leftNum=%i self.lastOutputTile=%s self.bankerIdx=%i self.curTurn=%i" %
      #               (self.ghostTile, p.seatIdx, leftNum, self.lastOutputTile, self.bankerIdx, self.curTurn))
      #     for idx in self.gamePlayers:
      #       DEBUG_MSG("GameDdz::onEnter: idx=%s" % (idx))
      #     p.client.onReConnectRoom(self.roomID, "GameDdz", self.curRound, self.maxRound, self.playerCount, self.ghostTile,
      #                              leftNum, self.lastOutputTile, self.lastDiscardSeat, self.bankerIdx,
      #                              self.curTurn, self.bOutputTile, self.gamePlayers)
      #     break

  def onLeave(self, entityID):
    """
    defined method.
    离开场景
    """
    DEBUG_MSG('GameDdz::onLeave space[%d] entityID = %i.' % (self.id, entityID))
    if entityID in self.ddzPlayers:
      del self.ddzPlayers[entityID]
    else:
      ERROR_MSG("GameDdz::onLeave: %i entityID=%i not found" % (self.id, entityID))

  # def reset(self):
    # 开局标志
    # self.started = 0
    # 庄家座位号
    # self.bankerSeat = -1 # seatIdx = 0
    # self.turnCutdown = -1
    # 地主牌
    # self.bankerPoker = []
    # self.lastDiscardSeat = -1

  def onGameStart(self):
    ''' 游戏开始 '''
    pokers = list(ddz_util.fapai())
    DEBUG_MSG("GameDdz::onGameStart: %i pokers=%s" % (self.id, pokers))
    idx = 0
    for id, p in self.ddzPlayers.items():
      p.resetData()
      DEBUG_MSG("GameDdz::onGameStart: i=%i, pokers=%s" % (id, pokers[idx]))
      p.initHandPokers(pokers[idx])
      idx += 1
    self.bankerPoker = pokers.pop()
    for seatIdx, p in self.ddzPlayers.items():
      if p.client:
        poker = pokers[seatIdx]
        DEBUG_MSG ("GameDdz::onGameStart: p.id=%i seatIdx=%i, %s" % (p.id, seatIdx, poker))
        iTurn = seatIdx == 0 and 1 or 0
        p.client.onDdzGameStart(poker, iTurn)
    self.gameState = GameState.STARTED

  def getSeatIdx(self, entityCall):
    ''' 获取座位号 '''
    for seatIdx, p in self.ddzPlayers.items():
      if p.id == entityCall.id:
        return seatIdx
    return -1

  def reqBeLandLord(self, entityCall, isLandLord):
    ''' 请求当地主 '''
    if not self.isGameRunning():
      return
    iSeatIdx = self.getSeatIdx(entityCall)
    self.lastDiscardSeat = iSeatIdx
    ddzPlayer = self.ddzPlayers[iSeatIdx]
    ddzPlayer.beLandLord(self.bankerPoker)
    DEBUG_MSG("GameDdz[%i]::reqBeLandLord: iSeatIdx=%i, isLandLord=%i, bankCount=%i" % (self.id, iSeatIdx, isLandLord, len(ddzPlayer.pokers)))
    for seatIdx, p in self.ddzPlayers.items():
      if p.client:
        DEBUG_MSG("GameDdz::onReqBeLandLord: p.id=%i, seatIdx=%i" % (p.id, seatIdx))
        p.client.onReqBeLandLord(iSeatIdx, isLandLord, self.bankerPoker)

  def reqOutputCards(self, entityCall, cards):
    ''' 请求出牌 '''
    if not self.isGameRunning():
      return
    iSeatIdx = self.getSeatIdx(entityCall)
    self.lastDiscardSeat = iSeatIdx
    DEBUG_MSG("GameDdz::reqOutputCards: %i iSeatIdx=%i" % (self.id, iSeatIdx))
    # remove cards in self.lPokers
    ddzPlayer = self.ddzPlayers[iSeatIdx]
    ddzPlayer.removeHandPokers(cards)
    iLeftNum = len(ddzPlayer.pokers)
    for seatIdx, p in self.ddzPlayers.items():
      if p.id != entityCall.id and p.client:
        DEBUG_MSG("GameDdz::onReqOutputCards: p.id=%i, seatIdx=%i iLeftNum=%i" % (p.id, seatIdx, iLeftNum))
        p.client.onReqOutputCards(iSeatIdx, cards, iLeftNum)
    self.onGameOverCheck(iLeftNum)
    self.onCheckRobotTurn(iSeatIdx)

  def reqPass(self, entityCall):
    ''' 请求过牌 '''
    if not self.isGameRunning():
      return
    iSeatIdx = self.getSeatIdx(entityCall)
    self.lastDiscardSeat = iSeatIdx
    DEBUG_MSG("GameDdz::reqPass: %i iSeatIdx=%i" % (self.id, iSeatIdx))
    for seatIdx, p in self.ddzPlayers.items():
      if p.id != entityCall.id and p.client:
        DEBUG_MSG("GameDdz::onReqPass: p.id=%i, seatIdx=%i iSeatIdx=%i" % (p.id, seatIdx, iSeatIdx))
        p.client.onReqPass(iSeatIdx)
    self.onCheckRobotTurn(iSeatIdx)

  def onCheckRobotTurn(self, iSeatIdx):
    ''' 检查机器人出牌 '''
    if not self.isGameRunning():
      return
    # iNextSeatIdx = (iSeatIdx + 1) % 3
    # avatar = self.ddzPlayers[iNextSeatIdx]
    # cellAvatar = KBEngine.entities.get(avatar.id)
    # DEBUG_MSG("GameDdz::reqPass: iNextSeatIdx=%i, avatar.id=%i cellAvatar.isRobot=%i" % (iNextSeatIdx, avatar.id, cellAvatar.isRobot))
    # if cellAvatar.isRobot:
    #   self.addTimer(2, 0, SCDefine.TIMER_TYPE_NEXT_TURN)

  def onGameOverCheck(self, iLeftNum):
    ''' 游戏结束检查 '''
    DEBUG_MSG("GameDdz::onGameOverCheck: %i seatIdx=%i" % (self.id, iLeftNum))
    if iLeftNum == 0:
      self.gameState = GameState.ENDED

  def isGameRunning(self):
    ''' 游戏状态检查 '''
    DEBUG_MSG("GameDdz::onGameStateCheck: %i gameState=%s" % (self.id, self.gameState.name))
    if self.gameState == GameState.STARTED:
      return True
    else:
      return False

