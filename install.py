"""
Author: Tak
Website: https://tak.ta-note.com
Module Name: install.py
Description:
    Drag and drop module installer.
    Shelf button added in current shelf tab.
    "moduleName.mod" file created in "Documents\maya\modules" directory automatically.
"""

import os
import sys

import maya.cmds as cmds
import maya.mel as mel


MODULE_NAME = os.path.dirname(__file__).rsplit('/', 1)[-1]
MODULE_VERSION = '1.0.0'
MODULE_PATH = os.path.dirname(__file__)


def onMayaDroppedPythonFile(*args, **kwargs):
    modulesDir = getModulesDirectory()
    createModuleFile(modulesDir)
    addScriptPath()
    loadPlugins()
    addShelfButtons()

def getModulesDirectory():
    modulesDir = None

    documentDir = os.path.expanduser('~')
    mayaAppDir = os.path.join(documentDir, 'maya')
    modulesDir = os.path.join(mayaAppDir, 'modules')

    if not os.path.exists(modulesDir):
        os.mkdir(modulesDir)

    return modulesDir

def createModuleFile(modulesDir):
    moduleFileName = '{0}.mod'.format(MODULE_NAME)

    # Need to modify depend on module
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

    # Need to modify depend on module
    iconPath = 'takXgenManager.png'
    command = '''
import takXgenManager.xgenManager as xgManager

xgmg = xgManager.XGenManager()
xgmg.show()
'''
    cmds.shelfButton(
        command=command,
        annotation=MODULE_NAME,
        sourceType='Python',
        image=iconPath,
        image1=iconPath,
        parent=curShelf
    )

def getCurrentShelf():
    curShelf = None

    shelf = mel.eval('$gShelfTopLevel = $gShelfTopLevel')
    curShelf = cmds.tabLayout(shelf, query=True, selectTab=True)

    return curShelf
