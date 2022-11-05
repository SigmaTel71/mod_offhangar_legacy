import os
import signal

import BigWorld
import constants
import Account

from debug_utils import LOG_CURRENT_EXCEPTION

from ConnectionManager import connectionManager, CONNECTION_STATUS
from predefined_hosts import g_preDefinedHosts

from gui.mods.offhangar.logging import *
from gui.mods.offhangar.utils import *
from gui.mods.offhangar._constants import *
from gui.mods.offhangar.server import *
from gui.mods.offhangar.requests import *

Account.LOG_DEBUG = LOG_DEBUG
Account.LOG_NOTE = LOG_NOTE

from gui.Scaleform.gui_items.Vehicle import Vehicle
from gui.Scaleform.Login import Login

def fini():
	# Force killing game process
	os.kill(os.getpid(), signal.SIGTERM)

g_preDefinedHosts._hosts.append(g_preDefinedHosts._makeHostItem(OFFLINE_SERVER_ADDRESS, OFFLINE_SERVER_ADDRESS, OFFLINE_SERVER_ADDRESS))

@override(Vehicle, 'canSell')
def Vehicle_canSell(baseFunc, baseSelf):
	return BigWorld.player().isOffline or baseFunc(baseSelf)

@override(Login, 'populateUI')
def Login_populateUI(baseFunc, baseSelf, proxy):
	baseFunc(baseSelf, proxy)
 	connectionManager.connect(OFFLINE_SERVER_ADDRESS, OFFLINE_LOGIN, OFFLINE_PWD, False, False, False)

@override(Account.PlayerAccount, '__init__')
def Account_init(baseFunc, baseSelf):
	baseSelf.isOffline = not baseSelf.name
	if baseSelf.isOffline:
		constants.IS_SHOW_SERVER_STATS = False
		baseSelf.fakeServer = FakeServer()
		baseSelf.name = OFFLINE_NICKNAME
		baseSelf.serverSettings = OFFLINE_SERVER_SETTINGS

	baseFunc(baseSelf)

	if baseSelf.isOffline:
		BigWorld.player(baseSelf)
		print BigWorld.player().serverSettings

@override(Account.PlayerAccount, '__getattribute__')
def Account_getattribute(baseFunc, baseSelf, name):
	if name in ('cell', 'base', 'server') and baseSelf.isOffline:
		name = 'fakeServer'
	return baseFunc(baseSelf, name)

@override(Account.PlayerAccount, 'onBecomePlayer')
def Account_onBecomePlayer(baseFunc, baseSelf):
	baseFunc(baseSelf)
	if baseSelf.isOffline:
		baseSelf.showGUI(OFFLINE_GUI_CTX)

@override(BigWorld, 'clearEntitiesAndSpaces')
def BigWorld_clearEntitiesAndSpaces(baseFunc, *args):
	if getattr(BigWorld.player(), 'isOffline', False):
		return
	baseFunc(*args)

@override(BigWorld, 'connect')
def BigWorld_connect(baseFunc, server, loginParams, progressFn):
	if server == OFFLINE_SERVER_ADDRESS:
		LOG_DEBUG('BigWorld.connect')
		progressFn(1, "LOGGED_ON", {})
		BigWorld.createEntity('Account', BigWorld.createSpace(), 0, (0, 0, 0), (0, 0, 0), {})
	else:
		baseFunc(server, loginParams, progressFn)