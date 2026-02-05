import json
import time
import weakref
import KBEngine
from KBEDebug import *
from MJ_FINAL_RESULT_INFO import TMJFinalResultInfo

class MJResultMgr:
  def __init__(self, entity):
    self._entity = weakref.proxy(entity)
    DEBUG_MSG("MJResultMgr __init__")

  def add_resultInfo(self, roomId, playerCount, totalRound, finalPlayerData):
    endTime = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    DEBUG_MSG("MJResultMgr add_resultInfo endTime=%s,roomId=%d,playerCount=%d,totalRound=%d" % (endTime,roomId,playerCount,totalRound))
    # 先存本地
    info = TMJFinalResultInfo()
    info.extend([roomId, playerCount, totalRound, endTime, finalPlayerData])
    self._entity.mjResultList[roomId] = info
    for playerData in finalPlayerData:
      DEBUG_MSG("MJResultMgr add_resultInfo playerData=%s" % (playerData))
    # roomId 转成字符串
    roomId = str(roomId)
    def sqlcallback(result, rows, insertid, error):
      DEBUG_MSG("MJResultMgr add_message sqlcallback result=%s,rows=%s, insertid=%s, error=%s" % (result,rows,insertid,error))
    KBEngine.executeRawDatabaseCommand("""INSERT INTO tbl_Spaces_mjResultList_values (parentID, sm_roomId, sm_playerCount, sm_totalRound, sm_endTime)
                                       VALUES(1, '%s',%d,%d,'%s');"""
                      % (roomId, playerCount, totalRound, endTime) , sqlcallback)

  def get_resultInfo(self, avatarEntity, roomId):
    DEBUG_MSG("MJResultMgr get_resultInfo roomId=%d" % (roomId))
    # roomId = str(roomId)
    # 从本地直接获取
    if roomId in self._entity.mjResultList:
      if avatarEntity.client:
        info = self._entity.mjResultList[roomId]
        DEBUG_MSG("MJResultMgr get_resultInfo info=%s" % (info))
        avatarEntity.client.onReqMJFinalResult(info)
    # def sqlcallback(result, rows, insertid, error):
    #   if result:
    #     self._entity.mjResultList.clear()
    #     for data in result:
    #       info = TMJFinalResultInfo()
    #       sm_finalPlayerData_json = data[4].decode()
    #       DEBUG_MSG("MJResultMgr get_resultInfo sm_finalPlayerData_json=%s" % (sm_finalPlayerData_json))
    #       # 解析 JSON 数据
    #       sm_finalPlayerData = json.loads(sm_finalPlayerData_json)
    #       DEBUG_MSG("MJResultMgr get_resultInfo sm_finalPlayerData=%s" % (sm_finalPlayerData))
    #       info.extend([data[0].decode(), int(data[1].decode()), int(data[2].decode()), data[3].decode(), data[4].decode(), sm_finalPlayerData])
    #       DEBUG_MSG("MJResultMgr __init__ info=%s" % (info))
    #       self._entity.mjResultList[0] = info
    #     if avatarEntity.client:
    #       avatarEntity.client.onReqMJFinalResult(self._entity.mjResultList[0])
    # KBEngine.executeRawDatabaseCommand("""
    #     SELECT sm_roomId, sm_playerCount, sm_totalRound, sm_endTime, sm_finalPlayerData
    #     FROM tbl_Spaces_mjResultList_values WHERE sm_roomId = %s;
    # """ % (roomId), sqlcallback)
