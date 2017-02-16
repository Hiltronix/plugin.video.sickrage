import xbmc
import xbmcgui
import xbmcaddon
import os
import sys
import json
import common
import TvdbApi


my_addon = xbmcaddon.Addon('plugin.video.sickrage')

cache_dir = xbmc.translatePath('special://temp/sb/cache/')
ep_cache_dir = xbmc.translatePath('special://temp/sb/cache/episodes/')
image_cache_dir = xbmc.translatePath('special://temp/sb/cache/images/')
actor_cache_dir = xbmc.translatePath('special://temp/sb/cache/actors/')


def CacheFromTvdb(tvdbid, season, episode, force=True):
# Creates a local cache of show meta data and images for a show on TheTVdb.com.
# If "force" is False, then existing data will be passed over and not replaced.
    diag_title = 'Update from TVdb'
    
    tvdbid = str(tvdbid)
    
    json_file = os.path.join(ep_cache_dir, tvdbid + '-' + str(season) + '-' + str(episode) + '.json')

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
    
    # Meta data file:
    if force or not file_exist or (file_version < required_version):
        # Get show meta data:
        try:
            data = TvdbApi.GetMetaDataDict(tvdbid, int(season), int(episode), '', log=None)
        except Exception, e:
            common.messageWindow(diag_title, 'ERROR Retrieving show meta data: ' + str(e))
        
        # Save show meta data as json file to cache:
        try:
            with open(json_file, 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4)
        except Exception, e:
            common.messageWindow(diag_title, 'ERROR Saving show meta data: ' + str(e))

    # Show images:
    #if force or not os.path.isfile(image_cache_dir + tvdbid + '.poster.jpg') or not os.path.isfile(image_cache_dir + tvdbid + '.fanart.jpg') or not os.path.isfile(image_cache_dir + tvdbid + '.banner.jpg'):
    if force or not os.path.isfile(image_cache_dir + tvdbid + '.poster.jpg'):
        # Get show images links from meta data file dict:
        poster = TvdbApi.getFromDict(data, ['Images', 'poster'], [])
        fanart = TvdbApi.getFromDict(data, ['Images', 'fanart'], [])
        banner = TvdbApi.getFromDict(data, ['Images', 'banner'], [])

        # Save show image links:
        try:
            if poster and len(poster) > 0:
                TvdbApi.SaveImageFile(poster[0], image_cache_dir, tvdbid + '.poster', log=None)
            if fanart and len(fanart) > 0:
                TvdbApi.SaveImageFile(fanart[0], image_cache_dir, tvdbid + '.fanart', log=None)
            if banner and len(banner) > 0:
                TvdbApi.SaveImageFile(banner[0], image_cache_dir, tvdbid + '.banner', log=None)
        except Exception, e:
            common.messageWindow(diag_title, 'ERROR Saving show images: ' + str(e))

    # Save actor images to cache:
    try:
        pass
        #actors = data.get('Actors', [])
        #actors = TvdbApi.CacheActorImages(actors, actor_cache_dir, force)
    except Exception, e:
        common.messageWindow(diag_title, 'ERROR Saving actor meta data: ' + str(e))

    if force:
        show_name = TvdbApi.getFromDict(data, ['Show', 'seriesName'], 'Unknown')
        title = TvdbApi.getFromDict(data, ['Details', 'episodeName'], 'Unknown')
        msg = u'{0}[CR]{1}[CR]Season: {2}  Epsiode: {3}[CR]TVdb: {4}'.format(show_name, title, season, episode, tvdbid)
        common.CreateNotification(header=diag_title, message=msg, icon=xbmcgui.NOTIFICATION_INFO, time=3000, sound=False)
    

# Clear image file cache.
def ClearImages():
    # Show images.
    path = image_cache_dir
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.lower().endswith(".jpg"):
                os.unlink(os.path.join(path, file))
        for file in os.listdir(path):
            if file.lower().endswith(".png"):
                os.unlink(os.path.join(path, file))
    # Actor images.
    path = actor_cache_dir
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.lower().endswith(".jpg"):
                os.unlink(os.path.join(path, file))
        for file in os.listdir(path):
            if file.lower().endswith(".png"):
                os.unlink(os.path.join(path, file))


# Clear episode meta data cache.
def ClearMetaData():
    path = ep_cache_dir
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
            CacheFromTvdb(tvdbid, season, episode, force=True)
            xbmc.executebuiltin('Container.Refresh')
        finally:
            xbmc.executebuiltin("Dialog.Close(busydialog)")
    
