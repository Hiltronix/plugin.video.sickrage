import xbmc
import xbmcgui
import xbmcplugin
import os
import sys
import json
import urllib
import cache
import common
import sickbeard
import TvdbApi


pluginID = 'plugin.video.sickrage'

# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get the tvdbid and show names.
def GetShowInfo(filter):
    shows = Sickbeard.GetShows()
    if not shows:
        exit()
    list = []
    for show in sorted(shows, key=lambda k: k['show_name'], reverse=False):
        name = show['show_name']
        tvdbid = show['tvdbid']
        paused = show['paused']
        next_airdate = show['next_ep_airdate']
        status = show['status']
        status_msg = '    [COLOR gray]Unknown[/COLOR]'
        if paused == 1:
            paused_msg = "Resume"
            ispaused = "    [COLOR cyan]Paused[/COLOR]"
        else:
            paused_msg = "Pause"
            ispaused = ""
        if status == 'Ended':
            status_msg = '    [COLOR red]'+str(status)+'[/COLOR]'
        elif status:
            status_msg = '    [COLOR gray]'+str(status)+'[/COLOR]'
        if filter:
            if (filter == 'All'):
                list.append([name, '[COLOR gold]' + name + '[/COLOR]' + status_msg + ispaused, str(tvdbid), paused_msg, next_airdate])
            if (filter == 'Continuing') and (status == 'Continuing'):
                list.append([name, '[COLOR gold]' + name + '[/COLOR]' + status_msg + ispaused, str(tvdbid), paused_msg, next_airdate])
            if (filter == 'Ended') and (status == 'Ended'):
                list.append([name, '[COLOR gold]' + name + '[/COLOR]' + status_msg + ispaused, str(tvdbid), paused_msg, next_airdate])
            if (filter == 'Paused') and (paused == 1) and (status == 'Continuing'):
                list.append([name, '[COLOR gold]' + name + '[/COLOR]' + status_msg + ispaused, str(tvdbid), paused_msg, next_airdate])
    return list


# Parse through shows and add directory line for each.
def menu(filter='All'):
    show_info = GetShowInfo(filter)
    total_items = len(show_info)

    for show_name, name, tvdbid, paused, next_airdate in show_info:
    
        # This is intended for general show info, so we force the use of Season 1, Episode 1 for generic reasons.  We can assume that all shows have at least 1 episode.
        season = 1
        episode = 1

        context_items = []
        context_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_items.append(('Open Show Folder', 'XBMC.RunPlugin(plugin://{0}?mode={1}&tvdb_id={2}&show_name={3})'.format(pluginID, 15, tvdbid, urllib.quote_plus(show_name.encode("utf-8")))))
        if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)'):
            context_items.append(('ExtendedInfo', 'XBMC.RunScript(script.extendedinfo, info=extendedtvinfo, tvdb_id={0})'.format(tvdbid)))
        context_items.append(('Episode List', 'XBMC.Container.Update(plugin://{0}?mode={1}&tvdb_id={2}&show_name={3})'.format(pluginID, 4, tvdbid, urllib.quote_plus(show_name.encode("utf-8")))))
        context_items.append(('Add New Show', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/addshow.py)'.format(pluginID)))
        context_items.append(('Delete Show', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/deleteshow.py, {1}, {2})'.format(pluginID, tvdbid, show_name)))
        context_items.append((paused + ' Show', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/setpausestate.py, {1}, {2})'.format(pluginID, paused, tvdbid)))
        context_items.append(('Force Server Update', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/forcesearch.py, {1})'.format(pluginID, tvdbid)))
        context_items.append(('Update Cache from TVdb', 'XBMC.RunScript(special://home/addons/{0}/resources/lib/cache.py, {1}, {2}, {3})'.format(pluginID, tvdbid, season, episode)))
        context_items.append(('Refresh List', 'XBMC.Container.Refresh'))
        context_items.append(('Go Back', 'XBMC.Action(back)'))
        
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        banner_path = Sickbeard.GetShowBanner(tvdbid)
        addDirectory(show_name, name, tvdbid, season, episode, next_airdate, thumbnail_path, fanart_path, banner_path, total_items, context_items)

    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
    xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    common.CreateNotification(header='Show List', message=str(total_items)+' Shows in list', icon=xbmcgui.NOTIFICATION_INFO, time=3000, sound=False)


def addDirectory(show_name, name, tvdbid, season, episode, next_airdate, thumbnail_path, fanart_path, banner_path, total_items, context_items):
    return_url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode=6&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(name, thumbnailImage=thumbnail_path)
    list_item.setArt({'icon': thumbnail_path, 'thumb': thumbnail_path, 'poster': thumbnail_path, 'fanart': fanart_path, 'banner': banner_path, 'clearart': '', 'clearlogo': '', 'landscape': ''})
    list_item.setProperty('LibraryHasMovie', '0')  # Removes the "Play" button from the video info screen, and replaces it with "Browse".
    meta = {}
    try:
        # Load and parse meta data.
        if not os.path.exists(cache.ep_cache_dir):
            os.makedirs(cache.ep_cache_dir)
        json_file = os.path.join(cache.ep_cache_dir, tvdbid + '-' + str(season) + '-' + str(episode) + '.json')
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
        meta['tvdb_id'] = str(tvdbid)
        meta['imdbnumber'] = TvdbApi.getFromDict(data, ['Show', 'imdbId'], '')
        meta['overlay'] = 6
        meta['plot'] = TvdbApi.getFromDict(data, ['Show', 'overview'], '')
        list_item.setRating('tvdb', TvdbApi.getFromDict(data, ['Show', 'siteRating'], 0), TvdbApi.getFromDict(data, ['Show', 'siteRatingCount'], 0), True)
        meta['premiered'] = TvdbApi.getFromDict(data, ['Show', 'firstAired'], next_airdate)
        meta['aired'] = meta['premiered']
        meta['dateadded'] = meta['premiered']
        # Date for sorting must be in Kodi format dd.mm.yyyy
        meta['date'] = meta['premiered'][8:10] + '.' + meta['premiered'][5:7] + '.' + meta['premiered'][0:4]
        meta['duration'] = TvdbApi.getFromDict(data, ['Show', 'runtime'], 0)    # Minutes.
        meta['genre'] = ' / '.join(TvdbApi.getFromDict(data, ['Show', 'genre'], ''))
        meta['studio'] = TvdbApi.getFromDict(data, ['Show', 'network'], '')
        meta['mpaa'] = TvdbApi.getFromDict(data, ['Show', 'rating'], '')
        meta['year'] = TvdbApi.getFromDict(data, ['Show', 'firstAired'], '')[:4]
        meta['status'] = TvdbApi.getFromDict(data, ['Show', 'status'], '')
        #meta['cast'] = []
        #actors = [{'name': 'Tom Cruise', 'role': 'Himself', 'thumbnail': ''}, {'name': 'Actor 2', 'role': 'role 2'}]
        actors = data.get('Actors', [])
        actors = TvdbApi.CacheActorImages(actors, cache.actor_cache_dir)
        for value in TvdbApi.getFromDict(data, ['Details', 'guestStars'], ''):
            actors.append(dict({'name': value, 'role': 'Guest Star'}))
        if actors:
            list_item.setCast(actors)
    except:
        meta['tvdb_id'] = str(tvdbid)
        meta['tvshowtitle'] = show_name
        meta['title'] = name
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=False, totalItems=total_items)  

