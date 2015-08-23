import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import sickbeard
import settings
from metahandler import metahandlers


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Get a list of episodes snatched and downloaded by SickRage.
def GetHistoryItems():
    history = Sickbeard.GetHistory(settings.__history_max__)
    history_list = []
    status_msg = '[COLOR gray]Unknown[/COLOR]'
    for show in history:
      if (show['status'] == 'Downloaded'):
          status_msg = '[COLOR cyan]' + str(show['status']) + '[/COLOR]'
      elif show['status']:
          status_msg = str(show['status'])
      history_list.append([show['show_name'], '[COLOR gold]'+show['show_name']+'[/COLOR] '+str(show['season'])+'x'+str(show['episode'])+' '+show['date']+'    '+status_msg, str(show['tvdbid']), show['season'], show['episode']])
  
    return history_list


# Add directory items for each episode recently grabbed
def menu():
    history_list = GetHistoryItems()
    history_total = len(history_list)
    for show_name, history_name, tvdbid, season, episode in history_list:
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
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        addHistoryDirectory(show_name, history_name, tvdbid, season, episode, thumbnail_path, fanart_path, history_total, context_menu_items)

    xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')


# Add history items to directory
def addHistoryDirectory(show_name, history_name, tvdbid, season, episode, thumbnail_path, fanart_path, history_total, context_items):
    url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode=6&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(history_name, thumbnailImage=thumbnail_path)
    list_item.setProperty('fanart_image', fanart_path) 
    meta = {}
    metaget = metahandlers.MetaData()
    try:
        meta = metaget.get_episode_meta(show_name, tvdbid, int(season), int(episode), '', '', '')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False, totalItems=history_total)

