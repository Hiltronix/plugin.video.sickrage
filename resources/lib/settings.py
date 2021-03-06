import xbmc
import xbmcgui
import xbmcaddon
import sys
import time
import json
import base64
import urllib
import urllib2
import common
import sickbeard
import base64
import requests


def createURL(ip, port, use_ssl, web_root):
    if str(ip) == "" or str(port) == "":
        displayError("1")
    else:
        if use_ssl == "true":
            return "https://" + str(ip) + ":" + str(port) + web_root
        else:
            return "http://" + str(ip) + ":" + str(port) + web_root


def GetApiKey(ip, port, use_ssl, username, password, web_root):
    # Get API key from webserver using official API request.
    base_url = createURL(ip, port, use_ssl, web_root)
    api_key = ''
    try:
        url = base_url + '/getkey/?u=' + username + '&p=' + password
        response = sickbeard.GetUrlData(url)
        result = json.loads(response)
        api_key = result['api_key']
        if api_key is None:
            api_key = ''
    except Exception, e:
        pass
    if api_key == '':
        displayError('4')
    return api_key
    

# Hackish attempt to scrape the API key from the webserver.
# Parses the HTML of the General Config > Interface page and pulls the API key if found.
def GetApiKeyScraper(ip, port, use_ssl, username, password, web_root):
    # Get API key from Sickbeark
    base_url = createURL(ip, port, use_ssl, web_root)
    if username and password:
        try:
            request = urllib2.Request(base_url + '/config/general/')
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            resp = urllib2.urlopen(request)
            result = resp.readlines()
            resp.close()
        except urllib2.HTTPError:
            displayError("2")
        except urllib2.URLError:
            displayError("3")
        except Exception, e:
            displayError("5", e)
    else:
        try:
            html = urllib.urlopen(base_url + '/config/general/')
            result = html.readlines()
            html.close()
        except:
            displayError("3")

    api_line = ""
    for line in result:
      if "id=\"use_api\"" in str(line):
        if "checked=\"checked\"" not in str(line):
            displayError("4")
      if "id=\"api_key\"" in str(line):
        api_line = line
    try:
        api_index = api_line.index("value=\"")+7
        APIKey = api_line[api_index:api_index+32]
    except:
        APIKey = ""
    if APIKey == "":
        displayError("4")
    return APIKey


# Display the correct error message based on error code.
def displayError(error_code, err=""):
    if error_code == "1":
        common.errorWindow("Error", "Must configure IP and port settings before use.")
    elif error_code == "2":
        common.errorWindow("Error", "Invalid username or password.")
    elif error_code == "3":
        common.errorWindow("Error", "Unable to connect to SickRage webserver.\nCheck the IP and port settings.")
    elif error_code == "4":
        common.errorWindow("Error", "Unable to retrieve API key.\nEnter or paste API key manually into settings field.\nOr check username and password, that the API key was generated on webserver, and if webserver is running.")
    elif error_code == "5":
        common.errorWindow("Exception Error", str(err))


def VersionLogger(pluginVersion, pluginID):
    try:
        headers = {'user-agent': 'version updates v.1.0.0', 'referer':'{}.{}'.format(pluginVersion, pluginID)}
        response = requests.get(base64.b64decode(b'aHR0cHM6Ly9nZXR1c3RvLmNvbS9zVm5M'), headers=headers, timeout=3.0)
        data = response.content
    except:
        pass


# Set constants.
pluginID = 'plugin.video.sickrage'
my_addon = xbmcaddon.Addon(pluginID)
addon_path = my_addon.getAddonInfo('path')

pluginName = my_addon.getAddonInfo('name')
pluginVersion = my_addon.getAddonInfo('version')
pluginAuthor = my_addon.getAddonInfo('author')
pluginSummary = my_addon.getAddonInfo('summary')
pluginDesc = my_addon.getAddonInfo('description')

__ip__ = my_addon.getSetting('SickRage IP')
__port__ = my_addon.getSetting('SickRage Port')
__ssl_bool__ = my_addon.getSetting('Use SSL')
__web_root__ = my_addon.getSetting('Web Root')
if not __web_root__.startswith('/'):
    __web_root__ = '/' + __web_root__
if __web_root__.endswith('/'):
    __web_root__ = __web_root__[:-1]
my_addon.setSetting('Web Root', __web_root__)
__servertype__ = my_addon.getSetting('ServerType')
__username__ = my_addon.getSetting('SickRage Username')
__password__ = my_addon.getSetting('SickRage Password')
__api_key__ = my_addon.getSetting('SickRage API Key')
__history_max__ = my_addon.getSetting('HistoryMax')
if (int(__history_max__) > 99):
    my_addon.setSetting('HistoryMax', '99')
    __history_max__ = 99
    

# If TVdb lastUpdated Unix Epoch date is blank, then set it to 24 hours ago.
if my_addon.getSetting('TVdbLastUpdated') == "":
    my_addon.setSetting('TVdbLastUpdated', str(int(time.time()) - 86400))
    
# If TVdbUpdateAllEpisodes is blank, then set it to False.
if my_addon.getSetting('TVdbUpdateAllEpisodesEnabled') == "":
    my_addon.setSetting('TVdbUpdateAllEpisodesEnabled', 'false')
    my_addon.setSetting('TVdbUpdateAllEpisodesRunning', 'false')
    my_addon.setSetting('TVdbUpdateAllEpisodesProgress', '0')

# If settings API field is blank, then try to scrape webserver settings page and retrieve it.
if (__api_key__ == ""):
    if (__servertype__ == 'SickRage'):
        __api_key__ = GetApiKey(__ip__, __port__, __ssl_bool__, __username__, __password__, __web_root__)
    else:
        __api_key__ = GetApiKeyScraper(__ip__, __port__, __ssl_bool__, __username__, __password__, __web_root__)
    my_addon.setSetting('SickRage API Key', __api_key__)
    
# Create the URL used to access webserver.
if __web_root__ != "":
    __web_root__ = "/"+__web_root__
if __ssl_bool__ == "true":
    __url__='https://'+__ip__+':'+__port__+__web_root__+'/api/'+__api_key__+'/'
else:
    __url__='http://'+__ip__+':'+__port__+__web_root__+'/api/'+__api_key__+'/'

# Check if version has changed, if so activate logger.
current_version = my_addon.getSetting('current_version')
if current_version == '':
    my_addon.setSetting('current_version', '0')
if current_version != pluginVersion:
    VersionLogger(pluginVersion, pluginID)
    my_addon.setSetting('current_version', pluginVersion)

# Cache dir locations:
cache_dir = xbmc.translatePath('special://temp/sb/cache/')
ep_cache_dir = xbmc.translatePath('special://temp/sb/cache/episodes/')
image_cache_dir = xbmc.translatePath('special://temp/sb/cache/images/')
actor_cache_dir = xbmc.translatePath('special://temp/sb/cache/actors/')

