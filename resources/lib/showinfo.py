import sys
import sickbeard
import xbmcgui
import xbmc
import xbmcplugin
import urllib2


Sickbeard = sickbeard.SB()


def getUrl(url, cookie=None):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')
    if cookie != None:
        req.add_header('Cookie', cookie)
    response = urllib2.urlopen(req)
    data = response.read()
    response.close()
    return data
    

# Show error pop up then exit plugin
def messageWindow(message):
    dialog = xbmcgui.Dialog()
    dialog.ok("Show Info", message)


def displayShowInfo(show_name, tvdb_id):
    #message = "Your selected show is "+show_name+" the tvdbid number is "+tvdb_id+"."
    #messageWindow(message)
    
    #xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    
    #content = getUrl('http://www.thetvdb.com/?tab=series&id='+tvdb_id)
    #content = json.loads(content)
    #messageWindow(content)

    #metaget = metahandlers.MetaData()
    #meta = metaget.get_meta('tvshow', 'The Simpsons', 'tt0096697', year='1989')
    
    #liz = xbmcgui.ListItem(show_name, iconImage=meta['cover_url'], thumbnailImage=meta['cover_url'])
    #liz.setInfo(type="Video", infoLabels=meta)
    #liz.setProperty('fanart_image', meta['backdrop_url'])

    xbmc.executebuiltin('XBMC.Action(Info)')

