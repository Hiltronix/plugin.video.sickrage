import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import sickbeard
from metahandler import metahandlers


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get the tvdbid and show names.
def GetShowInfo():
    shows = Sickbeard.GetShows()
    show_names = []
    for show in sorted(shows, key=lambda k: k['show_name'], reverse=False):
        name = show['show_name']
        tvdbid = show['tvdbid']
        paused = show['paused']
        status = show['status']
        if paused == 0:
            paused = "Pause"
            ispaused = ""
        else:
            paused = "Resume"
            ispaused = "    [COLOR cyan]Paused[/COLOR]"
        if (status == 'Ended'):
            status = '    [COLOR red]'+status+'[/COLOR]'
        else:
            status = '    [COLOR gray]'+status+'[/COLOR]'
        show_names.append([name, '[COLOR gold]'+name+'[/COLOR]'+status+ispaused, str(tvdbid), Sickbeard.GetShowPoster(tvdbid), paused])
      
    return show_names


# Parse through shows and add dirs for each.
def menu():
    show_info = GetShowInfo()
    show_total = len(show_info)
    for show_name, name, tvdbid, thumbnail_path, paused in show_info:

        context_menu_items = []
        context_menu_items.append(('Show Info', 'XBMC.Action(Info)'))
        context_menu_items.append(('ExtendedInfo', 'XBMC.RunPlugin(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=10&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Episode List', 'XBMC.Container.Update(plugin://plugin.video.sickrage?tvdb_id='+urllib.quote_plus(str(tvdbid))+'&mode=4&show_name='+urllib.quote_plus(show_name.encode( "utf-8" ))+')'))
        context_menu_items.append(('Add New Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/addshow.py, new)'))
        context_menu_items.append(('Delete Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/deleteshow.py, '+tvdbid+', '+show_name+')'))
        context_menu_items.append(('Force Update', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/forcesearch.py, '+tvdbid+')'))
        context_menu_items.append((paused+' Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setpausestate.py, '+paused+', '+tvdbid+')'))
        if xbmc.getCondVisibility('System.HasAddon(context.videolookup.dialog)'):
            context_menu_items.append(('Video Lookup', 'XBMC.RunScript(context.videolookup.dialog)'))
        context_menu_items.append(('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'))
        context_menu_items.append(('Go Back', 'XBMC.Action(back)'))
        
        addShowDirectory(show_name, name, tvdbid, 4, thumbnail_path, show_total, context_menu_items)


# Add directory item.
def addShowDirectory(show_name, name, tvdbid, menu_number, thumbnail_path, show_total, context_menu_items):
    return_url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode="+str(menu_number)+"&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(name, thumbnailImage=thumbnail_path)
    meta = {}
    metaget = metahandlers.MetaData()
    try:
        meta = metaget.get_meta('tvshow', show_name, tvdbid, year='')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_menu_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=show_total)  

