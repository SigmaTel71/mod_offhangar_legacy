import BigWorld

class CameraNode(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)


# Polyfill for GUI Mod Loader
def load_mods():
    from constants import IS_DEVELOPMENT
    from debug_utils import LOG_DEBUG, LOG_NOTE, LOG_CURRENT_EXCEPTION, LOG_WARNING
    import ResMgr, os, glob
    
    modulepath = '/scripts/client/gui/mods/mod_*'
    if IS_DEVELOPMENT: _MOD_NAME_POSTFIX = '.py'
    else:              _MOD_NAME_POSTFIX = '.pyc'
    
    LOG_NOTE('Polyfill for GUI Mod Loader: idea by goofy67, implementation by WG & DrWeb7_1')
    sec = ResMgr.openSection('../paths.xml')
    subsec = sec['Paths']
    vals = subsec.values()[0:2]
    for val in vals:
        mp = val.asString + modulepath + _MOD_NAME_POSTFIX
        for fp in glob.iglob(mp):
            _, fn = os.path.split(fp)
            sn, _ = fn.split('.')
            if sn != '__init__':
                try:
                    LOG_DEBUG('GUI mod found', sn)
                    exec 'import gui.mods.' + sn
                except Exception as e:
                    LOG_WARNING('A problem had occurred while importing GUI mod', sn)
                    LOG_CURRENT_EXCEPTION()

load_mods()