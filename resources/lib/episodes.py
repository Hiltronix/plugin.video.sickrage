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


# Get episodes for the selected show and season.
def GetSeasonEpisodes(tvdbid, season_number):
    season_episode_list = []
    season_episodes = Sickbeard.GetSeasonEpisodeList(tvdbid, season_number)
    temp = season_episodes.keys()
    temp = sorted(temp)
    for each in temp:
      season_episode_list.append([each, season_episodes[each]['name'], season_episodes[each]['status'], season_episodes[each]['airdate'], tvdbid, season_number])

    return season_episode_list


# Add directory items for each episode.
def menu(tvdbid, show_name, season_number):
    episode_list = GetSeasonEpisodes(tvdbid, season_number)
    episode_total = len(episode_list)
    season_numbers = []
    for ep_number, ep_name, ep_status, ep_airdate, ep_tvdbid, ep_season in episode_list:
        season_numbers.append(str(ep_number))
        season_status_args = ", "+ep_tvdbid+", "+ep_season+", "+"|".join(season_numbers)
        episode_status_args = ", "+ep_tvdbid+", "+ep_season+", "+ep_number

        context_menu_items = []
        context_menu_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_menu_items.append(('ExtendedInfo', 'XBMC.RunPlugin(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=10&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Set Episode Status', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setstatus.py'+episode_status_args+')'))
        context_menu_items.append(('Set Season Status', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setstatus.py'+season_status_args+')'))
        context_menu_items.append(('Download Episode', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/manualsearch.py'+episode_status_args+')'))
        if xbmc.getCondVisibility('System.HasAddon(context.videolookup.dialog)'):
            context_menu_items.append(('Video Lookup', 'XBMC.RunScript(context.videolookup.dialog)'))
        context_menu_items.append(('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'))
        context_menu_items.append(('Go Back', 'XBMC.Action(back)'))

        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        addEpisodeDirectory(show_name, season_number, ep_number, ep_name, ep_status, ep_airdate, ep_tvdbid, ep_season, thumbnail_path, fanart_path, episode_total, context_menu_items)

    xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')


# Add episode directory items.
def addEpisodeDirectory(show_name, season_number, ep_number, ep_name, ep_status, ep_airdate, ep_tvdbid, ep_season, thumbnail_path, fanart_path, episode_total, context_menu_items):
    url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(ep_tvdbid))+"&mode=6&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    if (ep_airdate != ''):
        ep_airdate = '(Aired ' + ep_airdate + ')   '
    list_item = xbmcgui.ListItem("[COLOR gold]"+str(ep_season)+"x"+str(ep_number)+". "+ep_name+"[/COLOR]   "+ep_airdate+ep_status, thumbnailImage=thumbnail_path)
    list_item.setProperty('fanart_image', fanart_path) 
    list_item.setProperty('LibraryHasMovie', '0')  # Removes the "Play" button from the video info screen, and replaces it with "Browse".
    meta = {}
    metaget = metahandlers.MetaData(tmdb_api_key=settings.__tmdb_api_key__)
    try:
        meta = metaget.get_episode_meta(show_name, ep_tvdbid, int(ep_season), int(ep_number), '', '', '')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_menu_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=list_item, isFolder=False, totalItems=episode_total)

