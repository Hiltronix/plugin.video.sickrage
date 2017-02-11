import xbmc
import xbmcgui
import xbmcplugin
import os
import sys
import json
import urllib
import common
import settings
import sickbeard
import TvdbApi


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get the tvdbid and show names.
def GetShowInfo(filter):
    shows = Sickbeard.GetShows()
    list = []
    for show in sorted(shows, key=lambda k: k['show_name'], reverse=False):
        name = show['show_name']
        tvdbid = show['tvdbid']
        paused = show['paused']
        next_airdate = show['next_ep_airdate']
        status = show['status']
        status_msg = '    [COLOR gray]Unknown[/COLOR]'
        if paused == 0:
            paused_msg = "Pause"
            ispaused = ""
        else:
            paused_msg = "Resume"
            ispaused = "    [COLOR cyan]Paused[/COLOR]"
        if status == 'Ended':
            status_msg = '    [COLOR red]'+str(status)+'[/COLOR]'
        elif status:
            status_msg = '    [COLOR gray]'+str(status)+'[/COLOR]'
        if filter:
            if (filter == 'All'):
                list.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), paused_msg, next_airdate])
            if (filter == 'Continuing') and (status == 'Continuing'):
                list.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), paused_msg, next_airdate])
            if (filter == 'Ended') and (status == 'Ended'):
                list.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), paused_msg, next_airdate])
            if (filter == 'Paused') and (paused == 1):
                list.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), paused_msg, next_airdate])
    return list


# Parse through shows and add directory line for each.
def menu(filter='All'):
    show_info = GetShowInfo(filter)
    total_items = len(show_info)

    for show_name, name, tvdbid, paused, next_airdate in show_info:

        context_items = []
        context_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_items.append(('ExtendedInfo', 'XBMC.RunPlugin(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=10&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_items.append(('Episode List', 'XBMC.Container.Update(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=4&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_items.append(('Add New Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/addshow.py, new)'))
        context_items.append(('Delete Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/deleteshow.py, '+tvdbid+', '+show_name+')'))
        context_items.append((paused+' Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setpausestate.py, '+paused+', '+tvdbid+')'))
        context_items.append(('Force Server Update', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/forcesearch.py, '+tvdbid+')'))
        #context_items.append(('Update Show Images', 'XBMC.RunPlugin(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=13&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_items.append(('Update Cache from TVdb', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/forceupdate.py, {0}, {1}, {2})'.format(tvdbid, 1, 1)))
        context_items.append(('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'))
        context_items.append(('Go Back', 'XBMC.Action(back)'))
        #if xbmc.getCondVisibility('System.HasAddon(context.videolookup.dialog)'):
        #    context_items.append(('Video Lookup', 'XBMC.RunScript(context.videolookup.dialog)'))
        
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        banner_path = Sickbeard.GetShowBanner(tvdbid)
        addDirectory(show_name, name, tvdbid, next_airdate, thumbnail_path, fanart_path, banner_path, total_items, context_items)

    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
    xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    common.CreateNotification(header='Show List', message=str(total_items)+' Shows in list', icon=xbmcgui.NOTIFICATION_INFO, time=3000, sound=False)


def addDirectory(show_name, name, tvdbid, next_airdate, thumbnail_path, fanart_path, banner_path, total_items, context_items):
    return_url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode=6&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(name, thumbnailImage=thumbnail_path)
    list_item.setArt({'icon': thumbnail_path, 'thumb': thumbnail_path, 'poster': thumbnail_path, 'fanart': fanart_path, 'banner': banner_path, 'clearart': '', 'clearlogo': '', 'landscape': ''})
    list_item.setProperty('LibraryHasMovie', '0')  # Removes the "Play" button from the video info screen, and replaces it with "Browse".
    meta = {}
    season = 1
    episode = 1
    try:
        # Load and parse meta data.
        ep_cache_dir = xbmc.translatePath('special://temp/sb/cache/episodes/')
        if not os.path.exists(ep_cache_dir):
            os.makedirs(ep_cache_dir)
        json_file = os.path.join(ep_cache_dir, tvdbid + '-' + str(season) + '-' + str(episode) + '.json')
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
        actors = data.get('Actors', '')
        actor_cache_dir = xbmc.translatePath('special://temp/sb/cache/actors/')
        actors = TvdbApi.CacheActorImages(actors, actor_cache_dir)
        for value in TvdbApi.getFromDict(data, ['Details', 'guestStars'], ''):
            actors.append(dict({'name': value, 'role': 'Guest Star'}))
        list_item.setCast(actors)
    except:
        meta['tvdb_id'] = str(tvdbid)
        meta['tvshowtitle'] = show_name
        meta['title'] = name
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=False, totalItems=total_items)  

