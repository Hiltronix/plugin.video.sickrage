import sys
import xbmc
import xbmcgui
import xbmcaddon
import sickbeard
import resources.lib.common as common


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Show log file level selection dialog.
def levelSelection():
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Log Detail Level", ["Info", "Warning", "Error", "Debug"])
    return ret  

  
# Set the status of a show.
def viewLog(level):
    level_list = ["info", "warning", "error", "debug"]
    log_list = Sickbeard.GetLog(level_list[level])
    log_str = '\n'.join(log_list)
    if (len(log_str) == 0):
        log_str = 'No Data.'
    w = common.TextViewer_Dialog('DialogTextViewer.xml', common.ADDON_PATH, header='Log File', text=log_str)
    w.doModal()


def main():
    level = levelSelection()
    if (level != -1):
        viewLog(level)
        xbmc.executebuiltin("Container.Refresh")

