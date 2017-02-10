import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import os
import sys
import urllib
import resources.lib.common as common
import resources.lib.settings as settings
import resources.lib.upcoming as upcoming
import resources.lib.history as history
import resources.lib.seasons as seasons
import resources.lib.show_filter as show_filter
import resources.lib.shows as shows
import resources.lib.addshow as addshow
import resources.lib.episodes as episodes
import resources.lib.backlog as backlog
import resources.lib.log as log
import resources.lib.sickbeard as sickbeard


my_addon = xbmcaddon.Addon('plugin.video.sickrage')

# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Add the main directory folders.
def mainMenu():
    total_items = 5
    addDirectory('Upcoming - 1 Week', 2, True, my_addon.getAddonInfo('path')+'/upcoming.png', my_addon.getAddonInfo('path')+'/resources/images/upcoming_thn.png', total_items)
    addDirectory('Upcoming - Extended', 22, True, my_addon.getAddonInfo('path')+'/upcoming.png', my_addon.getAddonInfo('path')+'/resources/images/upcoming_thn.png', total_items)
    addDirectory('History', 3, True, my_addon.getAddonInfo('path')+'/history.png', my_addon.getAddonInfo('path')+'/resources/images/history_thn.png', total_items)
    if (settings.__servertype__ == "SickRage"):
        total_items += 1
        addDirectory('Backlog', 9, True, my_addon.getAddonInfo('path')+'/backlog.png', my_addon.getAddonInfo('path')+'/resources/images/backlog_thn.png', total_items)
    addDirectory('Show List', 1, True, my_addon.getAddonInfo('path')+'/manage.png', my_addon.getAddonInfo('path')+'/resources/images/manage_thn.png', total_items)
    addDirectory('Add New Show', 7, False, my_addon.getAddonInfo('path')+'/add.png', my_addon.getAddonInfo('path')+'/resources/images/add_thn.png', total_items)
    if (settings.__show_log__ == "true"):
        total_items += 1
        addDirectory('View Log File', 11, False, my_addon.getAddonInfo('path')+'/log.png', my_addon.getAddonInfo('path')+'/resources/images/log_thn.png', total_items)
    if (settings.__show_clearcache__ == "true"):
        total_items += 1
        addDirectory('Clear Cached Data', 12, False, my_addon.getAddonInfo('path')+'/settings.png', my_addon.getAddonInfo('path')+'/resources/images/settings_thn.png', total_items)


# Add directory item.
def addDirectory(menu_item_name, menu_number, folder, icon, thumbnail, total_items):
    return_url = sys.argv[0]+"?url="+urllib.quote_plus("")+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(menu_item_name)
    list_item = xbmcgui.ListItem(menu_item_name, iconImage=thumbnail, thumbnailImage=icon)
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
menu_number = None
action = None
show_name = None
tvdb_id = None
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

# Open directories based on selection.
if menu_number == None:
    mainMenu()
       
elif menu_number == 1:
    show_filter.menu()
        
elif menu_number == 14:
    shows.menu(filter=name)
        
elif menu_number == 2:  # Upcoming 1 Week.
    upcoming.menu(False)
        
elif menu_number == 22:   # Upcoming Extended.
    upcoming.menu(True)
        
elif menu_number == 3:
    history.menu()

elif menu_number == 4:
    seasons.menu(tvdb_id, show_name)

elif menu_number == 5:
    episodes.menu(tvdb_id, show_name, number)

elif menu_number == 6:
    xbmc.executebuiltin('XBMC.Action(Info)')

elif menu_number == 7:
    addshow.AddShow(show_name)

elif menu_number == 8:
    if (action == 'addshow'):
        if show_name:
            addshow.AddShow(show_name)
        elif tvdb_id:
            # Convert tvdb_id to show_name so we can do a normal show lookup and user select confirmation.
            xbmc.executebuiltin("ActivateWindow(busydialog)")
            show_info = []
            try:
                show_info,total = Sickbeard.GetShowDetails(tvdb_id)
            finally:
                xbmc.executebuiltin("Dialog.Close(busydialog)")
            show_name = show_info['show_name']
            addshow.AddShow(show_name)

elif menu_number == 9:
    backlog.menu()
        
# ExtendedInfo Script optional TV Show lookup feature.
elif menu_number == 10:
    if xbmc.getCondVisibility('System.HasAddon(script.extendedinfo)'):
        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedtvinfo,tvdb_id=%s)' %(tvdb_id))
    else:
        settings.messageWindow('Feature Not Available', 'The optional add-on for this feature has not been installed.\nTo Install Goto: System > Add-ons> Install from Repo > Kodi Add-on Repo > Program Add-ons > ExtendedInfo Script')
                
# View log file.
elif menu_number == 11:
    log.main()

# Clear the image cache.
elif menu_number == 12:
    size = common.GetDirSizeFormatted(xbmc.translatePath('special://temp/sb/cache/'))
    if common.selectNoYes('Clear cached images and meta data?  [{0}]'.format(size), 'No', 'Yes') == 1:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        try:
            Sickbeard.ClearImageCache()
            Sickbeard.ClearMetaDataCache()
        finally:
            xbmc.executebuiltin("Dialog.Close(busydialog)")
        common.CreateNotification(header='Image Cache', message='Cleared', icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)

# Update a show's images.
elif menu_number == 13:
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        # Update Poster image.
        Sickbeard.GetShowPoster(tvdb_id, update=True)
        # Update Fanart image.
        Sickbeard.GetShowFanArt(tvdb_id, update=True)
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    common.CreateNotification(header='Updated Cached Images for', message=show_name, icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)
    xbmc.executebuiltin('Container.Refresh')

xbmcplugin.endOfDirectory(int(sys.argv[1]))

