# -*- coding: utf-8 -*-
from KBEDebug import *

class TMJFinalResultInfo(list):
	"""
	"""
	def __init__(self):
		"""
		"""
		list.__init__(self)

	def asDict(self):
		data = {
			"roomId"			: self[0],
			"playerCount"			: self[1],
			"totalRound"		: self[2],
      "endTime" : self[3],
      "mjFinalPlayerData" : self[4],
		}

		return data

	def createFromDict(self, dictData):
		self.extend([dictData["roomId"], dictData["playerCount"], dictData["totalRound"],
               dictData["endTime"], dictData["mjFinalPlayerData"]])
		return self

class MJ_FINAL_RESULT_INFO_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TMJFinalResultInfo().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TMJFinalResultInfo)

mj_final_result_info_inst = MJ_FINAL_RESULT_INFO_PICKLER()

class TMJFinalResultInfoList(dict):
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

class MJ_FINAL_RESULT_INFO_LIST_PICKLER:
	def __init__(self):
		pass

	def createObjFromDict(self, dct):
		return TMJFinalResultInfoList().createFromDict(dct)

	def getDictFromObj(self, obj):
		return obj.asDict()

	def isSameType(self, obj):
		return isinstance(obj, TMJFinalResultInfoList)
