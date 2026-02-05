# -*- coding: utf-8 -*-
import KBEngine
import time
from KBEDebug import *
import importlib
import Async
importlib.reload(Async)
import kbe
importlib.reload(kbe)
import Promise
importlib.reload(Promise)
import cfg_room
importlib.reload(cfg_room)

from AVATAR_INFOS import TAvatarInfos


class Account(KBEngine.Proxy, kbe.Base):
    def __init__(self):
        KBEngine.Proxy.__init__(self)
        self.activeAvatar = None
        self.relogin = time.time()

    def reqAvatarList(self, strAccount):
        """
        exposed.
        客户端请求查询角色列表
        """
        DEBUG_MSG("Account[%i].reqAvatarList: size=%i." % (self.id, len(self.characters)))
        if len(self.characters) == 0:
          self.reqCreateAvatar(1, strAccount)
        else:
          self.client.onReqAvatarList(self.characters)

    def reqCreateAvatar(self, roleType, name):
        """
        exposed.
        客户端请求创建一个角色
        """

        props = {
          "name"				: name,
          "roleType"			: roleType,
          "gold"				: 100,
          "seatIdx"     : 0,
          "isReady"     : 0,
          "winScore"    : 0,
          "isRobot"     : 0
        }

        avatar = KBEngine.createEntityLocally('Avatar', props)
        if avatar:
          avatar.writeToDB(self._onAvatarSaved)

        DEBUG_MSG("Account[%i].reqCreateAvatar:%s.\n" % (self.id, name))

    def onEntitiesEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        INFO_MSG("Account[%i]::onClientEnabled:entities enable. entityCall:%s, clientType(%i), clientDatas=(%s), hasAvatar=%s, accountName=%s" % \
			(self.id, self.client, self.getClientType(), self.getClientDatas(), self.activeAvatar, self.__ACCOUNT_NAME__))

    def onLogOnAttempt(self, ip, port, password):
        """
        KBEngine method.
        客户端登陆失败时会回调到这里
        """
        INFO_MSG("Account[%i]::onLogOnAttempt: ip=%s, port=%i, selfclient=%s" % (self.id, ip, port, self.client))

        if self.activeAvatar:
          if self.activeAvatar.client is not None:
            self.activeAvatar.giveClientTo(self)

          self.relogin = time.time()
          self.activeAvatar.destroySelf()
          self.activeAvatar = None

        return KBEngine.LOG_ON_ACCEPT

    def onClientDeath(self):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        if self.activeAvatar:
          self.activeAvatar.accountEntity = None
          self.activeAvatar = None

        DEBUG_MSG("Account[%i].onClientDeath:" % self.id)
        self.destroy()

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Account::onDestroy: %i." % self.id)

        if self.activeAvatar:
          self.activeAvatar.accountEntity = None

          try:
            self.activeAvatar.destroySelf()
          except:
            pass

          self.activeAvatar = None

    def selectAvatarGame(self, dbid):
        """
        exposed.
        客户端选择某个角色进行游戏
        """
        DEBUG_MSG("Account[%i].selectAvatarGame:%i. self.activeAvatar=%s" % (self.id, dbid, self.activeAvatar))
        # 注意:使用giveClientTo的entity必须是当前baseapp上的entity
        if self.activeAvatar is None:
          if dbid in self.characters:
            self.lastSelCharacter = dbid
            # 由于需要从数据库加载角色，因此是一个异步过程，加载成功或者失败会调用__onAvatarCreated接口
            # 当角色创建好之后，account会调用giveClientTo将客户端控制权（可理解为网络连接与某个实体的绑定）切换到Avatar身上，
            # 之后客户端各种输入输出都通过服务器上这个Avatar来代理，任何proxy实体获得控制权都会调用onClientEnabled
            # Avatar继承了Teleport，Teleport.onClientEnabled会将玩家创建在具体的场景中
            # self.nameB = self.cellData["name"] KeyError: 'name'
            KBEngine.createEntityFromDBID("Avatar", dbid, self.__onAvatarCreated)
          else:
            ERROR_MSG("Account[%i]::selectAvatarGame: not found dbid(%i)" % (self.id, dbid))
        else:
          self.giveClientTo(self.activeAvatar)

    def __onAvatarCreated(self, baseRef, dbid, wasActive):
        """
        选择角色进入游戏时被调用
        """
        if wasActive:
          ERROR_MSG("Account::__onAvatarCreated:(%i): this character is in world now!" % (self.id))
          return
        if baseRef is None:
          ERROR_MSG("Account::__onAvatarCreated:(%i): the character you wanted to created is not exist!" % (self.id))
          return

        avatar = KBEngine.entities.get(baseRef.id)
        if avatar is None:
          ERROR_MSG("Account::__onAvatarCreated:(%i): when character was created, it died as well!" % (self.id))
          return

        if self.isDestroyed:
          ERROR_MSG("Account::__onAvatarCreated:(%i): i dead, will the destroy of Avatar!" % (self.id))
          avatar.destroy()
          return

        info = self.characters[dbid]
        avatar.accountEntity = self
        self.activeAvatar = avatar
        self.giveClientTo(avatar)

    def _onAvatarSaved(self, success, avatar):
        """
        新建角色写入数据库回调
        """
        INFO_MSG('Account::_onAvatarSaved:(%i) create avatar state: %i, %s, %i' % (self.id, success, avatar.cellData["name"], avatar.databaseID))

        # 如果此时账号已经销毁， 角色已经无法被记录则我们清除这个角色
        if self.isDestroyed:
          if avatar:
            avatar.destroy(True)

          return

        avatarinfo = TAvatarInfos()
        avatarinfo.extend([0, "", 0, 0, 0, 0, 0, 0])

        if success:
          info = TAvatarInfos()
          info.extend([avatar.databaseID, avatar.cellData["name"], avatar.roleType, 100, 0, 0, 0, 0])
          self.characters[avatar.databaseID] = info
          avatarinfo[0] = avatar.databaseID
          avatarinfo[1] = avatar.cellData["name"]
          avatarinfo[2] = avatar.roleType
          avatarinfo[3] = 100
          avatarinfo[4] = 0
          avatarinfo[5] = 0
          avatarinfo[6] = 0
          avatarinfo[7] = 0
          self.writeToDB()
        else:
          avatarinfo[1] = "创建失败了"

        avatar.destroy()

        if self.client:
          self.client.onCreateAvatarResult(0, avatarinfo)
