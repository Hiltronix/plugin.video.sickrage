import xbmcplugin
import xbmcgui
import sys
import sickbeard
import urllib
from metahandler import metahandlers


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Get a list of episodes grabbed by SickRage
def GetHistoryItems():
  show_ids = Sickbeard.GetShowIds()
  show_info = Sickbeard.GetShowInfo(show_ids)

  show_names = {}
  for show_name, tvdbid in sorted(show_info.iteritems()):
    show_names[show_name] = str(tvdbid[0])
    
  history = Sickbeard.GetHistory()
  history_list = []
  for show in history:
    tvdbid = show_names[show['show_name']]
    if (show['status'] == 'Downloaded'):
        status = '[COLOR cyan]' + show['status'] + '[/COLOR]'
    else:
        status = show['status']
    history_list.append([show['show_name'], '[COLOR gold]'+show['show_name']+'[/COLOR] '+str(show['season'])+'x'+str(show['episode'])+' '+show['date']+'    '+status, str(tvdbid), show['season'], show['episode']])
  
  return history_list


# Add directory items for each episode recently grabbed
def menu():
    history_list = GetHistoryItems()
    history_total = len(history_list)
    for show_name, history_name, tvdbid, season, episode in history_list:
        episode_status_args = ", "+tvdbid+", "+str(season)+", "+str(episode)
        context_items = [('Show Info', 'XBMC.Action(Info)'),\
                         ('Set Episode Status', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setstatus.py'+episode_status_args+')'),\
                         ('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'),\
                         ('Go Back', 'XBMC.Action(back)')]
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        addHistoryDirectory(show_name, history_name, tvdbid, season, episode, thumbnail_path, history_total, context_items)


# Add history items to directory
def addHistoryDirectory(show_name, history_name, tvdbid, season, episode, thumbnail_path, history_total, context_items):
    url = sys.argv[0]+"?url="+urllib.quote_plus(str(tvdbid))+"&mode=6&name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(history_name, thumbnailImage=thumbnail_path)
    meta = {}
    metaget = metahandlers.MetaData()
    try:
        meta = metaget.get_episode_meta(show_name, tvdbid, season, episode, '', '', '')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False, totalItems=history_total)

