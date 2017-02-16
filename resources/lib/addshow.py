# New version of addshow.py that always the viewing of shows before selecting.

import xbmc
import xbmcgui
import xbmcplugin
import os
import sys
import json
import urllib
import cache
import common
import settings
import sickbeard
import TvdbApi


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


def showSearchDialog(show_name):
    keyboard = xbmc.Keyboard(show_name, 'Search for show on TheTVDB', False)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        text = keyboard.getText()
    else:
        text = ''
    return text  

  
# Search results selection window
def ShowSelectMenu(shows):
    formatted_shows = []
    for show in shows:
        try:
            show_name = u"" + show['name']
        except TypeError:
            continue
        try:
            first_aired = u"" + show['first_aired']
        except TypeError:
            first_aired = "Unknown"
        formatted_shows.append('[COLOR gold]' + show_name[:50] + '[/COLOR]    (' + first_aired + ')')
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Search Results", formatted_shows)
    return ret


# Add show main function. Shows the initial search window. 
def AddShow(show_name):
    #menu([{'name': 'Tiger Mom', 'tvdbid': '296279', 'first_aired': '2015-05-03'}])
    #return

    text = showSearchDialog(show_name)
    if (text == ''):
        exit()
    
    # Search for the show using SB search API.
    OK = True
    while OK:
        try:
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            search_results = Sickbeard.SearchShowName(urllib.quote_plus(text))
            if not search_results:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
                common.CreateNotification(header="Show Search", message="No results for that query.", icon=xbmcgui.NOTIFICATION_INFO, time=4000, sound=True)
                exit()
        finally:
            xbmc.executebuiltin("Dialog.Close(busydialog)")

        # Create dir list of possible shows to view and select from.
        selected_show = ShowSelectMenu(search_results)
        if (selected_show == -1):
            exit()

        tvdbid = str(search_results[selected_show]['tvdbid'])
        show_name = search_results[selected_show]['name']
        first_aired = search_results[selected_show]['first_aired']

        DisplayShow(tvdbid, show_name, first_aired)

        if common.selectNoYes('Add this show? [ {0} ]'.format(show_name[:25] + ' (' + first_aired + ')'), 'No', 'Yes') == 1:
            #ShowMessage('Selected Title', search_results[selected_show]['name'])
            AddShowDetails(tvdbid, show_name)
            exit()
        

def DisplayShow(tvdbid, show_name, first_aired):
# Show individual show info dialog.
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")

        cache.CacheFromTvdb(tvdbid, 1, 1, force=False)
    
        image_cache_dir = cache.image_cache_dir
        thumbnail_path = image_cache_dir + tvdbid + '.poster.jpg'
        fanart_path = image_cache_dir + tvdbid + '.fanart.jpg'
        banner_path = image_cache_dir + tvdbid + '.banner.jpg'
    
        list_item = xbmcgui.ListItem(show_name, thumbnailImage=thumbnail_path)
        list_item.setArt({'icon': thumbnail_path, 'thumb': thumbnail_path, 'poster': thumbnail_path, 'fanart': fanart_path, 'banner': banner_path, 'clearart': '', 'clearlogo': '', 'landscape': ''})
        list_item.setProperty('LibraryHasMovie', '0')  # Removes the "Play" button from the video info screen, and replaces it with "Browse".
        meta = {}
        season = 1
        episode = 1
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
            meta['title'] = show_name # This is what is displayed at the top of the video dialog window.
            meta['originaltitle'] = TvdbApi.getFromDict(data, ['Details', 'episodeName'], show_name)
            meta['tvdb_id'] = str(tvdbid)
            meta['imdbnumber'] = TvdbApi.getFromDict(data, ['Show', 'imdbId'], '')
            meta['overlay'] = 6
            meta['plot'] = TvdbApi.getFromDict(data, ['Show', 'overview'], '')
            list_item.setRating('tvdb', TvdbApi.getFromDict(data, ['Show', 'siteRating'], 0), TvdbApi.getFromDict(data, ['Show', 'siteRatingCount'], 0), True)
            meta['premiered'] = TvdbApi.getFromDict(data, ['Show', 'firstAired'], first_aired)
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
            actors = data.get('Actors', [])
            actors = TvdbApi.CacheActorImages(actors, cache.actor_cache_dir)
            for value in TvdbApi.getFromDict(data, ['Details', 'guestStars'], ''):
                actors.append(dict({'name': value, 'role': 'Guest Star'}))
            if actors:
                list_item.setCast(actors)
        except:
            meta['tvdb_id'] = str(tvdbid)
            meta['tvshowtitle'] = show_name
            meta['title'] = show_name
        list_item.setInfo(type="Video", infoLabels=meta)

    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")

    dialog = xbmcgui.Dialog()
    ret = dialog.info(list_item)


