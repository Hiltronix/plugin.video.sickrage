import xbmc
import xbmcgui
import xbmcaddon
import os
import sys
import json
import common
import settings
import TvdbApi


my_addon = xbmcaddon.Addon('plugin.video.sickrage')

tvdbid = sys.argv[1]
season = sys.argv[2]
episode = sys.argv[3]

diag_title = 'Update from TVdb'

ep_cache_dir = xbmc.translatePath('special://temp/sb/cache/episodes/')
image_cache_dir = xbmc.translatePath('special://temp/sb/cache/images/')
actor_cache_dir = xbmc.translatePath('special://temp/sb/cache/actors/')
json_file = os.path.join(ep_cache_dir, tvdbid + '-' + str(season) + '-' + str(episode) + '.json')

xbmc.executebuiltin("ActivateWindow(busydialog)")

# Get show meta data:
try:
    data = TvdbApi.GetMetaDataDict(tvdbid, int(season), int(episode), '', log=None)
except Exception, e:
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    settings.errorWindow(diag_title, 'ERROR Retrieving show meta data: ' + str(e))

# Save show meta data as json file to cache:
try:
    with open(json_file, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
except Exception, e:
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    settings.errorWindow(diag_title, 'ERROR Saving show meta data: ' + str(e))

# Get show images links:
try:
    tvdb = TvdbApi.theTVDB()
    poster = tvdb.GetImageLinks(series_id=tvdbid, img_type='poster', thumbnail=False, log=None)
    fanart = tvdb.GetImageLinks(series_id=tvdbid, img_type='fanart', thumbnail=False, log=None)
    banner = tvdb.GetImageLinks(series_id=tvdbid, img_type='series', thumbnail=False, log=None)
except Exception, e:
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    settings.errorWindow(diag_title, 'ERROR Retrieving show images: ' + str(e))

# Save show image links:
try:
    if poster and len(poster) > 0:
        try:
            TvdbApi.SaveImageFile(poster[0], image_cache_dir, tvdbid + '.poster', log=None)
        except Exception, e:
            raise 'Poster: {0}'.format(e)
    if fanart and len(fanart) > 0:
        try:
            TvdbApi.SaveImageFile(fanart[0], image_cache_dir, tvdbid + '.fanart', log=None)
        except Exception, e:
            raise 'Fanart: {0}'.format(e)
    if banner and len(banner) > 0:
        try:
            TvdbApi.SaveImageFile(banner[0], image_cache_dir, tvdbid + '.banner', log=None)
        except Exception, e:
            raise 'Banner: {0}'.format(e)
except Exception, e:
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    settings.errorWindow(diag_title, 'ERROR Saving show images: ' + str(e))

# Save actor images to cache:
try:
    actors = data.get('Actors', '')
    actors = TvdbApi.CacheActorImages(actors, actor_cache_dir)
except Exception, e:
    xbmc.executebuiltin("Dialog.Close(busydialog)")
    settings.errorWindow(diag_title, 'ERROR Saving actor meta data: ' + str(e))

show_name = TvdbApi.getFromDict(data, ['Show', 'seriesName'], 'Unknown')
title = TvdbApi.getFromDict(data, ['Details', 'episodeName'], 'Unknown')

xbmc.executebuiltin("Dialog.Close(busydialog)")

xbmc.executebuiltin('Container.Refresh')

msg = '{0}[CR]{1}[CR]Season: {2}  Epsiode: {3}[CR]TVdb: {4}'.format(show_name, title, season, episode, tvdbid)
common.CreateNotification(header=diag_title, message=msg, icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)
#common.messageWindow(diag_title, msg)

