import xbmc
import xbmcgui
import sys
import common
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
    message = Sickbeard.ForceDownload(tvdbid, season, episode)
    if not message:
        exit()
    messageWindow(message)


common.messageWindow('Notice', '- This function can take several minutes, and cause the server to be unresponive.[CR]- Setting episode status to "wanted" may be slower but provide a better user experience, provided the show is not paused.')
rtn = common.selectNoYes('Continue?', 'No', 'Yes')
if rtn != True:
    exit()

manualSearch(__tvdbid__, __season__, __episode__)
xbmc.executebuiltin("Container.Refresh")
