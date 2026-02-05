#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import poker_util
import mj_tileStack_util
importlib.reload(poker_util)
import random
import functools

# class MJTileStack(poker_util.Poker):
#     def enableType(self):
#         ''' 是否符合牌型 '''
#         for w, y, tnum, ty in ABLES:
#             for rectCards, pk in self.iterFlipRect(w, y):
#                 # print(rectCards, pk)
#                 if MJTileStack(pk).isComprise(ty, tnum):
#                     return w, y, tnum, ty, next(iter(rectCards)).x

#     def ableDiscards(self, w, y, tnum=0, ty=0, xmin=0):
#         ''' 所有合法的出牌 '''
#         for rectCards, pk in self.iterFlipRect(w, y, xmin+1):
#             pk = MJTileStack(pk)
#             if tnum == 0 or ty == 0:
#                 yield rectCards
#             else:
#                 for cards in pk.iterTails(tnum, ty):
#                     yield rectCards + cards
#         bomb = 0
#         if w == 1 and y == 4 and not tnum and not ty:
#             bomb = xmin
#         for rectCards, pk in self.iterFlipRect(1, 4, bomb+1):
#             yield rectCards

#     def ableDiscard(self, discardType):
#         ''' 对于目标牌型是否合法 '''
#         able = self.enableType()
#         if not able or not discardType:
#             return able
#         w, y, tnum, ty, xmin = discardType
#         w_, y_, tnum_, ty_, xmin_ = able
#         isBomb = self.isBomb()
#         if isBomb:
#             if tnum == 0 and w == 1 and y == 4 and isBomb <= xmin:
#                 return
#             else:
#                 return able
#         if w_ == w and y == y_ and tnum_ == tnum and ty_ == ty and xmin_ > xmin:
#             return able

#     def isBomb(self):
#         ''' 是否炸弹 '''
#         if not len(self):
#             return
#         c = self[0]
#         if len(self) == 2 and poker_util.isKing(c) and poker_util.isKing(self[1]):
#             return c.x
#         if len(self) == 4 and sum(1 for a in self if a.x == c.x) == 4:
#             return c.x


def fapai():
    ''' 发牌 '''
    allTiles = mj_tileStack_util.getAllTiles()
    random.shuffle(allTiles)

    return allTiles
    # bankerPoker, poker = poker[:3], poker[3:]
    # count = int(len(poker)/3)
    # count = 16
    # for i in range(2):
    #     yield allTiles[i*count:(i+1)*count]
    # anotherTile = allTiles.pop()
    # yield anotherTile
    # otherTiles = allTiles[2*count+1:]
    # yield otherTiles
    # for i in range(3):
    #     yield poker[i*count:(i+1)*count]
    # yield bankerPoker


# def allDiscards(myPoker):
#     ''' 所有出牌 '''
#     myPoker = DDZPoker(myPoker)
#     for w, y, tnum, ty in reversed(ABLES):
#         for v in myPoker.ableDiscards(w, y, tnum, ty):
#             yield v


# def allDiscardsWithPoker(myPoker, poker):
#     ''' 合法出牌 '''
#     myPoker = DDZPoker(myPoker)
#     poker = DDZPoker(poker)
#     args = poker.enableType()
#     assert args
#     return myPoker.ableDiscards(*args)
