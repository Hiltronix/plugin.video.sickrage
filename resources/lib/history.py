import xbmc
import xbmcgui
import xbmcplugin
import os
import sys
import rpc
import json
import urllib
import common
import settings
import sickbeard
import TvdbApi


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Get a list of episodes snatched and downloaded by SickRage.
def GetHistoryItems():
    history = Sickbeard.GetHistory(settings.__history_max__)
    if not history:
        return []
    list = []
    status_msg = '[COLOR gray]Unknown[/COLOR]'
    for show in history:
      if (show['status'] == 'Downloaded'):
          status_msg = '[COLOR cyan]' + str(show['status']) + '[/COLOR]'
      elif show['status']:
          status_msg = str(show['status'])
      list.append([show['show_name'], '[COLOR gold]'+show['show_name']+'[/COLOR] '+str(show['season'])+'x'+str(show['episode'])+' '+show['date']+'    '+status_msg, str(show['tvdbid']), show['season'], show['episode']])
  
    return list


# Add directory items for each episode recently grabbed
def menu(handle):
    list = GetHistoryItems()
    total_items = len(list)
    for show_name, name, tvdbid, season, episode in list:
        episode_status_args = ", "+tvdbid+", "+str(season)+", "+str(episode)

        context_items = []
        context_items.append(('Episode List', 'XBMC.Container.Update(plugin://{0}?mode={1}&tvdb_id={2}&show_name={3})'.format(settings.pluginID, 4, tvdbid, urllib.quote_plus(show_name.encode("utf-8")))))
        context_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_items.append(('Open Show Folder', 'XBMC.RunPlugin(plugin://{0}?mode={1}&tvdb_id={2}&show_name={3})'.format(settings.pluginID, 15, tvdbid, urllib.quote_plus(show_name.encode("utf-8")))))
        if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)'):
            context_items.append(('ExtendedInfo', 'XBMC.RunScript(script.extendedinfo, info=extendedtvinfo, tvdb_id={0})'.format(tvdbid)))
        context_items.append(('Set Episode Status', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/setstatus.py, {1}, {2}, {3})'.format(settings.pluginID, tvdbid, season, episode)))
        context_items.append(('Add New Show', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/addshow.py)'.format(settings.pluginID)))
        if xbmc.getCondVisibility('System.HasAddon(plugin.program.qbittorrent)'):
            context_items.append(('Search qBittorrent', 'XBMC.Container.Update(plugin://plugin.program.qbittorrent?mode=1&keywords={}+S{:02d}E{:02d})'.format(urllib.quote_plus(show_name.encode('utf-8')), int(season), int(episode))))
        context_items.append(('Delete Show', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/deleteshow.py, {1}, {2})'.format(settings.pluginID, tvdbid, show_name)))
        context_items.append(('Force Server Update', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/forcesearch.py, {1})'.format(settings.pluginID, tvdbid)))
        context_items.append(('Update Cache from TVdb', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/cache.py, {1}, {2}, {3})'.format(settings.pluginID, tvdbid, season, episode)))
        context_items.append(('Refresh List', 'XBMC.Container.Refresh'))
        context_items.append(('Go Back', 'XBMC.Action(back)'))
        
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        banner_path = Sickbeard.GetShowBanner(tvdbid)
        addDirectory(handle, show_name, name, tvdbid, season, episode, thumbnail_path, fanart_path, banner_path, total_items, context_items)

    xbmcplugin.addSortMethod(handle=int(handle), sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(handle=int(handle), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
    xbmcplugin.setContent(handle=int(handle), content='tvshows')
    xbmcplugin.endOfDirectory(int(handle))
    common.CreateNotification(header='Show List', message=str(total_items)+' Shows in list', icon=xbmcgui.NOTIFICATION_INFO, time=3000, sound=False)


# Add history items to directory
def addDirectory(handle, show_name, name, tvdbid, season, episode, thumbnail_path, fanart_path, banner_path, total_items, context_items):
    path = rpc.GetEpisodePath(tvdbid, season, episode)
    if path:
        # If path to video is found, play video on click.
        return_url = path
    else:
        # If path to video is NOT found, then display episode video dialog meta data.
        return_url = 'plugin://{}/?mode={}&tvdb_id={}&show_name={}'.format(settings.pluginID, 6, tvdbid, urllib.quote_plus(show_name.encode("utf-8")))

    list_item = xbmcgui.ListItem(name, thumbnailImage=thumbnail_path)
    list_item.setArt({'icon': thumbnail_path, 'thumb': thumbnail_path, 'poster': thumbnail_path, 'fanart': fanart_path, 'banner': banner_path, 'clearart': '', 'clearlogo': '', 'landscape': ''})
    list_item.setProperty('LibraryHasMovie', '0')  # Removes the "Play" button from the video info screen, and replaces it with "Browse".
    meta = {}
    try:
        # Load and parse meta data.
        if not os.path.exists(settings.ep_cache_dir):
            os.makedirs(settings.ep_cache_dir)
        json_file = os.path.join(settings.ep_cache_dir, '{}-{}-{}.json'.format(tvdbid, int(season), int(episode)))
        if os.path.isfile(json_file):
            # Load cached tvdb episode json file.
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
            except Exception, e:
                print e
        else:
            data = TvdbApi.GetMetaDataDict(tvdbid, int(season), int(episode), '', log=None)
            # Save cached tvdb episode json file.
            try:
                with open(json_file, 'w') as f:
                    json.dump(data, f, sort_keys=True, indent=4)
            except Exception, e:
                print e
        meta['tvshowtitle'] = TvdbApi.getFromDict(data, ['Show', 'seriesName'], show_name)
        meta['sorttitle'] = meta['tvshowtitle']
        meta['title'] = name # This is what is displayed at the top of the video dialog window.
        meta['originaltitle'] = TvdbApi.getFromDict(data, ['Details', 'episodeName'], name)
        meta['season'] = int(season)
        meta['episode'] = int(episode)
        meta['tvdb_id'] = str(tvdbid)
        meta['imdbnumber'] = TvdbApi.getFromDict(data, ['Show', 'imdbId'], '')
        meta['overlay'] = 6
        meta['plot'] = TvdbApi.getFromDict(data, ['Details', 'overview'], '')
        list_item.setRating('tvdb', TvdbApi.getFromDict(data, ['Show', 'siteRating'], 0), TvdbApi.getFromDict(data, ['Show', 'siteRatingCount'], 0), True)
        meta['premiered'] = TvdbApi.getFromDict(data, ['Details', 'firstAired'], '')
        meta['aired'] = meta['premiered']
        meta['dateadded'] = meta['premiered']
        # Date for sorting must be in Kodi format dd.mm.yyyy
        meta['date'] = meta['premiered'][8:10] + '.' + meta['premiered'][5:7] + '.' + meta['premiered'][0:4]
        meta['duration'] = int(TvdbApi.getFromDict(data, ['Show', 'runtime'], 0)) * 60    # Must be in seconds as an integer.
        meta['genre'] = ' / '.join(TvdbApi.getFromDict(data, ['Show', 'genre'], ''))
        meta['writer'] = ', '.join(TvdbApi.getFromDict(data, ['Details', 'writers'], ''))
        meta['director'] = ', '.join(TvdbApi.getFromDict(data, ['Details', 'directors'], ''))
        meta['studio'] = TvdbApi.getFromDict(data, ['Show', 'network'], '')
        meta['mpaa'] = TvdbApi.getFromDict(data, ['Show', 'rating'], '')
        meta['episode_id'] = TvdbApi.getFromDict(data, ['Details', 'id'], '')
        meta['year'] = TvdbApi.getFromDict(data, ['Details', 'firstAired'], '')[:4]
        meta['status'] = TvdbApi.getFromDict(data, ['Show', 'status'], '')
        airsDayOfWeek = TvdbApi.getFromDict(data, ['Show', 'airsDayOfWeek'], '')
        airsTime = TvdbApi.getFromDict(data, ['Show', 'airsTime'], '')
        if airsDayOfWeek or airsTime:
            meta['status'] += ' ({}{}{})'.format(airsDayOfWeek[0:3], ' ' if airsDayOfWeek and airsTime else '',airsTime)
        meta['mediatype'] = 'episode'   # string - "video", "movie", "tvshow", "season", "episode" or "musicvideo" 
        #meta['cast'] = []
        #actors = [{'name': 'Tom Cruise', 'role': 'Himself', 'thumbnail': ''}, {'name': 'Actor 2', 'role': 'role 2'}]
        actors = data.get('Actors', [])
        actors = TvdbApi.CacheActorImages(actors, settings.actor_cache_dir)
        for value in TvdbApi.getFromDict(data, ['Details', 'guestStars'], ''):
            actors.append(dict({'name': value, 'role': 'Guest Star'}))
        if actors:
            list_item.setCast(actors)
    except:
        meta['tvdb_id'] = str(tvdbid)
        meta['tvshowtitle'] = show_name
        meta['title'] = name
        meta['season'] = int(season)
        meta['episode'] = int(episode)
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(handle), url=return_url, listitem=list_item, isFolder=False, totalItems=total_items)

