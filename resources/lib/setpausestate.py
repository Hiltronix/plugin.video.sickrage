import xbmc
import xbmcgui
import sickbeard


Sickbeard = sickbeard.SB()


# Show error pop up then exit plugin
def messageWindow(message):
    dialog = xbmcgui.Dialog()
    dialog.ok("Show Status", message)


paused = sys.argv[1]
tvdbid = sys.argv[2]

if paused == "Pause":
    pause = "1"
else:
    pause = "0"
    
message = Sickbeard.SetPausedState(pause, tvdbid)
messageWindow(message)
xbmc.executebuiltin("Container.Refresh")

