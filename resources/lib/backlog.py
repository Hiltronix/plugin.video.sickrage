import sys
import urllib
import datetime
import xbmc
import xbmcgui
import xbmcplugin
import sickbeard
from metahandler import metahandlers


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Get a list of episodes in the SickRage backlog list.
def GetBacklogItems():
    backlog = Sickbeard.GetBacklog()
    backlog_list = []
    for episode in backlog:
        if (episode['status'] == 'Ended'):
            status = '[COLOR red]' + episode['status'] + '[/COLOR]'
        else:
            status = '[COLOR cyan]' + episode['status'] + '[/COLOR]'
        backlog_list.append([episode['show_name'], '[COLOR gold]'+episode['show_name']+'[/COLOR] '+str(episode['season'])+'x'+str(episode['episode'])+' '+episode['name']+'  '+str(datetime.date.fromordinal(episode['airdate']))+'    '+status, str(episode['showid']), episode['season'], episode['episode']])

    return backlog_list


# Add directory items for each backlogged episode.
def menu():
    backlog_list = GetBacklogItems()
    backlog_total = len(backlog_list)
    for show_name, backlog_name, tvdbid, season, episode in backlog_list:
        episode_status_args = ", "+tvdbid+", "+str(season)+", "+str(episode)

        context_menu_items = []
        context_menu_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_menu_items.append(('ExtendedInfo', 'XBMC.RunPlugin(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=10&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Episode List', 'XBMC.Container.Update(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=4&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Set Episode Status', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setstatus.py'+episode_status_args+')'))
        context_menu_items.append(('Add New Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/addshow.py, new)'))
        context_menu_items.append(('Delete Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/deleteshow.py, '+tvdbid+', '+show_name+')'))
        context_menu_items.append(('Force Update', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/forcesearch.py, '+tvdbid+')'))
        if xbmc.getCondVisibility('System.HasAddon(context.videolookup.dialog)'):
            context_menu_items.append(('Video Lookup', 'XBMC.RunScript(context.videolookup.dialog)'))
        context_menu_items.append(('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'))
        context_menu_items.append(('Go Back', 'XBMC.Action(back)'))
        
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        addBacklogDirectory(show_name, backlog_name, tvdbid, season, episode, thumbnail_path, backlog_total, context_menu_items)


# Add backlog items to directory.
def addBacklogDirectory(show_name, backlog_name, tvdbid, season, episode, thumbnail_path, backlog_total, context_items):
    url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode=6&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
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

