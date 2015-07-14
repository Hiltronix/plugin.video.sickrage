import sys
import xbmc
import xbmcgui
import xbmcaddon
import sickbeard

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


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
    #xbmc.executebuiltin('XBMC.RunScript(script.toolbox, info=textviewer, header=Log File, text='+log_str+')')
    w = TextViewer_Dialog('DialogTextViewer.xml', ADDON_PATH, header='Log File', text=log_str)
    w.doModal()


def main():
    level = levelSelection()
    if (level != -1):
        viewLog(level)
        xbmc.executebuiltin("Container.Refresh")

