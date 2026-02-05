# -*- coding: utf-8 -*-
from KBEDebug import *

class TMJGamePlayer(list):
	"""
	"""
	def __init__(self):
		"""
		"""
		list.__init__(self)

	def asDict(self):
		data = {
			"huaScore"			: self[0],
			"dictMeld"			: self[1],
			"handTileStack"		: self[2],
      "outputTiles"  : self[3],
      "tilesCount"  : self[4],
      "seatIdx": self[5],
      "playerName": self[6],
      "isOffline": self[7],
      "winScore": self[8],
		}

		return data

	def createFromDict(self, dictData):
		self.extend([dictData["huaScore"], dictData["dictMeld"], dictData["handTileStack"],
               dictData["outputTiles"], dictData["tilesCount"], dictData["seatIdx"],
               dictData["playerName"], dictData["isOffline"], dictData["winScore"]])
		return self

class MJ_GAME_PLAYER_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TMJGamePlayer().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TMJGamePlayer)

mj_game_player_inst = MJ_GAME_PLAYER_PICKLER()

class TMJGamePlayerList(dict):
	"""
	"""
	def __init__(self):
		"""
		"""
		dict.__init__(self)

	def asDict(self):
		datas = []
		dct = {"values" : datas}

		for key, val in self.items():
			datas.append(val)

		return dct

	def createFromDict(self, dictData):
		for data in dictData["values"]:
			self[data[0]] = data
		return self

class MJ_GAME_PLAYER_LIST_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TMJGamePlayerList().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TMJGamePlayerList)
