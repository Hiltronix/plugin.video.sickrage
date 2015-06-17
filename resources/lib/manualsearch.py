import xbmc
import xbmcgui
import sys
import sickbeard

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

__tvdbid__ = sys.argv[1]
__season__ = sys.argv[2]
__episode__ = sys.argv[3]

# Show pop up
def messageWindow(message):
    dialog = xbmcgui.Dialog()
    dialog.ok("Search Status", message)
  
# Set the status of a show.
def manualSearch(tvdbid, season, episode):
    message = Sickbeard.ManualSearch(tvdbid, season, episode)
    messageWindow(message)

manualSearch(__tvdbid__, __season__, __episode__)
xbmc.executebuiltin("Container.Refresh")
