import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import urllib
import shows


my_addon = xbmcaddon.Addon('plugin.video.sickrage')


def menu():
    total_items = 4
    addDirectory('All', 14, True, my_addon.getAddonInfo('path')+'/manage.png', total_items)
    addDirectory('Continuing', 14, True, my_addon.getAddonInfo('path')+'/manage.png', total_items)
    addDirectory('Ended', 14, True, my_addon.getAddonInfo('path')+'/manage.png', total_items)
    addDirectory('Paused', 14, True, my_addon.getAddonInfo('path')+'/manage.png', total_items)

      
def addDirectory(menu_item_name, menu_number, folder, icon, total_items):
    return_url = sys.argv[0]+"?url="+urllib.quote_plus("")+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(menu_item_name)
    list_item = xbmcgui.ListItem(menu_item_name)
    list_item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': '', 'banner': '', 'clearart': '', 'clearlogo': '', 'landscape': ''})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=folder, totalItems=total_items)

