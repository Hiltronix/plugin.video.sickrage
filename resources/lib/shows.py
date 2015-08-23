import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import sickbeard
import common
from metahandler import metahandlers


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get the tvdbid and show names.
def GetShowInfo(filter):
    shows = Sickbeard.GetShows()
    show_names = []
    for show in sorted(shows, key=lambda k: k['show_name'], reverse=False):
        name = show['show_name']
        tvdbid = show['tvdbid']
        paused = show['paused']
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
            if (filter == 'Continuing') and (status == 'Continuing'):
                show_names.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), Sickbeard.GetShowPoster(tvdbid), Sickbeard.GetShowFanArt(tvdbid), paused_msg])
            if (filter == 'Ended') and (status == 'Ended'):
                show_names.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), Sickbeard.GetShowPoster(tvdbid), Sickbeard.GetShowFanArt(tvdbid), paused_msg])
            if (filter == 'Paused') and (paused == 1):
                show_names.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), Sickbeard.GetShowPoster(tvdbid), Sickbeard.GetShowFanArt(tvdbid), paused_msg])
        else:
            show_names.append([name, '[COLOR gold]'+name+'[/COLOR]'+status_msg+ispaused, str(tvdbid), Sickbeard.GetShowPoster(tvdbid), Sickbeard.GetShowFanArt(tvdbid), paused_msg])
      
    return show_names


# Parse through shows and add dirs for each.
def menu(filter=''):
    show_info = GetShowInfo(filter)
    show_total = len(show_info)
    for show_name, name, tvdbid, thumbnail_path, fanart_path, paused in show_info:

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
        
        addShowDirectory(show_name, name, tvdbid, 4, thumbnail_path, fanart_path, show_total, context_menu_items)

    xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE)
    xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    common.CreateNotification(header='Show List', message=str(show_total)+' Shows in list', icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=False)


# Add directory item.
def addShowDirectory(show_name, name, tvdbid, menu_number, thumbnail_path, fanart_path, show_total, context_menu_items):
    return_url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(str(tvdbid))+"&mode="+str(menu_number)+"&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))
    list_item = xbmcgui.ListItem(name, thumbnailImage=thumbnail_path)
    list_item.setProperty('fanart_image', fanart_path) 
    meta = {}
    metaget = metahandlers.MetaData()
    try:
        meta = metaget.get_meta('tvshow', show_name, tvdbid, year='')
    except:
        pass
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_menu_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=show_total)  

