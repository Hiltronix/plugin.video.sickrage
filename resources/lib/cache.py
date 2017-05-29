import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import os
import sys
import json
import time
import common
import settings
import sickbeard
import TvdbApi


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()

# Initialize TVdb class.
tvdb = TvdbApi.theTVDB()

# Logging level:
log_level = xbmc.LOGDEBUG       # Un-Comment this line for production.
#log_level = xbmc.LOGERROR       # Comment out this line for production.


def UpdateUpcomingEpisodes():
# Scan all upcoming episodes and update TVdb meta data.
# If any upcoming episodes are not cached, then download meta data to the cache location.
# Silent operation, intended for service.
    try:
        monitor = xbmc.Monitor()
        
        coming_soon = Sickbeard.GetFutureShows()
        if not coming_soon:
            return

        list = []

        # Get todays upcoming episodes.
        if len(coming_soon["today"]):
            for show in coming_soon['today']:
                list.append([str(show['tvdbid']), show['show_name'], bool(show['paused']), show['season'], show['episode'], show['airdate']])
              
        # Get coming soon episodes.
        if len(coming_soon["soon"]):    
            for show in coming_soon['soon']:
                list.append([str(show['tvdbid']), show['show_name'], bool(show['paused']), show['season'], show['episode'], show['airdate']])
    
        # Get upcoming later episodes.
        if len(coming_soon["later"]):
            for show in coming_soon['later']:
                list.append([str(show['tvdbid']), show['show_name'], bool(show['paused']), show['season'], show['episode'], show['airdate']])

        for tvdbid, show_name, paused, season, episode, airdate in list:
            if monitor.abortRequested():    # Check if Kodi is trying to shutdown.
                return
            xbmc.log('Service [{}] Updating Upcoming (non-forced): tvdb:{} {}-{}'.format(settings.pluginID, tvdbid, season, episode), level=log_level)
            CacheFromTvdb(tvdbid, season, episode, forceText=False, forceShowImages=False, forceActorImages=False, silent=True)
    except Exception, e:
        xbmc.log('Service [{}] Exception: {}  tvdb:{} {}-{}'.format(settings.pluginID, e, tvdbid, season, episode), level=xbmc.LOGERROR)


