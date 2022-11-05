import nations
import items
import functools
import time

from constants import ACCOUNT_ATTR
from items import ITEM_TYPE_INDICES, ITEM_TYPE_NAMES
items.init(True)
from items import vehicles
from items.vehicles import g_list, g_cache

from gui.mods.offhangar.logging import *
from gui.mods.offhangar.utils import *
from gui.mods.offhangar._constants import *

doLog = functools.partial(doLog, 'OFFHANGAR')
LOG_NOTE = functools.partial(doLog, '[NOTE]')
LOG_DEBUG = functools.partial(doLog, '[DEBUG]')

def getOfflineShop():
	return {
		'berthsPrices': (16,16,[300]),
		'freeXPConversion': (25,1),
		'dropSkillsCost': {
			0: { 'xpReuseFraction': 0.5, 'gold': 0, 'credits': 0 },
			1: { 'xpReuseFraction': 0.75, 'gold': 0, 'credits': 20000 },
			2: { 'xpReuseFraction': 1.0, 'gold': 200, 'credits': 0 }
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
			360: 24000,
			180: 13500,
			30: 2500
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
		'isEnabledBuyingGoldShellsForCredits': True,
		'items': {},
		'slotsPrices': (9, [300]),
		'freeXPToTManXPRate': 10,
		'defaults': {
			'items': {},
			'freeXPToTManXPRate': 0,
			'goodies': { 'prices': { } }
		},
		'sellPriceFactor': 0.5,
		'isEnabledBuyingGoldEqsForCredits': True,
		'playerInscriptionCost': {
			0: (15, True),
			7: (1500, False),
			30: (6000, False),
			'nations': { }
		}
	}

def getOfflineInventory():
	data = dict((k, {}) for k in ITEM_TYPE_INDICES)
	
	data[ITEM_TYPE_INDICES['vehicle']] = {
		'repair': {},
		'lastCrew': {},
		'settings': {},
		'compDescr': {},
		'eqs': {},
		'shells': {},
		'lock': {},
		'shellsLayout': {},
		'vehicle': {}
	}

	return {
		'inventory': data
	}

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
		'stats': {
			'berths': 40,
			'accOnline': 0,
			'autoBanTime': 0,
			'gold': 1000000,
			'crystal': 1000,
			'isFinPswdVerified': True,
			'finPswdAttemptsLeft': 0,
			'denunciationsLeft': 0,
			'freeVehiclesLeft': 0,
			'refSystem': {'referrals': {}},
			'slots': 0,
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
			'premiumExpiryTime': time.time()+86400,
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
			'clanDBID': 0,
			'attrs': attrs,
		}
	}

def getOfflineQuestsProgress():
	return {'quests': {}}