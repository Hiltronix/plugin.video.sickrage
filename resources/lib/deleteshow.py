import xbmc
import xbmcgui
import sickbeard

tvdbid = sys.argv[1]
show_name = sys.argv[2]

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

def confirmDialog(show_name):
    list = ["No", "Yes"]
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Are you sure you want to delete '+show_name+'?', list)
    return ret

def removeDialog(show_name):
    list = ["No", "Yes"]
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Delete ALL files as well? IRREVERSIBLE!', list)
    return ret

def deleteShow(tvdbid, removefiles):
    ret = Sickbeard.DeleteShow(tvdbid, removefiles)
    dialog = xbmcgui.Dialog()
    dialog.ok('Delete Show', ret)
    xbmc.executescript('special://home/addons/plugin.video.sickrage/resources/lib/refresh.py')
    return ret

if confirmDialog(show_name) == 1:
    removefiles = removeDialog(show_name)
    if (removefiles != -1):
        deleteShow(tvdbid, removefiles)
        # Refresh the directory listing after deleting a show.
        xbmc.executebuiltin("Container.Refresh")