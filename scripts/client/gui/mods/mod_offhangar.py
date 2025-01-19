import os
import signal

import Account
import BigWorld
import account_shared

from ConnectionManager import connectionManager
from GameSessionController import _GameSessionController
from account_helpers.Shop import Shop
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.Login import Login
from gui.Scaleform.gui_items.Vehicle import Vehicle
from helpers.time_utils import _TimeCorrector, _g_instance
from nations import INDICES
from predefined_hosts import g_preDefinedHosts

from gui.mods.offhangar.logging import *
from gui.mods.offhangar.utils import *
from gui.mods.offhangar._constants import *
from gui.mods.offhangar.server import *
from gui.mods.offhangar.requests import *

Account.LOG_DEBUG = LOG_DEBUG
Account.LOG_NOTE = LOG_NOTE

g_preDefinedHosts._hosts.append(g_preDefinedHosts._makeHostItem(OFFLINE_SERVER_ADDRESS, OFFLINE_SERVER_ADDRESS, OFFLINE_SERVER_ADDRESS))

# Force killing game process
def fini():
	os.kill(os.getpid(), signal.SIGTERM)

@override(Shop, '__onSyncComplete')
def Shop__onSyncComplete(baseFunc, baseSelf, syncID, data):
	data = {
		'berthsPrices': (16, 16, [300]),
		'freeXPConversion': (25, 1),
		'dropSkillsCost': {
			0: {'xpReuseFraction': 0.5, 'gold': 0, 'credits': 0},
			1: {'xpReuseFraction': 0.75, 'gold': 0, 'credits': 20000},
			2: {'xpReuseFraction': 1.0, 'gold': 200, 'credits': 0}
		},
		'refSystem': {
			'maxNumberOfReferrals': 50,
			'posByXPinTeam': 10,
			'maxReferralXPPool': 350000,
			'periods': [(24, 3.0), (168, 2.0), (876000, 1.5)]
		},
		'playerEmblemCost': {
			0: (15, True),
			30: (6000, False),
			7: (1500, False)
		},
		'premiumCost': {
			1: 250,
			3: 650,
			7: 1250,
			30: 2500,
			180: 13500,
			360: 24000
		},
		'winXPFactorMode': 0,
		'sellPriceModif': 0.5,
		'passportChangeCost': 50,
		'exchangeRateForShellsAndEqs': 400,
		'exchangeRate': 400,
		'tankmanCost': ({
			'isPremium': False,
			'baseRoleLoss': 0.20000000298023224,
			'gold': 0,
			'credits': 0,
			'classChangeRoleLoss': 0.20000000298023224,
			'roleLevel': 50
		},
		{
			'isPremium': False,
			'baseRoleLoss': 0.10000000149011612,
			'gold': 0,
			'credits': 20000,
			'classChangeRoleLoss': 0.10000000149011612,
			'roleLevel': 75
		},
		{
			'isPremium': True,
			'baseRoleLoss': 0.0,
			'gold': 200,
			'credits': 0,
			'classChangeRoleLoss': 0.0,
			'roleLevel': 100
		}),
		'paidRemovalCost': 10,
		'dailyXPFactor': 2,
		'changeRoleCost': 500,
		'items': getOfflineShopItems(),
		'customization': dict((nation, {'camouflages': {}}) for nation in INDICES.values()),
		'isEnabledBuyingGoldShellsForCredits': True,
		'slotsPrices': (9, [300]),
		'freeXPToTManXPRate': 10,
		'sellPriceFactor': 0.5,
		'isEnabledBuyingGoldEqsForCredits': True,
		'playerInscriptionCost': {
			0: (15, True),
			7: (1500, False),
			30: (6000, False),
			'nations': {}
		}
	}

	baseFunc(baseSelf, syncID, data)

@override(_TimeCorrector, 'serverRegionalTime')
def TimeCorrector_serverRegionalTime(baseFunc, baseSelf):
	regionalSecondsOffset = 0
	try:
		serverRegionalSettings = OFFLINE_SERVER_SETTINGS['regional_settings']
		regionalSecondsOffset = serverRegionalSettings['starting_time_of_a_new_day']
	except Exception:
		LOG_CURRENT_EXCEPTION()
	return _g_instance.serverUTCTime + regionalSecondsOffset

@override(_GameSessionController, 'isSessionStartedThisDay')
def GameSessionController_isSessionStartedThisDay(baseFunc, baseSelf):
	serverRegionalSettings = OFFLINE_SERVER_SETTINGS['regional_settings']
	return int(_g_instance.serverRegionalTime) / 86400 == int(baseSelf._GameSessionController__sessionStartedAt + serverRegionalSettings['starting_time_of_a_new_day']) / 86400

@override(_GameSessionController, '_getWeeklyPlayHours')
def GameSessionController_getWeeklyPlayHours(baseFunc, baseSelf):
	serverRegionalSettings = OFFLINE_SERVER_SETTINGS['regional_settings']
	weekDaysCount = account_shared.currentWeekPlayDaysCount(_g_instance.serverUTCTime, serverRegionalSettings['starting_time_of_a_new_day'], serverRegionalSettings['starting_day_of_a_new_weak'])
	return baseSelf._getDailyPlayHours() + sum(baseSelf._GameSessionController__stats.dailyPlayHours[1:weekDaysCount])

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
		baseSelf.fakeServer = FakeServer()
		baseSelf.name = OFFLINE_NICKNAME
		baseSelf.serverSettings = OFFLINE_SERVER_SETTINGS

	baseFunc(baseSelf)

	if baseSelf.isOffline:
		BigWorld.player(baseSelf)

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