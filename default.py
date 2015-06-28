import urllib
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import resources.lib.settings
import resources.lib.sickbeard as sickbeard


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


# Add the main directory folders.
def mainMenu():
        addDirectory('Upcoming Episodes', 2, True, 'special://home/addons/plugin.video.sickrage/upcoming.png')
        addDirectory('History', 3, True, 'special://home/addons/plugin.video.sickrage/history.png')
        addDirectory('Backlog', 9, True, 'special://home/addons/plugin.video.sickrage/backlog.png')
        addDirectory('Manage Shows', 1, True, 'special://home/addons/plugin.video.sickrage/manage.png')
        addDirectory('Add New Show', 7, False, 'special://home/addons/plugin.video.sickrage/add.png')


# Add directory item.
def addDirectory(menu_item_name, menu_number, folder, icon):
        return_url = sys.argv[0]+"?url="+urllib.quote_plus("")+"&mode="+str(menu_number)+"&name="+urllib.quote_plus(menu_item_name)
        list_item = xbmcgui.ListItem(menu_item_name, iconImage=icon)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=return_url, listitem=list_item, isFolder=folder, totalItems=3)


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
showtitle = None
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
    showtitle = urllib.unquote_plus(params["title"])
    menu_number = 7
    print showtitle
except:
    pass

try:
    action = urllib.unquote_plus(params["action"])
    menu_number = 8
    print action
except:
    pass

try:
    show_name = urllib.unquote_plus(params["show_name"])
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
    import resources.lib.shows as shows
    shows.menu()
        
elif menu_number == 2:
    import resources.lib.upcoming as upcoming
    upcoming.menu()
        
elif menu_number == 3:
    import resources.lib.history as history
    history.menu()

elif menu_number == 4:
    import resources.lib.seasons as seasons
    seasons.menu(url, name)

elif menu_number == 5:
    import resources.lib.episodes as episodes
    episodes.menu(url, name, number)

elif menu_number == 6:
    import resources.lib.showinfo as showinfo
    showinfo.displayShowInfo(name, url)

elif menu_number == 7:
    import resources.lib.addshow as addshow
    addshow.AddShow(showtitle)

elif menu_number == 8:
    import resources.lib.addshow as addshow
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
    import resources.lib.backlog as backlog
    backlog.menu()
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))        
