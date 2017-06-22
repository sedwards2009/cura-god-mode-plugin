# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from . import GodMode
from . import GodView

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "view": {
            "name": "GodView",
            "weight": 0
        }
    }

def register(app):
    return {"extension": GodMode.GodMode(), "view": GodView.GodView()}
