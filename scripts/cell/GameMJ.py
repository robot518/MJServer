# -*- coding: utf-8 -*-
import random
import KBEngine
from KBEDebug import *
from interfaces.GameObject import GameObject
import mj_util

from enum import Enum

from MJ_GAME_RESULT_PLAYER import TMJGameResultPlayer
from MJ_GAME_PLAYER import TMJGamePlayer
import SCDefine

class GameState(Enum):
    WAITING = 1
    STARTED = 2
    ENDED = 3

class MJPlayer:
  def __init__(self, entityCall, seatIdx, playerName):
    self.entityCall = entityCall # 实体与客户端通信
    self.client = entityCall.client # 客户端
    self.seatIdx = seatIdx # 座位号 0-3
    self.playerName = playerName # 名字
    self.tileStacks = [] # 手牌
    self.outputTileStacks = [] # 打出去的牌
    self.dictMelds = [] # 吃碰的牌 {"strMeldType": strMeldType, "tiles": [meldTile, self.lastOutputTile]}
    self.huaScore = 0 # 花分
    self.isOffline = False # 是否离线
    self.angangTiles = [] # 暗杠
    self.winScore = 0 # 分数
    self.winDict = {} # 胡牌类型 {"hu": 1, "zimo": 1, "sanjindao": 1}

  def getGhostCount(self, ghostTile):
    ghostCount = 0
    for tile in self.tileStacks:
      if tile == ghostTile:
        ghostCount += 1
    return ghostCount

  def addWinDict(self, strWinType, ghostTile):
    ''' 添加胡牌类型 '''
    ghostCount = self.getGhostCount(ghostTile)
    # 得分=花分+金+杠, 自摸*2
    winScore = self.huaScore + len(self.angangTiles) + ghostCount + 1
    if strWinType == "zimo":
      winScore *= 2
    if strWinType in self.winDict:
      self.winDict[strWinType] += 1
    else:
      self.winDict[strWinType] = 1
    self.winScore += winScore
    return winScore

  def addWinScore(self, score):
    ''' 加分 '''
    self.winScore += score

  def addHuaScore(self):
    ''' 加花分 '''
    self.huaScore += 1

  def resetData(self):
    self.huaScore = 0
    self.outputTileStacks = []
    self.dictMelds = []
    self.angangTiles = []

  def initTileStacks(self, tileStacks):
    ''' 初始化手牌 '''
    self.tileStacks = tileStacks

  def addHandTile(self, tile):
    ''' 添加手牌 '''
    self.tileStacks.append(tile)

  def removeHandTile(self, tile):
    ''' 移除手牌 '''
    self.tileStacks.remove(tile)

  def addOutputTileStacks(self, tile):
    ''' 添加打出去的牌 '''
    self.outputTileStacks.append(tile)

  def removeLastOutputTile(self):
    ''' 移除打出去的牌 '''
    self.outputTileStacks.pop()

  def addDictMelds(self, meld):
    ''' 添加吃碰的牌 '''
    self.dictMelds.append(meld)

  def addAngangTile(self, tile):
    ''' 添加暗杠的牌 '''
    self.angangTiles.append(tile)

  def changeEntityCall(self, entityCall):
    ''' 重置实体 '''
    self.entityCall = entityCall
    self.client = entityCall.client

  def setOffline(self, isOffline):
    ''' 设置离线 '''
    self.isOffline = isOffline

