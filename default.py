import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import os
import sys
import urllib
import resources.lib.cache as cache
import resources.lib.common as common
import resources.lib.settings as settings
import resources.lib.upcoming as upcoming
import resources.lib.history as history
import resources.lib.seasons as seasons
import resources.lib.show_filter as show_filter
import resources.lib.shows as shows
import resources.lib.addTvdbShow as addshow
import resources.lib.episodes as episodes
import resources.lib.backlog as backlog
import resources.lib.log as log
import resources.lib.sickbeard as sickbeard
import resources.lib.TvdbApi as TvdbApi


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Add the main directory folders.
def mainMenu():
    total_items = 6
    addDirectory('Upcoming - 1 Week', 2, True, settings.addon_path + '/upcoming.png', total_items)
    addDirectory('Upcoming - Extended', 22, True, settings.addon_path + '/upcomingplus.png', total_items)
    addDirectory('History', 3, True, settings.addon_path + '/history.png', total_items)
    if (settings.__servertype__ == "SickRage"):
        total_items += 1
        addDirectory('Backlog', 9, True, settings.addon_path + '/backlog.png', total_items)
    addDirectory('Show List', 1, True, settings.addon_path + '/manage.png', total_items)
    addDirectory('Add New Show', 7, False, settings.addon_path + '/add.png', total_items)
    addDirectory('Settings', 11, False, settings.addon_path + '/settings.png', total_items)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


# Add directory item.
def addDirectory(menu_item_name, menu_number, folder, icon, total_items):
    return_url = 'plugin://{}/?mode={}&name={}'.format(settings.pluginID, menu_number, urllib.quote_plus(menu_item_name))
    list_item = xbmcgui.ListItem(menu_item_name)
    list_item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': '', 'banner': '', 'clearart': '', 'clearlogo': '', 'landscape': ''})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=folder, totalItems=total_items)


# Get the parameters from the URL supplied as an arg to this script.
def getParameters():
    param=[]
    try:
      paramstring=sys.argv[2]
      if len(paramstring)>=2:
              params=sys.argv[2]
              cleanedparams=params.replace('?','')
              if (params[len(params)-1]=='/'):
                      params=params[0:len(params)-2]
              pairsofparams=cleanedparams.split('&')
              param={}
              for i in range(len(pairsofparams)):
                      splitparams={}
                      splitparams=pairsofparams[i].split('=')
                      if (len(splitparams))==2:
                              param[splitparams[0]]=splitparams[1]
      return param
    except:
      return param
          
          
# Initialize URL parameters.
url = None
name = None
number = None
menu_number = None
action = None
show_name = None
show_id = None
tvdb_id = None
season = 0
episode = 0
params = getParameters()

# Parse internal URL.
try:
    url = urllib.unquote_plus(params["url"])
    print url
except:
    pass

try:
    name = urllib.unquote_plus(params["name"])
    print name
except:
    pass

try:
    number = urllib.unquote_plus(params["number"])
    print number
except:
    pass

try:
    menu_number = int(params["mode"])
    print menu_number
except:
    pass
    
try:
    show_name = urllib.unquote_plus(params["title"])
    menu_number = 7
    print show_name
except:
    pass

try:
    action = urllib.unquote_plus(params["action"])
    menu_number = 8
    print action
except:
    pass

try:
    show_name = urllib.unquote_plus(params["show_name"]).decode('utf-8')
    print show_name
except:
    pass

try:
    tvdb_id = urllib.unquote_plus(params["tvdb_id"])
    print tvdb_id
except:
    pass

try:
    tvdb_id = urllib.unquote_plus(params["show_id"])    # Used by ExtendedInfo.
    print tvdb_id
except:
    pass

try:
    season = urllib.unquote_plus(params["season"])
    print season
except:
    pass

try:
    episode = urllib.unquote_plus(params["episode"])
    print episode
except:
    pass

# Open directories based on selection.
if menu_number == None:
    mainMenu()
       
elif menu_number == 1:  # Show list type [All, Continuing, Ended, Paused].
    show_filter.menu(sys.argv[1])
        
elif menu_number == 14: # Shows list.
    shows.menu(handle=sys.argv[1], filter=name)
        
elif menu_number == 2:  # Upcoming 1 Week.
    upcoming.menu(sys.argv[1], False)
        
