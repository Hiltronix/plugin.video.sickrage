import sys
import xbmc
import xbmcgui
import xbmcaddon
import common
import sickbeard


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Show log file level selection dialog.
def levelSelection():
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Log Detail Level", ["Info", "Warning", "Error", "Debug", "Show Version"])
    return ret  

  
# View log file.
def viewLog(level):
    level_list = ["info", "warning", "error", "debug"]
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        log_list = Sickbeard.GetLog(level_list[level])
        if not log_list:
            exit()
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    log_str = '\n'.join(log_list)
    if (len(log_str) == 0):
        log_str = 'No Data.'
    w = common.TextViewer_Dialog('DialogTextViewer.xml', common.ADDON_PATH, header='Log File', text=log_str)
    w.doModal()


def main():
    level = levelSelection()
    if level == 4:
        api, version = Sickbeard.GetVersion()
        common.messageWindow('SickRage / SickBeard Version', 'API Version: {0}[CR]Version: {1}'.format(api, version))
        exit()
    if (level != -1):
        viewLog(level)
        xbmc.executebuiltin("Container.Refresh")

