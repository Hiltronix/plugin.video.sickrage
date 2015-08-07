import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import sickbeard


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get season number list.
def GetSeasons(tvdbid):
    season_list = Sickbeard.GetSeasonNumberList(tvdbid)
    
    for season_number in season_list:
      if season_number == 0:
        season_list[season_list.index(season_number)] = [0, "Extras"]
      else:
        season_list[season_list.index(season_number)] = [season_number, "Season "+str(season_number)]
    return season_list


# Add directory items for each season number.
def menu(tvdbid, show_name):
    season_list = GetSeasons(tvdbid)
    season_total = len(season_list)
    
    context_menu_items = []
    context_menu_items.append(('Refresh List', 'XBMC.RunScript(special://home/addons/plugin.video.sickrage/resources/lib/refresh.py)'))
    if xbmc.getCondVisibility('System.HasAddon(context.videolookup.dialog)'):
        context_menu_items.append(('Video Lookup', 'XBMC.RunScript(context.videolookup.dialog)'))
    context_menu_items.append(('Go Back', 'XBMC.Action(back)'))

    for season_number, season_text in season_list:
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        addSeasonDirectory(show_name, season_number, season_text, tvdbid, 5, thumbnail_path, season_total, context_menu_items)

      
# Add season directory items.
def addSeasonDirectory(show_name, season_number, season_text, tvdbid, menu_number, thumbnail_path, season_total, context_items):
    return_url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(tvdbid)+"&mode="+str(menu_number)+"&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))+"&number="+urllib.quote_plus(str(season_number))
    list_item = xbmcgui.ListItem(season_text, thumbnailImage=thumbnail_path)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=True, totalItems=season_total)

