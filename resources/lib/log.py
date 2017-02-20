import sys
import xbmc
import xbmcgui
import xbmcaddon
import common
import sickbeard


pluginID = 'plugin.video.sickrage'
my_addon = xbmcaddon.Addon(pluginID)
addon_path = my_addon.getAddonInfo('path')

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Show log file level selection dialog.
def levelSelection():
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Log Detail Level", ["Info", "Warning", "Error", "Debug"])
    return ret  

  
# View log file.
def viewLog(level):
    level_list = ["info", "warning", "error", "debug"]
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        log_list = Sickbeard.GetLog(level_list[level])
        if not log_list:
            exit()
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    log_str = '\n'.join(log_list)
    if (len(log_str) == 0):
        log_str = 'No Data.'
    w = common.TextViewer_Dialog('DialogTextViewer.xml', addon_path, header='Log File', text=log_str)
    w.doModal()


def main():
    level = levelSelection()
    if (level != -1):
        viewLog(level)
        xbmc.executebuiltin("Container.Refresh")