class GameMJ(KBEngine.Entity, GameObject):
  """
  游戏场景，在这里代表野外大地图
  """
  def __init__(self):
    KBEngine.Entity.__init__(self)
    GameObject.__init__(self)

    KBEngine.globalData["space_%i" % self.spaceID] = self.base

    self.mjPlayers = {}

    self.lastDiscardSeat = 10
    self.gameState = GameState.WAITING
    self.leftTiles = [] # 剩余的牌
    self.bankerIdx = 10 # 庄家
    self.curTurn = 10
    self.lastOutputTile = 0
    self.ghostTile = 0
    self.bOutputTile = 0

    self.curRound = 0
    self.maxRound = 8
    self.roomID = 0
    self.playerCount = 0

  #--------------------------------------------------------------------------------------------
  #                              Callbacks
  #--------------------------------------------------------------------------------------------
  def onTimer(self, tid, userArg):
    """
    KBEngine method.
    引擎回调timer触发
    """
    if SCDefine.TIMER_TYPE_NEXT_TURN == userArg:
      iNextSeatIdx = (self.lastDiscardSeat + 1) % self.playerCount
      mjPlayer = self.getMJPlayerBySeatIdx(iNextSeatIdx)
      DEBUG_MSG("GameDdz::onTimer: iNextSeatIdx=%i" % iNextSeatIdx)
      self.reqNewTile(mjPlayer.entityCall)
      self.reqOutputMjTile(mjPlayer.entityCall, mjPlayer.tileStacks[0])
    elif SCDefine.TIMER_TYPE_BANKER_TURN == userArg:
      mjPlayer = self.getMJPlayerBySeatIdx(self.bankerIdx)
      DEBUG_MSG("GameMJ::onTimer: bankerIdx=%i" % self.bankerIdx)
      self.reqOutputMjTile(mjPlayer.entityCall, mjPlayer.tileStacks[0])

    GameObject.onTimer(self, tid, userArg)

  def onDestroy(self):
    """
    KBEngine method.
    """
    del KBEngine.globalData["space_%i" % self.spaceID]
    self.destroySpace()

  def onEnter(self, entityCall, iSeatIdx):
    """
    defined method.
    进入场景
    """
    DEBUG_MSG('GameMJ::onEnter space[%d] entityID = %i iSeatIdx=%i.' % (self.id, entityCall.id, iSeatIdx))
    # 重复登录
    if entityCall.id in self.mjPlayers:
      return
    mjPlayer = self.getMJPlayerBySeatIdx(iSeatIdx)
    # 第一次登录
    if mjPlayer == None:
      avatar = KBEngine.entities.get(entityCall.id)
      if avatar:
        mjPlayer = MJPlayer(entityCall, iSeatIdx, avatar.name)
        self.mjPlayers[entityCall.id] = mjPlayer
      else:
        ERROR_MSG("GameMJ::onEnter: %i entityCall.id=%i not found" % (self.id, entityCall.id))
    # 踢出离线玩家
    else:
      oldPlayer = self.getMJPlayerBySeatIdx(iSeatIdx)
      if not oldPlayer.isOffline:
        ERROR_MSG("GameMJ::onEnter: %i seatIdx=%i oldPlayer=%s not offline" % (self.id, iSeatIdx, oldPlayer.isOffline))
        # return
      self.mjPlayers[entityCall.id] = oldPlayer
      del self.mjPlayers[oldPlayer.entityCall.id]
      oldPlayer.changeEntityCall(entityCall)
      oldPlayer.setOffline(False)
      for id, p in self.mjPlayers.items():
        if p.client and id != entityCall.id:
          p.client.onOffline(iSeatIdx, 0)
    if self.gameState == GameState.STARTED:
      leftNum = len(self.leftTiles)
      self.resetMJGamePlayers(iSeatIdx)
      for id, p in self.mjPlayers.items():
        if p.client and p.seatIdx == iSeatIdx:
          DEBUG_MSG("GameMJ::onEnter: self.ghostTile=%s, seatIdx=%i, leftNum=%i self.lastOutputTile=%s self.bankerIdx=%i self.curTurn=%i" %
                    (self.ghostTile, p.seatIdx, leftNum, self.lastOutputTile, self.bankerIdx, self.curTurn))
          for idx in self.gamePlayers:
            DEBUG_MSG("GameMJ::onEnter: idx=%s" % (idx))
          t = {"roomId": self.roomID, "gameName": "GameMJ", "curRound": self.curRound, "maxRound": self.maxRound, "playerCount": self.playerCount,
                    "ghostTile": self.ghostTile, "leftNum": leftNum, "lastOutputTile": self.lastOutputTile, "lastDiscardSeat": self.lastDiscardSeat,
                    "bankerIdx": self.bankerIdx, "curTurn": self.curTurn, "bOutputTile": self.bOutputTile}
          p.client.onReConnectRoom(t, self.gamePlayers)
          break

  def reqOffline(self, entityCall):
    ''' 请求离线 '''
    if entityCall.id in self.mjPlayers:
      mjPlayer = self.mjPlayers[entityCall.id]
      mjPlayer.setOffline(True)
      for id, p in self.mjPlayers.items():
        if p.client and id != entityCall.id:
          p.client.onOffline(mjPlayer.seatIdx, 1)
    else:
      ERROR_MSG("GameMJ::reqOffline: %i entityCall.id=%i not found" % (self.id, entityCall.id))

  # 玩家请求登出房间
  def onLeave(self, entityID):
    """
    defined method.
    离开场景
    """
    DEBUG_MSG('GameMJ::onLeave space[%d] entityID = %i.' % (self.id, entityID))
    if entityID in self.mjPlayers:
      del self.mjPlayers[entityID]
    else:
      ERROR_MSG("GameMJ::onLeave: %i entityID=%i not found" % (self.id, entityID))

  def resetMJGamePlayers(self, iSeatIdx):
    ''' 获取游戏玩家 '''
    for id, p in self.mjPlayers.items():
      player = TMJGamePlayer()
      seatIdx = p.seatIdx
      handTiles = iSeatIdx == seatIdx and p.tileStacks or []
      player.extend([p.huaScore, p.dictMelds, handTiles, p.outputTileStacks, len(p.tileStacks),
                     seatIdx, p.playerName, p.isOffline, p.winScore])
      self.gamePlayers[seatIdx] = player

  def getNewTile(self, mjPlayer):
    ''' 获取新牌 '''
    if len(self.leftTiles) > 0:
      newTile = self.leftTiles.pop()
      # 花判断
      if newTile > 29:
        mjPlayer.addHuaScore()
        return self.getNewTile(mjPlayer)
      else:
        return newTile
    else:
      # 没牌怎么处理？
      return 0

  def getMJPlayerBySeatIdx(self, seatIdx):
    ''' 获取玩家 '''
    for id, p in self.mjPlayers.items():
      if p.seatIdx == seatIdx:
        return p
    return None

  def getAllHuaScores(self):
    ''' 获取所有花分 '''
    lHuaScores = [0, 0, 0, 0]
    for id, p in self.mjPlayers.items():
      lHuaScores[p.seatIdx] = p.huaScore
    return lHuaScores

  def onGameStart(self, curRound, maxRound, roomId, playerCount):
    ''' 游戏开始 '''
    DEBUG_MSG("GameMJ::onGameStart: %i curRound=%i maxRound=%i roomId=%i playerCount=%i" %
              (self.id, curRound, maxRound, roomId, playerCount))
    self.curRound = curRound
    self.maxRound = maxRound
    self.roomID = roomId
    self.bOutputTile = 0
    self.playerCount = playerCount
    self.gameState = GameState.STARTED
    self.leftTiles = mj_util.fapai()
    DEBUG_MSG("GameMJ::onGameStart: %i leftTiles=%s" % (self.id, len(self.leftTiles)))
    for id, p in self.mjPlayers.items():
      p.resetData()
      tileStacks = []
      for j in range(16):
        tileStacks.append(self.getNewTile(p))
      DEBUG_MSG("GameMJ::onGameStart: i=%i, lTileStacks=%s" % (id, tileStacks))
      p.initTileStacks(tileStacks)
    # 随机地主
    diceNumber = 0
    if curRound == 1:
      diceNumber1 = random.randint(1, 6)
      diceNumber2 = random.randint(1, 6)
      diceNumber = 10 * diceNumber1 + diceNumber2
      sumDice = diceNumber1 + diceNumber2
      if self.playerCount == 2:
        self.bankerIdx = sumDice % 2 == 0 and 1 or 0
      elif self.playerCount == 3: # 0-2 1-0 2-1
        self.bankerIdx = sumDice % 3 == 0 and 2 or sumDice % 3 == 1 and 1 or 0
      elif self.playerCount == 4: # 0-3 1-0 2-1 3-2
        self.bankerIdx = sumDice % 4 == 0 and 3 or sumDice % 4 == 2 and 1 or sumDice % 4 == 3 and 2 or 0
    self.curTurn = self.bankerIdx
    # 庄多一张牌
    mjPlayer = self.getMJPlayerBySeatIdx(self.bankerIdx)
    mjPlayer.addHandTile(self.getNewTile(mjPlayer))
    # 金
    self.ghostTile = self.getNewTile(mjPlayer)
    for id, p in self.mjPlayers.items():
      if p.client:
        lHuaScores = self.getAllHuaScores()
        DEBUG_MSG ("GameMJ::onMjGameStart: id=%i seatIdx=%i, tiles=%s lHuaScores=%s bankerIdx=%i" % (id, p.seatIdx, p.tileStacks, lHuaScores, self.bankerIdx))
        p.client.onMjGameStart(self.bankerIdx, diceNumber, p.tileStacks, lHuaScores, self.ghostTile, self.curRound)
    self.onCheckRobotBanker()

  def reqOutputMjTile(self, entityCall, strTile):
    ''' 请求出牌 '''
    if not self.isGameRunning():
      return
    mjPlayer = self.mjPlayers[entityCall.id]
    iSeatIdx = mjPlayer.seatIdx
    DEBUG_MSG("GameMJ::reqOutputMjTile: %i iSeatIdx=%i strTile=%s" % (self.id, iSeatIdx, strTile))
    if strTile in mjPlayer.tileStacks:
      mjPlayer.removeHandTile(strTile)
    else:
      ERROR_MSG("GameMJ::reqOutputMjTile: %i strTile=%s not in lTileStacks" % (self.id, strTile))
      return
    self.lastDiscardSeat = iSeatIdx
    self.lastOutputTile = strTile
    self.bOutputTile = 1
    mjPlayer.addOutputTileStacks(strTile)
    iLeftNum = len(mjPlayer.tileStacks)
    for id, p in self.mjPlayers.items():
      if id != entityCall.id and p.client:
        DEBUG_MSG("GameMJ::onReqOutputMjTile: id=%i, seatIdx=%i iLeftNum=%i" % (id, p.seatIdx, iLeftNum))
        p.client.onReqOutputMjTile(iSeatIdx, strTile, iLeftNum)
    self.onCheckRobotTurn(iSeatIdx)

  def isGameRunning(self):
    ''' 游戏状态检查 '''
    # DEBUG_MSG("GameMJ::onGameStateCheck: %i gameState=%s" % (self.id, self.gameState.name))
    if self.gameState == GameState.STARTED:
      return True
    else:
      return False

  def reqNewTile(self, entityCall):
    ''' 请求摸牌 '''
    if not self.isGameRunning():
      return
    mjPlayer = self.mjPlayers[entityCall.id]
    iSeatIdx = mjPlayer.seatIdx
    self.curTurn = iSeatIdx
    self.bOutputTile = 0
    DEBUG_MSG("GameMJ::reqNewTile: %i iSeatIdx=%i" % (self.id, iSeatIdx))
    newTile = self.getNewTile(mjPlayer)
    mjPlayer.addHandTile(newTile)
    leftNum = len(self.leftTiles)
    huaScore = mjPlayer.huaScore
    for id, p in self.mjPlayers.items():
      if p.client:
        DEBUG_MSG("GameMJ::reqNewTile: id=%i, seatIdx=%i, name=%s, newTile=%s, leftNum=%i, lHuaScores=%s" % (id, p.seatIdx, p.playerName, newTile, leftNum, huaScore))
        clientTile = iSeatIdx == p.seatIdx and newTile or 0
        p.client.onReqNewTile(clientTile, leftNum, huaScore, iSeatIdx)

  def resetMJGameResultPlayers(self, strMeldType, score, entityID):
    ''' 获取游戏结果玩家 '''
    for id, p in self.mjPlayers.items():
      player = TMJGameResultPlayer()
      seatIdx = p.seatIdx
      isDianPao = strMeldType == "hu" and seatIdx == self.lastDiscardSeat and 1 or 0
      winScore = id == entityID and score or -score
      player.extend([seatIdx, p.angangTiles, p.tileStacks, isDianPao, winScore])
      self.gameResultPlayers[seatIdx] = player

  def getScorePlayers(self):
    t = []
    for id, p in self.mjPlayers.items():
      t.append({"seatIdx": p.seatIdx, "score": p.winScore})
    return t

  def getWinPlayers(self):
    t = []
    for id, p in self.mjPlayers.items():
      winList = []
      for k, v in p.winDict.items():
        winList.append({"strWinType": k, "winCount": v})
      isOwner = p.seatIdx == 0 and 1 or 0
      t.append({"playerName": p.playerName, "isOwner": isOwner, "winScore": p.winScore, "winList": winList})
      DEBUG_MSG("GameMJ::getWinPlayers: seatIdx=%i, playerName=%s, winScore=%i, winList=%s" % (p.seatIdx, p.playerName, p.winScore, winList))
    return t

  def reqMeldEvent(self, entityCall, strMeldType, meldTile):
    ''' 请求碰杠 '''
    if not self.isGameRunning():
      return
    mjPlayer = self.mjPlayers[entityCall.id]
    iSeatIdx = mjPlayer.seatIdx
    self.bOutputTile = 0
    if strMeldType != "hu" and strMeldType != "zimo":
      strTiles = strMeldType == "Chi" and [meldTile, self.lastOutputTile] or [meldTile]
      # 如果补杠，要替换掉原先的碰
      if strMeldType == "BuGang":
        for i in range(len(mjPlayer.dictMelds)):
          if mjPlayer.dictMelds[i]["strMeldType"] == "Peng" and mjPlayer.dictMelds[i]["tiles"][0] == meldTile:
            mjPlayer.dictMelds[i]["strMeldType"] = "BuGang"
            break
      else:
        mjPlayer.addDictMelds({"strMeldType": strMeldType, "tiles": strTiles})
    self.curTurn = iSeatIdx
    DEBUG_MSG("GameMJ::reqMeldEvent: %i iSeatIdx=%i strMeldType=%s meldTile=%s" % (entityCall.id, iSeatIdx, strMeldType, meldTile))
    if strMeldType == "hu" or strMeldType == "zimo":
      curWinScore = mjPlayer.addWinDict(strMeldType, self.ghostTile)
      for id, p in self.mjPlayers.items():
        if id != entityCall.id:
          p.addWinScore(-curWinScore)
      self.gameState = GameState.ENDED
      self.resetMJGameResultPlayers(strMeldType, curWinScore, entityCall.id)
      for id, p in self.mjPlayers.items():
        if p.client:
          p.client.onMJGameResult(iSeatIdx, strMeldType, self.gameResultPlayers)
      # 游戏结束，房间解散
      if self.curRound == self.maxRound:
        self.getSpaces().disbandRoom(self.roomID, self.getWinPlayers())
      else:
        self.getSpaces().onNextRound(self.roomID, self.getScorePlayers())
      self.bankerIdx = iSeatIdx
      return
    elif strMeldType != "AnGang":
      for id, p in self.mjPlayers.items():
        if id != entityCall.id and p.client:
          p.client.onReqMeldEvent(strMeldType, meldTile, iSeatIdx)
    else:
      mjPlayer.addAngangTile(meldTile)
      for id, p in self.mjPlayers.items():
        if id != entityCall.id and p.client:
          p.client.onReqMeldEvent(strMeldType, "bai", iSeatIdx)
    if strMeldType == "Chi":
      self.onChiEvent(mjPlayer, meldTile)
    elif strMeldType == "Peng":
      self.onPengEvent(mjPlayer, meldTile)
    elif strMeldType == "MingGang":
      self.onGangEvent(mjPlayer, meldTile)
    elif strMeldType == "AnGang":
      self.onAnGangEvent(mjPlayer, meldTile)
    elif strMeldType == "BuGang":
      self.onBuGangEvent(mjPlayer, meldTile)
    if strMeldType == "Chi" or strMeldType == "Peng" or strMeldType == "MingGang":
      self.lastOutputTile = 0
      lastMjPlayer = self.getMJPlayerBySeatIdx(self.lastDiscardSeat)
      lastMjPlayer.removeLastOutputTile()

  def onChiEvent(self, mjPlayer, beginTile):
    ''' 吃 '''
    DEBUG_MSG("GameMJ::onChiEvent: %i iSeatIdx=%i self.lastOutputTile=%s beginTile=%s" % (self.id, mjPlayer.seatIdx, self.lastOutputTile, beginTile))
    for i in range(3):
      newTile = beginTile + i
      if newTile != self.lastOutputTile:
        if newTile in mjPlayer.tileStacks:
          mjPlayer.removeHandTile(newTile)
        else:
          ERROR_MSG("GameMJ::onChiEvent: %i strTile=%s not in lTileStacks" % (self.id, newTile))

  def onPengEvent(self, mjPlayer, meldTile):
    ''' 碰 '''
    DEBUG_MSG("GameMJ::onPengEvent: %i iSeatIdx=%i meldTile=%s" % (self.id, mjPlayer.seatIdx, meldTile))
    for i in range(2):
      mjPlayer.removeHandTile(meldTile)

  def onGangEvent(self, mjPlayer, meldTile):
    ''' 杠 '''
    DEBUG_MSG("GameMJ::onGangEvent: %i iSeatIdx=%i meldTile=%s" % (self.id, mjPlayer.seatIdx, meldTile))
    for i in range(3):
      mjPlayer.removeHandTile(meldTile)

  def onAnGangEvent(self, mjPlayer, meldTile):
    ''' 暗杠 '''
    DEBUG_MSG("GameMJ::onAnGangEvent: %i iSeatIdx=%i meldTile=%s" % (self.id, mjPlayer.seatIdx, meldTile))
    for i in range(4):
      mjPlayer.removeHandTile(meldTile)

  def onBuGangEvent(self, mjPlayer, meldTile):
    ''' 补杠 '''
    DEBUG_MSG("GameMJ::onBuGangEvent: %i iSeatIdx=%i meldTile=%s" % (self.id, mjPlayer.seatIdx, meldTile))
    mjPlayer.removeHandTile(meldTile)

  def onCheckRobotBanker(self):
    return
    if not self.isGameRunning():
      return
    mjPlayer = self.getMJPlayerBySeatIdx(self.bankerIdx)
    cellAvatar = KBEngine.entities.get(mjPlayer.entityCall.id)
    DEBUG_MSG("GameMJ::onCheckRobotBanker: bankerIdx=%i, avatar.id=%i cellAvatar.isRobot=%i" % (self.bankerIdx, mjPlayer.entityCall.id, cellAvatar.isRobot))
    # 前端要做动画，所以延迟
    if cellAvatar.isRobot:
      self.addTimer(10, 0, SCDefine.TIMER_TYPE_BANKER_TURN)

  def onCheckRobotTurn(self, iSeatIdx):
    ''' 检查机器人出牌 '''
    return
    if not self.isGameRunning():
      return
    iNextSeatIdx = (iSeatIdx + 1) % self.playerCount
    mjPlayer = self.getMJPlayerBySeatIdx(iNextSeatIdx)
    # avatar = self.mjPlayers[iNextSeatIdx]
    cellAvatar = KBEngine.entities.get(mjPlayer.entityCall.id)
    DEBUG_MSG("GameMJ::onCheckRobotTurn: iNextSeatIdx=%i, avatar.id=%i cellAvatar.isRobot=%i" % (iNextSeatIdx, mjPlayer.entityCall.id, cellAvatar.isRobot))
    if cellAvatar.isRobot:
      self.addTimer(2, 0, SCDefine.TIMER_TYPE_NEXT_TURN)
