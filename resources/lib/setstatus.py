import xbmc
import xbmcgui
import sys
import common
import sickbeard


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


__tvdbid__ = sys.argv[1]
__season__ = sys.argv[2]
__episode__ = sys.argv[3]


# Show status selection dialog.
def statusSelection():
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Set Status", ["Wanted", "Skipped", "Archived", "Ignored"])
  return ret  

  
# Set the status of a show.
def setStatus(status):
  status_list = ["wanted", "skipped", "archived", "ignored"]
  episode_list = []

  if "|" in __episode__:
    episode_list = __episode__.split("|")
    for ep in episode_list:
      Sickbeard.SetShowStatus(__tvdbid__, __season__, ep, status_list[status])
  else:
    Sickbeard.SetShowStatus(__tvdbid__, __season__, __episode__, status_list[status])

status = statusSelection()
if (status != -1):
    result = setStatus(status)
    if result:
        common.messageWindow('Set Episode Status', result)
    xbmc.executebuiltin("Container.Refresh")