def UpdateAllShows(AllEpisodes=False):
# Scan all shows and make sure S01E01 is cached, so lists of shows open fast.
# All cached image files are checked for during the scan for S01E01.
# If S01E01 is not cached, then all meta data is downloaded to the cache location, including caching all the episodes for that show.
# If "AllEpisodes" is True, then each show is checked for any missing epsiodes meta data.
# If even one episode is missing, then all episodes are downloaded for that show.
# Silent operation, intended for service.
    try:
        monitor = xbmc.Monitor()
        
        shows = Sickbeard.GetShows()
        if not shows:
            xbmc.log('Service [{}] Updating all episodes...Local show list unavailable.'.format(settings.pluginID), level=log_level)
            return
            
        xbmc.log('Service [{}] Updating all episodes from TVdb.'.format(settings.pluginID), level=log_level)

        settings.my_addon.setSetting('TVdbUpdateAllEpisodesEnabled', 'true')
        settings.my_addon.setSetting('TVdbUpdateAllEpisodesRunning', 'true')
        settings.my_addon.setSetting('TVdbUpdateAllEpisodesProgress', '0')

        i = 0

        for show in sorted(shows, key=lambda k: k['show_name'], reverse=False):
            if monitor.abortRequested():    # Check if Kodi is trying to shutdown.
                return

            tvdbid = show['tvdbid']
            OneTimeEpUpdate = False

            # Update progress value.
            i += 1
            completed = int((float(i) / float(len(shows))) * 100.0)
            settings.my_addon.setSetting('TVdbUpdateAllEpisodesProgress', str(completed))

            # If this setting is changed to false, then the operation was cancelled.
            if settings.my_addon.getSetting('TVdbUpdateAllEpisodesEnabled') == 'false':
                return

            # Check for first episode S01E01.
            season = 1
            episode = 1
            json_file = os.path.join(settings.ep_cache_dir, '{}-{}-{}.json'.format(tvdbid, season, episode))
            if not os.path.isfile(json_file):
                # If episode S01E01 does not exist, it's a new show, force all epsisodes to be cached.
                OneTimeEpUpdate = True
            # Create first episode S01E01 if it doesn't exist.
            xbmc.log('Service [{}] Updating Show (non-forced): tvdb:{} {}-{}'.format(settings.pluginID, tvdbid, season, episode), level=log_level)
            CacheFromTvdb(tvdbid, season, episode, forceText=False, forceShowImages=False, forceActorImages=False, silent=True)

            # Skip doing all episodes check/updates if not required.
            if not AllEpisodes and not OneTimeEpUpdate:
                continue

            # Download basic episode list and check if all episode files exist.
            missingEpisodes = False
            data = tvdb.GetAllEpisodes(series_id=tvdbid)
            for ep in data:
                if monitor.abortRequested():    # Check if Kodi is trying to shutdown.
                    return
                season = ep['airedSeason']
                episode = ep['airedEpisodeNumber']
                json_file = os.path.join(settings.ep_cache_dir, '{}-{}-{}.json'.format(tvdbid, season, episode))
                file_exist = os.path.isfile(json_file)
                if not file_exist:
                    missingEpisodes = True

            # Skip downloading and saving all episodes if none are missing.
            if not missingEpisodes:
                xbmc.log('Service [{}] All Episodes Exist for: tvdb:{}'.format(settings.pluginID, tvdbid), level=log_level)
                continue

            # Do a non-forced update of each episode.  Only missing images and episode text is created.
            episodes = tvdb.GetAllEpisodesWithDetails(series_id=tvdbid)
            for ep in episodes:
                if monitor.abortRequested():    # Check if Kodi is trying to shutdown.
                    return
                season = ep['data']['airedSeason']
                episode = ep['data']['airedEpisodeNumber']

                # Load cached tvdb S01E01 episode json file.
                json_file = os.path.join(settings.ep_cache_dir, tvdbid + '-1-1.json')
                file_exist = os.path.isfile(json_file)
                if file_exist:    
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                    except Exception, e:
                        xbmc.log('Service [{}] Exception: {}'.format(settings.pluginID, e), level=xbmc.LOGERROR)
                        continue
                else:
                    continue
            
                # Swap out the episode details dict from the first episode json and insert the current episode details dict.
                data['Details'] = ep['data']            
            
                # Save show meta data as json file to cache:
                json_file = os.path.join(settings.ep_cache_dir, '{}-{}-{}.json'.format(tvdbid, int(season), int(episode)))
                try:
                    with open(json_file, 'w') as f:
                        json.dump(data, f, sort_keys=True, indent=4)
                except Exception, e:
                        xbmc.log('Service [{}] Exception: {}'.format(settings.pluginID, e), level=xbmc.LOGERROR)
                        continue

                xbmc.log('Service [{}] Updating All Episodes: tvdb:{} {}-{}'.format(settings.pluginID, tvdbid, season, episode), level=log_level)

        xbmc.log('Service [{}] Completed Updating all episodes.'.format(settings.pluginID), level=log_level)

    except Exception, e:
        xbmc.log('Service [{}] Exception: {}'.format(settings.pluginID, e), level=xbmc.LOGERROR)
    finally:
        settings.my_addon.setSetting('TVdbUpdateAllEpisodesEnabled', 'false')
        settings.my_addon.setSetting('TVdbUpdateAllEpisodesRunning', 'false')
        settings.my_addon.setSetting('TVdbUpdateAllEpisodesProgress', '0')


