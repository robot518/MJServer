# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *


# 服务端timer定义
TIMER_TYPE_BUFF_TICK								= 1 # buff的tick
TIMER_TYPE_SPACE_SPAWN_TICK							= 2 # space出生怪
TIMER_TYPE_CREATE_SPACES							= 3 # 创建space
TIMER_TYPE_DESTROY									= 4 # 延时销毁entity
TIMER_TYPE_HEARDBEAT								= 5	# 心跳
TIMER_TYPE_FIGTH_WATI_INPUT_TIMEOUT					= 6	# 战斗回合等待用户输入超时
TIMER_TYPE_SPAWN									= 7	# 出生点出生timer
TIMER_TYPE_DESTROY									= 8	# entity销毁
TIMER_TYPE_SET_DDZ_ROBOT                          = 9 # 设置斗地主机器人
TIMER_TYPE_NEXT_TURN                           = 10 # 下一个玩家出牌
TIMER_TYPE_BANKER_TURN                         = 11 # 庄家出牌
