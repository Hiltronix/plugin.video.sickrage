import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import sys
import urllib
import shows
import settings


def menu(handle):
    total_items = 4
    addDirectory(handle, 'All', 14, True, settings.addon_path + '/manage.png', total_items)
    addDirectory(handle, 'Continuing', 14, True, settings.addon_path + '/manage.png', total_items)
    addDirectory(handle, 'Ended', 14, True, settings.addon_path + '/manage.png', total_items)
    addDirectory(handle, 'Paused', 14, True, settings.addon_path + '/manage.png', total_items)
    xbmcplugin.endOfDirectory(int(handle))

      
def addDirectory(handle, menu_item_name, menu_number, folder, icon, total_items):
    return_url = 'plugin://{}/?mode={}&name={}'.format(settings.pluginID, menu_number, urllib.quote_plus(menu_item_name))
    list_item = xbmcgui.ListItem(menu_item_name)
    list_item.setArt({'icon': icon, 'thumb': icon, 'poster': icon, 'fanart': '', 'banner': '', 'clearart': '', 'clearlogo': '', 'landscape': ''})
    xbmcplugin.addDirectoryItem(handle=int(handle), url=return_url, listitem=list_item, isFolder=folder, totalItems=total_items)

