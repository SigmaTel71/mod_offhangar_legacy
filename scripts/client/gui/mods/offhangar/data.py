import functools
import time
from itertools import cycle

import items
import nations
from AccountCommands import VEHICLE_SETTINGS_FLAG
from constants import ACCOUNT_ATTR
from items import vehicles, ITEM_TYPE_INDICES, _xml
from nations import AVAILABLE_NAMES, INDICES

from gui.mods.offhangar.logging import *
from gui.mods.offhangar.utils import *
from gui.mods.offhangar._constants import *

items.init(True)
vehicles.init(True)
from items.vehicles import g_list, g_cache # noqa: E402

doLog = functools.partial(doLog, 'OFFHANGAR')
LOG_NOTE = functools.partial(doLog, '[NOTE]')
LOG_DEBUG = functools.partial(doLog, '[DEBUG]')

def getOfflineShopItems():
	shopItems = {}
	for nationIdx in INDICES.values():
		shopItems[nationIdx] = dict((itemType, ({}, set())) for itemType in items.SIMPLE_ITEM_TYPE_INDICES)
		shopItems[nationIdx][ITEM_TYPE_INDICES['vehicle']] = ({}, set())

		xmlPath = vehicles._VEHICLE_TYPE_XML_PATH + AVAILABLE_NAMES[nationIdx] + '/list.xml'
		section = ResMgr.openSection(xmlPath)

		for vname, vsection in section.items():
			ctx = (None, xmlPath + '/' + vname)
			price = _xml.readPrice(ctx, vsection, 'price')

			# Read additional price data
			xmlVehPath = vehicles._VEHICLE_TYPE_XML_PATH + AVAILABLE_NAMES[nationIdx] + '/' + vname + '.xml'
			vehSec = ResMgr.openSection(xmlVehPath)
			priceFactorCamo = vehSec.readFloat('camouflage/priceFactor')
			hornPriceFactor = vehSec.readFloat('horns/priceFactor')
			ResMgr.purge(xmlVehPath, True)

			id = _xml.readInt(ctx, vsection, 'id', 0, 255)

			shopItems[nationIdx][ITEM_TYPE_INDICES['vehicle']][0][id] = (price[0], price[1], priceFactorCamo, hornPriceFactor)
			shopItems[nationIdx][ITEM_TYPE_INDICES['vehicle']][1].add(id)

		ResMgr.purge(xmlPath, True)

		'''
		compsXmlPath = vehicles._VEHICLE_TYPE_XML_PATH + AVAILABLE_NAMES[nationIdx] + '/components/'
		section = ResMgr.openSection(compsXmlPath + 'shells.xml')

		for vname, vsection in section.items():
			if vname == 'icons' or vsection.readBool("notInShop", False):
				continue

			ctx = (None, xmlPath + '/' + vname)
			price = _xml.readPrice(ctx, vsection, 'price')
			id = _xml.readInt(ctx, vsection, 'id', 0, 255)

			shopItems[nationIdx][ITEM_TYPE_INDICES['shell']][0][id] = (price[0], price[1], 0, 0)
			shopItems[nationIdx][ITEM_TYPE_INDICES['shell']][1].add(id)

		ResMgr.purge(compsXmlPath + 'shells.xml', True)
		'''

	return shopItems

def getOfflineInventory():
	data = dict((k, {}) for k in ITEM_TYPE_INDICES)
	i = 1
	i_crew = 1
	compDescr = {}
	data[ITEM_TYPE_INDICES['vehicle']] = {
		'repair': {},
		'lastCrew': {},
		'crew': {},
		'settings': {},
		'compDescr': {},
		'eqs': {},
		'eqsLayout': {},
		'shells': {},
		'customizationExpiryTime': {},
		'lock': {},
		'shellsLayout': {}
	}

	data[ITEM_TYPE_INDICES['tankman']] = {
		'vehicle': {},
		'compDescr': {}
	}

	for value in g_list._VehicleList__ids.values():
		vehicle = vehicles.VehicleDescr(typeID=value)
		compDescr[i] = vehicle.makeCompactDescr()
		turretGun = (vehicles.makeIntCompactDescrByID('vehicleTurret', *vehicle.turrets[0][0]['id']), vehicles.makeIntCompactDescrByID('vehicleGun', *vehicle.turrets[0][0]['guns'][0]['id']))

		tmanList = items.tankmen.generateTankmen(value[0], value[1], vehicle.type.crewRoles, False, items.tankmen.MAX_SKILL_LEVEL, [])
		tmanListCycle = cycle(tmanList)

		data[ITEM_TYPE_INDICES['vehicle']]['crew'].update({i: [tmanID for tmanID in xrange(i_crew, len(tmanList) + i_crew)]})
		data[ITEM_TYPE_INDICES['vehicle']]['settings'].update({i: VEHICLE_SETTINGS_FLAG.AUTO_REPAIR | VEHICLE_SETTINGS_FLAG.AUTO_LOAD})
		data[ITEM_TYPE_INDICES['vehicle']]['compDescr'].update(compDescr)
		data[ITEM_TYPE_INDICES['vehicle']]['eqs'].update({i: []})
		data[ITEM_TYPE_INDICES['vehicle']]['eqsLayout'].update({i: []})
		data[ITEM_TYPE_INDICES['vehicle']]['shells'].update({i: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])})
		data[ITEM_TYPE_INDICES['vehicle']]['shellsLayout'].update({i: {turretGun: vehicles.getDefaultAmmoForGun(vehicle.turrets[0][0]['guns'][0])}})

		for tmanID in xrange(i_crew, len(tmanList) + i_crew):
			data[ITEM_TYPE_INDICES['tankman']]['vehicle'][tmanID] = i
			data[ITEM_TYPE_INDICES['tankman']]['compDescr'][tmanID] = next(tmanListCycle)
			i_crew += 1

		i += 1

	return {'inventory': data}

