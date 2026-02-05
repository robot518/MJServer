# -*- coding: utf-8 -*-
from KBEDebug import *

class TMJGameResultPlayer(list):
	"""
	"""
	def __init__(self):
		"""
		"""
		list.__init__(self)

	def asDict(self):
		data = {
			"seatIdx"			: self[0],
			"angangTiles"			: self[1],
			"handTileStack"		: self[2],
      "isDianPao" : self[3],
      "winScore" : self[4],
		}

		return data

	def createFromDict(self, dictData):
		self.extend([dictData["seatIdx"], dictData["angangTiles"], dictData["handTileStack"],
               dictData["isDianPao"], dictData["winScore"]])
		return self

class MJ_GAME_RESULT_PLAYER_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TMJGameResultPlayer().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TMJGameResultPlayer)

mj_game_result_player_inst = MJ_GAME_RESULT_PLAYER_PICKLER()

class TMJGameResultPlayerList(dict):
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

class MJ_GAME_RESULT_PLAYER_LIST_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TMJGameResultPlayerList().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TMJGameResultPlayerList)