def AddShowDetails(tvdbid, show_name):
    
    print 'Selected Add Show: ' + show_name + ' ' + tvdbid

    # Check if show already exists in the show list.
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        shows = Sickbeard.GetShows()
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    for show in shows:
        if show_name == show['show_name']:
            header = 'Duplicate Show'
            msg = "'" + show_name + "' already exists in your show list."
            ShowMessage(header, msg)
            print header + ': ' + msg
            return

    # "Pick the parent folder" prompt.
    root_dir = SelectRootDirMessage()
    if (root_dir == -1):
        return
        
    print 'Add Show Root Dir: ' + root_dir

    # sb.getdefaults for status of show eps.  Need to make each option selectable so you can change initial status, folders, quality.
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        default_status, default_folders, default_quality = Sickbeard.GetDefaults()
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        
    print 'Add Show Retrieved Defaults'
    
    # Set status for previously aired episodes.
    prev_aired_status = SetStatus("Set Status for Previously Aired Episodes", default_status)
    if (prev_aired_status == -1):
        return
        
    print 'Add Show Set Prev Status: ' + str(prev_aired_status)

    # Set status for future episodes.
    future_status = ''
    if (settings.__servertype__ == "SickRage"):
        future_status = SetStatus("Set Status for Upcoming Episodes", "wanted")
        if (future_status == -1):
            return

    print 'Add Show Set Future Status: ' + str(future_status)

    # "Use season folders?" prompt.
    flatten_folders = SetFlattenFolders(default_folders)
    if (flatten_folders == -1):
        return

    print 'Add Show Set Season Folders: ' + str(flatten_folders)

    # "Set initial status of episodes" prompt.
    quality = SetQualityMessage(default_quality)
    if (quality == -1):
        return
  
    print 'Add Show Set Quality: ' + str(quality)

    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        ret = Sickbeard.AddNewShow(tvdbid, root_dir, prev_aired_status, future_status, flatten_folders, quality)
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    header = 'Add Show'
    if ret == 'success':
        msg = 'Successfully added {0}'.format(show_name)
        ShowMessage(header, msg)
        print header + ': ' + msg
    else:
        ShowMessage(header, msg)
        msg = 'Failed to add {0}'.format(show_name)
        print header + ': ' + msg


# Basic show message window
def ShowMessage(header, text):
    dialog = xbmcgui.Dialog()
    dialog.ok(header, text)


# Gets the root dirs from SB then shows selection window
def SelectRootDirMessage():
    directory_result = Sickbeard.GetRootDirs()
    directories = []
    for location in directory_result:
        directories.append(location['location'])
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Select Parent Folder", directories)
    if (ret == -1):
        return ret
    else:
        return directories[ret]


# Set Status for previously aired episodes.
def SetStatus(title, status):
    org_list = ["wanted", "skipped", "archived", "ignored"]
    status_list = list(org_list)  # Make a copy of the list to alter for the menu.
    for each in status_list:
        if each == status:
            index = status_list.index(status)
            status_list[index] = status + " (Default)"
    dialog = xbmcgui.Dialog()
    ret = dialog.select(title, status_list)
    if (ret == -1):
        return ret
    else:
        return org_list[ret]


# Use season folders selection window
def SetFlattenFolders(flatten_folders):
    if flatten_folders == 1:
        list = ["Yes (no season folders)", "No (episodes folder-grouped by season)"]
    else:
        list = ["Grouped Seasons in Sep. Folders", "All Shows in the Same Folder"]
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Group Seasons (Flatten Files Option)", list)
    if (ret == -1):
        return ret
    elif (ret == 0):
        if flatten_folders == 1:
            return True
        else:
            return False
    elif (ret == 1):
        if flatten_folders == 1:
            return False
        else:
            return True
  

# Set initial episode quality window
def SetQualityMessage(quality):
    anyList = [u'sdtv', u'sddvd', u'hdtv', u'fullhdtv', u'hdwebdl', u'fullhdwebdl', u'hdbluray', u'fullhdbluray', u'unknown']
    sdList = [u'sdtv', u'sddvd']
    hdList = [u'hdtv', u'fullhdtv', u'hdwebdl', u'fullhdwebdl', u'hdbluray', u'fullhdbluray']
    if all(x in quality for x in anyList):
        quality_list = ["Any (Default)", "SD", "HD"]
    elif all(x in quality for x in sdList):
        quality_list = ["Any", "SD (Default)", "HD"]
    else:
        quality_list = ["Any", "SD", "HD (Default)"]
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Preferred Quality of Episodes to be Downloaded", quality_list)
    if (ret == -1):
        return ret
    if (ret == 0):
        return 'sdtv|sddvd|hdtv|rawhdtv|fullhdtv|hdwebdl|fullhdwebdl|hdbluray|fullhdbluray|unknown'
    elif (ret == 1):
        return 'sdtv|sddvd'
    else:
        return 'hdtv|rawhdtv|fullhdtv|hdwebdl|fullhdwebdl|hdbluray|fullhdbluray'


if __name__ == '__main__':
    AddShow("")
    xbmc.executebuiltin("Container.Refresh")

