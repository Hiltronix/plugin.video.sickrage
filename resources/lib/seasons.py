import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import sys
import urllib
import sickbeard


# Initialize Sickbeard Class.
Sickbeard = sickbeard.SB()


# Get season number list.
def GetSeasons(tvdbid, show_name):
    list = Sickbeard.GetSeasonNumberList(tvdbid)
    if not list:
        exit()
    
    for season_number in list:
      if season_number == 0:
        list[list.index(season_number)] = [0, '[COLOR gold]Extras[/COLOR] - ' + show_name]
      else:
        list[list.index(season_number)] = [season_number, '[COLOR gold]Season ' + str(season_number) + '[/COLOR] - ' + show_name]
    return list


# Add directory items for each season number.
def menu(handle, tvdbid, show_name):
    list = GetSeasons(tvdbid, show_name)
    total_items = len(list)
    
    context_items = []
    context_items.append(('Refresh List', 'XBMC.Container.Refresh'))
    context_items.append(('Go Back', 'XBMC.Action(back)'))

    for season_number, season_text in list:
        thumbnail_path = Sickbeard.GetShowPoster(tvdbid)
        fanart_path = Sickbeard.GetShowFanArt(tvdbid)
        banner_path = Sickbeard.GetShowBanner(tvdbid)
        addDirectory(handle, show_name, season_number, season_text, tvdbid, thumbnail_path, fanart_path, banner_path, total_items, context_items)

    xbmcplugin.setContent(handle=int(handle), content='tvshows')
    xbmcplugin.endOfDirectory(int(handle))

      
# Add season directory items.
def addDirectory(handle, show_name, season_number, season_text, tvdbid, thumbnail_path, fanart_path, banner_path, total_items, context_items):
    return_url = sys.argv[0]+"?tvdb_id="+urllib.quote_plus(tvdbid)+"&mode=5&show_name="+urllib.quote_plus(show_name.encode( "utf-8" ))+"&number="+urllib.quote_plus(str(season_number))
    list_item = xbmcgui.ListItem(season_text)
    list_item.setArt({'icon': thumbnail_path, 'thumb': thumbnail_path, 'poster': thumbnail_path, 'fanart': fanart_path, 'banner': banner_path, 'clearart': '', 'clearlogo': '', 'landscape': ''})
    meta = {}
    meta['plot'] = '{0} [CR]Season {1}'.format(show_name, season_number)
    list_item.setInfo(type="Video", infoLabels=meta)
    list_item.addContextMenuItems(context_items, replaceItems = True)
    xbmcplugin.addDirectoryItem(handle=int(handle), url=return_url, listitem=list_item, isFolder=True, totalItems=total_items)

