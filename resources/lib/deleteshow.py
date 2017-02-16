import xbmc
import xbmcgui
import common
import sickbeard


tvdbid = sys.argv[1]
show_name = sys.argv[2]

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


def deleteShow(tvdbid, removefiles):
    ret = Sickbeard.DeleteShow(tvdbid, removefiles)
    dialog = xbmcgui.Dialog()
    dialog.ok('Delete Show', ret)
    xbmc.executescript('special://home/addons/plugin.video.sickrage/resources/lib/refresh.py')
    return ret


rtn = common.selectNoYes('Are you sure you want to delete ' + show_name + '?', 'No', 'Yes')
if rtn != True:
    exit()
rtn = common.selectNoYes('Delete ALL files as well?  IRREVERSIBLE!', 'Delete show entry, NOT the files.', 'Delete the show entry and ALL the files.')
if rtn == -1:
    exit()
removefiles = rtn
deleteShow(tvdbid, removefiles)
xbmc.executebuiltin("Container.Refresh")