def CheckForTVdbUpdates():
# Get the list of TV shows that have had updates done to them between a time range.
# Then update the show images and actor images for any shows that has changes done to it, as well as the text for the very first episode S01E01.
# Then update the text for every episode in the TV series (show ID) that had a change made to it.
# Silent operation, intended for service.
    try:
        monitor = xbmc.Monitor()
        
        fromTime = int(settings.my_addon.getSetting('TVdbLastUpdated'))
        toTime = int(time.time())   # This is converted to an integer to strip off the decimal points that represent fractions of a second, which TVdb doesn't allow.
        rangeStr = 'Range: {}[{}] to {}[{}]'.format(fromTime, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(fromTime)), toTime, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(toTime)))
       
        updates = tvdb.GetUpdatedShows(fromTime, toTime)
        if not updates:
            xbmc.log('Service [{}] Checking for TVdb Changes...No updated shows list. ({})'.format(settings.pluginID, rangeStr), level=log_level)
            return

        shows = Sickbeard.GetShows()
        if not shows:
            xbmc.log('Service [{}] Checking for TVdb Changes...Local show list unavailable.'.format(settings.pluginID), level=log_level)
            return
            
        xbmc.log('Service [{}] Checking for TVdb Changes ({})'.format(settings.pluginID, rangeStr), level=log_level)

        for show in sorted(shows, key=lambda k: k['show_name'], reverse=False):
            tvdbid = show['tvdbid']

            # Check for existence of show ID in the TVdb updates list.
            if any(str(keyname['id']) == str(tvdbid) for keyname in updates):
                # This series was recently updated.
                # Force full update of S01E01 as a baseline refresh that includes images.
                season = 1
                episode = 1
                xbmc.log('Service [{}] TVdb Meta Data Updated: tvdb:{} {}-{}'.format(settings.pluginID, tvdbid, season, episode), level=log_level)
                CacheFromTvdb(tvdbid, season, episode, forceText=True, forceShowImages=True, forceActorImages=True, silent=True)

                if monitor.abortRequested():    # Check if Kodi is trying to shutdown.
                    return

                # Get basic info for all the episodes for this show ID, and check the last updated value per episode.
                # If an episode was changed within date range then update that episode's text info only.
                data = tvdb.GetAllEpisodes(series_id=tvdbid)
                for ep in data:
                    if monitor.abortRequested():    # Check if Kodi is trying to shutdown.
                        return
                    if int(ep['lastUpdated']) >= fromTime and int(ep['lastUpdated']) <= toTime:
                        season = ep['airedSeason']
                        episode = ep['airedEpisodeNumber']
                        # Force update of text info only.
                        xbmc.log('Service [{}] TVdb Meta Data Updated: tvdb:{} {}-{}'.format(settings.pluginID, tvdbid, season, episode), level=log_level)
                        CacheFromTvdb(tvdbid, season, episode, forceText=True, forceShowImages=False, forceActorImages=False, silent=True)

        settings.my_addon.setSetting('TVdbLastUpdated', str(toTime))
        xbmc.log('Service [{}] Completed Checking for TVdb Changes.'.format(settings.pluginID), level=log_level)

    except Exception, e:
        xbmc.log('Service [{}] Exception: {}'.format(settings.pluginID, e), level=xbmc.LOGERROR)


