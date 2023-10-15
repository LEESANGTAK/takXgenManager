"""
Author: Tak
Website: https://ta-note.com
Description:
    Drag and drop install.py file in maya viewport.
    Shelf button will added in the current shelf tab.
    "<moduleName>.mod" file will created in "Documents\maya\modules" directory automatically.
"""

import os
import sys

import maya.cmds as cmds
import maya.mel as mel


MAYA_VERSION = int(cmds.about(version=True))
MODULE_PATH = os.path.dirname(__file__)
# Need to modify below depend on module
MODULE_NAME = 'takXGenManager'
MODULE_VERSION = '1.0.0'
SHELF_ICON_FILE = 'takXgenManager.png'
SHELF_BUTTON_COMMAND = '''
import takXgenManager.xgenManager as xgManager

xgmg = xgManager.XGenManager()
xgmg.show()
'''


def onMayaDroppedPythonFile(*args, **kwargs):
    modulesDir = getModulesDirectory()
    createModuleFile(modulesDir)
    addScriptPath()
    loadPlugins()
    addShelfButtons()

def getModulesDirectory():
    modulesDir = None

    mayaAppDir = cmds.internalVar(uad=True)
    modulesDir = os.path.join(mayaAppDir, 'modules')

    if not os.path.exists(modulesDir):
        os.mkdir(modulesDir)

    return modulesDir

def createModuleFile(modulesDir):
    moduleFileName = '{0}.mod'.format(MODULE_NAME)

    contents = '+ {0} {1} {2}'.format(MODULE_NAME, MODULE_VERSION, MODULE_PATH)

    with open(os.path.join(modulesDir, moduleFileName), 'w') as f:
        f.write(contents)

def addScriptPath():
    scriptPath = MODULE_PATH + '/scripts'
    if not scriptPath in sys.path:
        sys.path.append(scriptPath)

def loadPlugins():
    pluginsPath = os.path.join(MODULE_PATH, 'plug-ins')
    if os.path.exists(pluginsPath):
        pluginFiles = os.listdir(pluginsPath)
        if pluginFiles:
            for pluginFile in pluginFiles:
                cmds.loadPlugin(os.path.join(pluginsPath, pluginFile))

def addShelfButtons():
    curShelf = getCurrentShelf()

    cmds.shelfButton(
        command=SHELF_BUTTON_COMMAND,
        annotation=MODULE_NAME,
        sourceType='Python',
        image=SHELF_ICON_FILE,
        image1=SHELF_ICON_FILE,
        parent=curShelf
    )

def getCurrentShelf():
    curShelf = None

    shelf = mel.eval('$gShelfTopLevel = $gShelfTopLevel')
    curShelf = cmds.tabLayout(shelf, query=True, selectTab=True)

    return curShelf
