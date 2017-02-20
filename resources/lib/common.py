import xbmc
import xbmcgui
import os
import sys
import math
import json


def getFromDict(dataDict, mapList, default_result=None):
# Similar to dictionary '.get' but for nested dictionaies.
# Example: getFromDict(dataDict, ["b", "v", "y"])
# Returns 'None' if not found, unless a default result is provided.
    try:
        value = reduce(lambda d, k: d[k], mapList, dataDict)
        if value:
            return value
        else:
            return default_result
    except Exception:
        return default_result


def GetDirSizeFormatted(start_path):
# Gets the files size and returns the formatted size.
    try:
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        places = (0, 0, 1, 2, 2, 3, 3, 3, 3)

        size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                size += os.path.getsize(fp)

        if (size > 0):
            i = int(math.floor(math.log(size, 1024)))
            p = math.pow(1024, i)
            s = round(size / p, places[i])
            if places[i] == 0:
                s = int(s)
            return '%s %s' %(s, size_name[i])
        else:
            return '0B'
    except Exception:
        return '???'


class TextViewer_Dialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.text = kwargs.get('text')
        self.header = kwargs.get('header')

    def onInit(self):
        self.getControl(1).setLabel(self.header)
        self.getControl(5).setText(self.text)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        pass

    def onFocus(self, controlID):
        pass


def CreateNotification(header="", message="", icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=True):
# Popup notification in bottom right corner.
# Info: icon=xbmcgui.NOTIFICATION_INFO
# Warning: icon=xbmcgui.NOTIFICATION_WARNING
# Error: icon=xbmcgui.NOTIFICATION_ERROR
    dialog = xbmcgui.Dialog()
    dialog.notification(heading=header, message=message, icon=icon, time=time, sound=sound)


def messageWindow(header, message):
# Show message pop up.
    dialog = xbmcgui.Dialog()
    dialog.ok(header, message)


def errorWindow(header, message):
# Show error pop up then exit plugin.
    dialog = xbmcgui.Dialog()
    dialog.ok(header, message)
    sys.exit()
    

def selectNoYes(title, No, Yes):
# Yes or No dialog style dialog.
# Returns False for the first "No" value, and True for the second "Yes" value.
# Returns -1 if cancelled.
    dialog = xbmcgui.Dialog()
    ret = dialog.select(title, [No, Yes])
    if (ret == -1):
        return ret
    if ret == 1:
        return True
    else:
        return False


def JsonRpc(id, method, params):
    query = xbmc.executeJSONRPC('{"id":"%s", "jsonrpc": "2.0", "method": "%s", "params": %s}' %(id, method, json.dumps(params)))
    query = unicode(query, 'utf-8', errors='ignore')
    result = json.loads(query)
    return result