def CacheFromTvdb(tvdbid, season, episode, forceText=True, forceShowImages=True, forceActorImages=True, silent=False):
# Creates a local cache of show meta data and images for a show on TheTVdb.com.
# If "force" is False, then existing data will be passed over and not replaced.
    diag_title = 'Update from TVdb'
    
    tvdbid = str(tvdbid)
    
    json_file = os.path.join(settings.ep_cache_dir, '{}-{}-{}.json'.format(tvdbid, int(season), int(episode)))

    file_exist = os.path.isfile(json_file)
    # This is the required version of the file format, for this version of the app.
    required_version = 2

    if file_exist:    
        # Load cached tvdb episode json file.
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except Exception, e:
            print e
        # Get file version for compatibility of current app.
        file_version = data.get('Version', 0)
        # Get the last updated time in UTC Unix Epoch.
        ShowLastUpdated = TvdbApi.getFromDict(data, ['Show', 'lastUpdated'], 0)
        EpisodeLastUpdated = TvdbApi.getFromDict(data, ['Details', 'lastUpdated'], 0)
    
    # Meta data file:
    if forceText or not file_exist or (file_version < required_version):
        # Get show meta data:
        try:
            data = TvdbApi.GetMetaDataDict(tvdbid, int(season), int(episode), '', log=None)
        except Exception, e:
            err = 'ERROR Retrieving show meta data: ' + str(e)
            xbmc.log('[{}] Exception: {}  tvdb:{} {}-{}'.format(settings.pluginID, err, tvdbid, season, episode), level=xbmc.LOGERROR)
            if not silent:
                common.messageWindow(diag_title, err)
        
        # Save show meta data as json file to cache:
        try:
            with open(json_file, 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4)
        except Exception, e:
            err = 'ERROR Saving show meta data: ' + str(e)
            xbmc.log('[{}] Exception: {}  tvdb:{} {}-{}'.format(settings.pluginID, err, tvdbid, season, episode), level=xbmc.LOGERROR)
            if not silent:
                common.messageWindow(diag_title, err)

    # Show images:
    #if forceShowImages or not os.path.isfile(settings.image_cache_dir + tvdbid + '.poster.jpg') or not os.path.isfile(settings.image_cache_dir + tvdbid + '.fanart.jpg') or not os.path.isfile(settings.image_cache_dir + tvdbid + '.banner.jpg'):
    if forceShowImages or not os.path.isfile(settings.image_cache_dir + tvdbid + '.poster.jpg'):
        # Get show images links from meta data file dict:
        poster = TvdbApi.getFromDict(data, ['Images', 'poster'], [])
        fanart = TvdbApi.getFromDict(data, ['Images', 'fanart'], [])
        banner = TvdbApi.getFromDict(data, ['Images', 'banner'], [])

        # Save show image links:
        try:
            if poster and len(poster) > 0:
                TvdbApi.SaveImageFile(poster[0], settings.image_cache_dir, tvdbid + '.poster', log=None)
            if fanart and len(fanart) > 0:
                TvdbApi.SaveImageFile(fanart[0], settings.image_cache_dir, tvdbid + '.fanart', log=None)
            if banner and len(banner) > 0:
                TvdbApi.SaveImageFile(banner[0], settings.image_cache_dir, tvdbid + '.banner', log=None)
        except Exception, e:
            err = 'ERROR Saving show images: ' + str(e)
            xbmc.log('[{}] Exception: {}  tvdb:{} {}-{}'.format(settings.pluginID, err, tvdbid, season, episode), level=xbmc.LOGERROR)
            if not silent:
                common.messageWindow(diag_title, err)

    # Save actor images to cache.
    # They are only downloaded if they don't exist, or "force" is True.
    try:
        #pass
        actors = data.get('Actors', [])
        actors = TvdbApi.CacheActorImages(actors, settings.actor_cache_dir, forceActorImages)
    except Exception, e:
        err = 'ERROR Saving actor meta data: ' + str(e)
        xbmc.log('[{}] Exception: {}  tvdb:{} {}-{}'.format(settings.pluginID, err, tvdbid, season, episode), level=xbmc.LOGERROR)
        if not silent:
            common.messageWindow(diag_title, err)

    if not silent:
        if forceText or forceShowImages or forceActorImages:
            show_name = TvdbApi.getFromDict(data, ['Show', 'seriesName'], 'Unknown')
            title = TvdbApi.getFromDict(data, ['Details', 'episodeName'], 'Unknown')
            msg = u'{0}[CR]{1}[CR]Season: {2}  Epsiode: {3}[CR]TVdb: {4}'.format(show_name, title, season, episode, tvdbid)
            common.CreateNotification(header=diag_title, message=msg, icon=xbmcgui.NOTIFICATION_INFO, time=3000, sound=False)
    

# Clear image file cache.
def ClearImages():
    # Show images.
    path = settings.image_cache_dir
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.lower().endswith(".jpg"):
                os.unlink(os.path.join(path, file))
        for file in os.listdir(path):
            if file.lower().endswith(".png"):
                os.unlink(os.path.join(path, file))
    # Actor images.
    path = settings.actor_cache_dir
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.lower().endswith(".jpg"):
                os.unlink(os.path.join(path, file))
        for file in os.listdir(path):
            if file.lower().endswith(".png"):
                os.unlink(os.path.join(path, file))


# Clear episode meta data cache.
def ClearMetaData():
    path = settings.ep_cache_dir
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.lower().endswith(".json"):
                os.unlink(os.path.join(path, file))


if __name__ == '__main__':
    if len(sys.argv) == 4:
        tvdbid = sys.argv[1]
        season = sys.argv[2]
        episode = sys.argv[3]
        
        try:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            CacheFromTvdb(tvdbid, season, episode, forceText=True, forceShowImages=True, forceActorImages=True, silent=False)
            xbmc.executebuiltin('Container.Refresh')
        finally:
            xbmc.executebuiltin("Dialog.Close(busydialog)")
    
