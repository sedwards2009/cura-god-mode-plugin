# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from . import GodMode

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "plugin": {
            "name": "God Mode",
            "author": "Ultimaker",
            "version": "1.0",
            "description": "Dump the contents of all settings to a HTML file.",
            "api": 3
        }
    }

def register(app):
    return {"extension": GodMode.GodMode()}
