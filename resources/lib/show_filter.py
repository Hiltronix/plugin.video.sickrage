import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import sys
import urllib
import shows


pluginID = 'plugin.video.sickrage'
my_addon = xbmcaddon.Addon(pluginID)
addon_path = my_addon.getAddonInfo('path')


def menu(handle):
    total_items = 4
    addDirectory(handle, 'All', 14, True, addon_path + '/manage.png', total_items)
    addDirectory(handle, 'Continuing', 14, True, addon_path + '/manage.png', total_items)
    addDirectory(handle, 'Ended', 14, True, addon_path + '/manage.png', total_items)
    addDirectory(handle, 'Paused', 14, True, addon_path + '/manage.png', total_items)
    xbmcplugin.endOfDirectory(int(handle))

      
def addDirectory(handle, menu_item_name, menu_number, folder, icon, total_items):
    return_url = sys.argv[0] + "?url=" + urllib.quote_plus("") + "&mode=" + str(menu_number) + "&name=" + urllib.quote_plus(menu_item_name)
    list_item = xbmcgui.ListItem(menu_item_name)
    list_item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': '', 'banner': '', 'clearart': '', 'clearlogo': '', 'landscape': ''})
    xbmcplugin.addDirectoryItem(handle=int(handle), url=return_url, listitem=list_item, isFolder=folder, totalItems=total_items)

