import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import sys
import urllib
import shows


my_addon = xbmcaddon.Addon('plugin.video.sickrage')


def menu():
    addDirectory('All', 14, True, my_addon.getAddonInfo('path')+'/manage.png', my_addon.getAddonInfo('path')+'/resources/images/manage_thn.png')
    addDirectory('Continuing', 14, True, my_addon.getAddonInfo('path')+'/manage.png', my_addon.getAddonInfo('path')+'/resources/images/manage_thn.png')
    addDirectory('Ended', 14, True, my_addon.getAddonInfo('path')+'/manage.png', my_addon.getAddonInfo('path')+'/resources/images/manage_thn.png')
    addDirectory('Paused', 14, True, my_addon.getAddonInfo('path')+'/manage.png', my_addon.getAddonInfo('path')+'/resources/images/manage_thn.png')

      
def addDirectory(menu_item_name, menu_number, folder, icon, thumbnail):
        return_url = sys.argv[0]+"?url="+urllib.quote_plus("")+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(menu_item_name)
        list_item = xbmcgui.ListItem(menu_item_name, iconImage=thumbnail, thumbnailImage=icon)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=folder, totalItems=4)