def getOfflineStats():
	unlocksSet = set()
	vehiclesSet = set()

	for nationID in nations.INDICES.values():
		unlocksSet.update([vehicles.makeIntCompactDescrByID('vehicleChassis', nationID, i) for i in g_cache.chassis(nationID).keys()])
		unlocksSet.update([vehicles.makeIntCompactDescrByID('vehicleEngine', nationID, i) for i in g_cache.engines(nationID).keys()])
		unlocksSet.update([vehicles.makeIntCompactDescrByID('vehicleFuelTank', nationID, i) for i in g_cache.fuelTanks(nationID).keys()])
		unlocksSet.update([vehicles.makeIntCompactDescrByID('vehicleRadio', nationID, i) for i in g_cache.radios(nationID).keys()])
		unlocksSet.update([vehicles.makeIntCompactDescrByID('vehicleTurret', nationID, i) for i in g_cache.turrets(nationID).keys()])
		unlocksSet.update([vehicles.makeIntCompactDescrByID('vehicleGun', nationID, i) for i in g_cache.guns(nationID).keys()])
		unlocksSet.update([vehicles.makeIntCompactDescrByID('shell', nationID, i) for i in g_cache.shells(nationID).keys()])

		vData = [vehicles.makeIntCompactDescrByID('vehicle', nationID, i) for i in g_list.getList(nationID).keys()]
		unlocksSet.update(vData)
		vehiclesSet.update(vData)

	attrs = 0
	for field in dir(ACCOUNT_ATTR):
		value = getattr(ACCOUNT_ATTR, field, None)
		if isinstance(value, (int, long)):
			attrs |= value

	vehTypeXP = dict([(i, 0) for i in vehiclesSet])

	return {
		'account': {
			'autoBanTime': 0,
			'attrs': attrs,
			'clanDBID': 0,
			'premiumExpiryTime': time.time() + 86400
		},
		'stats': {
			'berths': 40,
			'accOnline': 0,
			'gold': 1000000,
			'isFinPswdVerified': True,
			'finPswdAttemptsLeft': 0,
			'denunciationsLeft': 0,
			'freeVehiclesLeft': 0,
			'refSystem': {'referrals': {}},
			'slots': 2000,
			'battlesTillCaptcha': 0,
			'hasFinPassword': True,
			'clanInfo': (None, None, 0, 0, 0),
			'unlocks': unlocksSet,
			'mayConsumeWalletResources': True,
			'freeTMenLeft': 0,
			'vehicleSellsLeft': 0,
			'SPA': {'/common/goldfish_bonus_applied/': u'1'},
			'vehTypeXP': vehTypeXP,
			'unitAcceptDeadline': 0,
			'globalVehicleLocks': {},
			'freeXP': 100000000,
			'captchaTriesLeft': 0,
			'fortResource': 0,
			'tkillIsSuspected': False,
			'credits': 100000000,
			'vehTypeLocks': {},
			'dailyPlayHours': [0],
			'globalRating': 0,
			'restrictions': {},
			'oldVehInvID': 0,
			'accOffline': 0,
			'dossier': '',
			'multipliedXPVehs': unlocksSet,
			'tutorialsCompleted': 33553532,
			'eliteVehicles': vehiclesSet,
			'playLimits': ((0, ''), (0, '')),
		}
	}

def getOfflineQuestsProgress():
	return {'quests': {}}
