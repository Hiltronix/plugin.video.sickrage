import sickbeard
import sys
import urllib
import xbmcplugin
import xbmcgui
import xbmc
from metahandler import metahandlers


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get the tvdbid and show names.
def GetShowInfo():
    show_ids = Sickbeard.GetShowIds()
    show_info = Sickbeard.GetShowInfo(show_ids)

    show_names = []
    for name, info in sorted(show_info.iteritems()):
      tvdbid, paused, status = info
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
        context_menu_items = [('Show Info', 'XBMC.Action(Info)'),\
                              ('Add New Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/addshow.py, new)'),\
                              ('Delete Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/deleteshow.py, '+tvdbid+', '+show_name+')'),\
                              ('Force Update', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/forcesearch.py, '+tvdbid+')'),\
                              (paused+' Show', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/setpausestate.py, '+paused+', '+tvdbid+')'),\
                              ('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'),\
                              ('Go Back', 'XBMC.Action(back)')]
        addShowDirectory(show_name, name, tvdbid, 4, thumbnail_path, show_total, context_menu_items)


# Add directory item.
def addShowDirectory(show_name, name, tvdbid, menu_number, thumbnail_path, show_total, context_menu_items):
    return_url = sys.argv[0]+"?url="+urllib.quote_plus(str(tvdbid))+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(show_name.encode( "utf-8" ))
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