elif menu_number == 22:   # Upcoming Extended.
    upcoming.menu(sys.argv[1], True)
        
elif menu_number == 3:  # History list.
    history.menu(sys.argv[1])

elif menu_number == 4:  # Seasons.
    seasons.menu(sys.argv[1], tvdb_id, show_name)

elif menu_number == 5:  # Episodes.
    episodes.menu(sys.argv[1], tvdb_id, show_name, number)

elif menu_number == 6:  # Open the video dialog window.
    xbmc.executebuiltin('XBMC.Action(Info)')
    
elif menu_number == 7:  # Add a new show.
    addshow.AddShow(show_name)

elif menu_number == 8:  # Action values.
    if action == 'addshow':  # Add a new show based on show name.  Used by the Manage section of ExtendedInfo.
        if tvdb_id:
            # Use tvdb_id to get show_name to pass as argument for user confirmation.
            try:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                show_name = TvdbApi.GetNameFromTvdb(tvdb_id)
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
            addshow.AddShowDetails(tvdb_id, show_name)
        else:
            common.messageWindow('Missing Parameter', 'Add new show request received,[CR]but the TVdb ID was not included.')

elif menu_number == 9:  # Backlog list.
    backlog.menu(sys.argv[1])

# Settings menu.
elif menu_number == 11:
    ret = 0
    while ret >= 0:
        dialog = xbmcgui.Dialog()
        ret = dialog.select("Settings", ["Add-on Settings", "Run Post Processing", "Add Add-on to Favouties", "Check if All Episodes are Cached", "Clear Cache", "Show Server Version", "View Server Log File", "Change Log", "About"])
    
        if ret == 0:    # App Settings (Kodi settings.)
            xbmc.executebuiltin('XBMC.Addon.OpenSettings({0})'.format(settings.pluginID))
            ret = -1    # Exit Settings menu so Kodi App Settings can be on top.
    
        if ret == 1:    # Run Post Processing.
            try:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                msg, res = Sickbeard.PostProcessing()
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
            if res:
                common.messageWindow('Post Processing', 'Msg: {}[CR]Result: {}'.format(msg, res))
    
        if ret == 2:    # Add App to Favourites.
            try:
                xml_open = '<favourites>\n'
                xml_fav = '    <favourite name="{0}" thumb="special://home/addons/{1}/icon.png">ActivateWindow(10025,&quot;plugin://{1}/&quot;,return)</favourite>\n'.format(settings.pluginName, settings.pluginID)
                xml_close = '</favourites>\n'
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                filename = xbmc.translatePath('special://home/userdata/favourites.xml')
                if os.path.isfile(filename):
                    with open(filename, 'r') as f:
                        data = f.read()
                    # Check is fav already exists.  If not, add it to end of file.
                    find_str = 'name="{}"'.format(settings.pluginName)
                    if find_str not in data:
                        data = data.replace(xml_close, xml_fav + xml_close)
                else:
                    data = xml_open + xml_fav + xml_close
                # Save favourites file.
                f = open(filename, 'w')
                f.write(data)
                f.close()
                common.messageWindow('Add to Favourites', 'Done.')
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
    
        if ret == 3:    # Check Cache for All Episodes.
            try:
                if settings.my_addon.getSetting('TVdbUpdateAllEpisodesEnabled') == 'true':
                    if settings.my_addon.getSetting('TVdbUpdateAllEpisodesRunning') == 'false':
                        state = '[COLOR cyan]Scheduled[/COLOR]'
                    else:
                        state = '[COLOR gold]Active[/COLOR]'
                    if common.DialogYesNo('Check Cache For All Episodes', text='Operation: {}[CR]Progress: [COLOR gold]{}%[/COLOR][CR][CR][COLOR grey](Re-open this dialog to see updated progress.)[/COLOR]'.format(state, settings.my_addon.getSetting('TVdbUpdateAllEpisodesProgress')), noLabel='Close', yesLabel='Cancel Operation'):
                        # Set flags to turn service operation off.
                        settings.my_addon.setSetting('TVdbUpdateAllEpisodesEnabled', 'false')
                        settings.my_addon.setSetting('TVdbUpdateAllEpisodesRunning', 'false')
                        settings.my_addon.setSetting('TVdbUpdateAllEpisodesProgress', '0')
                else:
                    if common.DialogYesNo('Check Cache For All Episodes  [Not Running]', u'{0} This background operation may take some time to complete.[CR]{0} If Kodi is shutdown before completion, you will have to manually select this setting again.[CR]{0} You can check progress by revisiting this selection.'.format(u'[COLOR cyan]\u2022[/COLOR]'), noLabel='Close', yesLabel='Start'):
                        # Set flags to turn service operation on at next interval.
                        settings.my_addon.setSetting('TVdbUpdateAllEpisodesEnabled', 'true')
                        settings.my_addon.setSetting('TVdbUpdateAllEpisodesRunning', 'false')
                        settings.my_addon.setSetting('TVdbUpdateAllEpisodesProgress', '0')
            finally:
                pass
                
    
        if ret == 4:    # Clear Cache.
            try:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                size = common.GetDirSizeFormatted(settings.cache_dir)
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
            if common.DialogYesNo('Clear Cached Images and Meta Data?', u'Cache storage is using: [COLOR gold]{0}[/COLOR]'.format(size), noLabel='Close', yesLabel='Clear Cache'):
            #if common.selectNoYes('Clear cached images and meta data?  [{0}]'.format(size), 'No', 'Yes') == 1:
                try:
                    xbmc.executebuiltin("ActivateWindow(busydialog)")
                    cache.ClearImages()
                    cache.ClearMetaData()
                finally:
                    xbmc.executebuiltin("Dialog.Close(busydialog)")
                common.CreateNotification(header='Image Cache', message='Cleared', icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)
    
        if ret == 5:    # SickRage/SickBeard Version.
            api, version = Sickbeard.GetVersion()
            common.messageWindow('Server Version', 'API Version: {0}[CR]Version: {1}'.format(api, version))
    
        if ret == 6:    # View log files.
            log.main()
    
        if ret == 7:    # Change log.
            try:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                filename = os.path.join(settings.addon_path, 'changelog.txt')
                if os.path.isfile(filename):
                    with open(filename, 'r') as f:
                        data = f.read()
                else:
                    data = 'Change log not available.'
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
            w = common.TextViewer_Dialog('DialogTextViewer.xml', settings.addon_path, header='Change Log', text=data)
            w.doModal()
    
        if ret == 8:    # About.
            try:
                xbmc.executebuiltin("ActivateWindow(busydialog)")
                filename = os.path.join(settings.addon_path, 'about.txt')
                if os.path.isfile(filename):
                    with open(filename, 'r') as f:
                        data = f.read()
                else:
                    data = 'About file not available.'
                data = '[COLOR gold]{} v.{}[CR]by {}[/COLOR][CR][COLOR cyan]{}[CR]{}[/COLOR][CR][CR]'.format(settings.pluginName, settings.pluginVersion, settings.pluginAuthor, settings.pluginSummary, settings.pluginDesc) + data
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
            w = common.TextViewer_Dialog('DialogTextViewer.xml', settings.addon_path, header='About', text=data)
            w.doModal()
    

# Update a show's images.
elif menu_number == 13:
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        # Update Poster image.
        Sickbeard.GetShowPoster(tvdb_id, update=True)
        # Update Fanart image.
        Sickbeard.GetShowFanArt(tvdb_id, update=True)
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    common.CreateNotification(header='Updated Cached Images for', message=show_name, icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)
    xbmc.executebuiltin('Container.Refresh')

# Open the TV show folder (to select a video to watch.)
elif menu_number == 15:
    try:
        data = common.JsonRpc('libTvShows', 'VideoLibrary.GetTVShows', {"properties": ["imdbnumber", "title", "year"], "sort": {"order": "ascending", "method": "title"}})
        shows = common.getFromDict(data,['result', 'tvshows'], [])
        tvshowid = None
        for show in shows:
            if show.get('imdbnumber') == str(tvdb_id):
                tvshowid = show.get('tvshowid')
                break
        if tvshowid:
            xbmc.executebuiltin('ActivateWindow(videos,videodb://tvshows/titles/{0}/, True)'.format(tvshowid))
    except Exception, e:
        common.messageWindow('Open Show Folder Error', str(e))
        print e
    
