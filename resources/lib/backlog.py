import xbmcplugin
import xbmcgui
import sys
import datetime
import sickbeard
import urllib
from metahandler import metahandlers


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Get a list of episodes in the SickRage backlog list.
def GetBacklogItems():
  show_ids = Sickbeard.GetShowIds()
  show_info = Sickbeard.GetShowInfo(show_ids)

  show_names = {}
  for show_name, tvdbid in sorted(show_info.iteritems()):
    show_names[show_name] = str(tvdbid[0])

  backlog = Sickbeard.GetBacklog()
  backlog_list = []
  for episode in backlog:
    tvdbid = show_names[episode['show_name']]
    if (episode['status'] == 'Ended'):
        status = '[COLOR red]' + episode['status'] + '[/COLOR]'
    else:
        status = '[COLOR cyan]' + episode['status'] + '[/COLOR]'
    backlog_list.append([episode['show_name'], '[COLOR gold]'+episode['show_name']+'[/COLOR] '+str(episode['season'])+'x'+str(episode['episode'])+' '+episode['name']+'  '+str(datetime.date.fromordinal(episode['airdate']))+'    '+status, str(tvdbid), episode['season'], episode['episode']])

  return backlog_list


# Add directory items for each backlogged episode.
def menu():
    backlog_list = GetBacklogItems()
    backlog_total = len(backlog_list)
    for show_name, backlog_name, tvdbid, season, episode in backlog_list:
        episode_status_args = ", "+tvdbid+", "+str(season)+", "+str(episode)
        context_items = [('Show Info', 'XBMC.Action(Info)'),\
                         ('Episode List', 'XBMC.Container.Update(plugin://plugin.video.sickrage?url='+urllib.quote_plus(str(tvdbid))+'&mode=4&name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'),\
                         ('Set Episode Status', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setstatus.py'+episode_status_args+')'),\
                         ('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'),\
                         ('Go Back', 'XBMC.Action(back)')]
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        addBacklogDirectory(show_name, backlog_name, tvdbid, season, episode, thumbnail_path, backlog_total, context_items)


# Add backlog items to directory.
def addBacklogDirectory(show_name, backlog_name, tvdbid, season, episode, thumbnail_path, backlog_total, context_items):
    url = sys.argv[0]+"?url="+urllib.quote_plus(str(tvdbid))+"&mode=6&name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(backlog_name, thumbnailImage=thumbnail_path)
    meta = {}
    metaget = metahandlers.MetaData()
    try:
        meta = metaget.get_episode_meta(show_name, tvdbid, int(season), int(episode), '', '', '')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False, totalItems=backlog_total)

