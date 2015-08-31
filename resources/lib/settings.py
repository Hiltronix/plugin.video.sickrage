import xbmcgui
import xbmcaddon
import sys
import json
import urllib
import urllib2
import base64
import sickbeard


def createURL(ip, port, use_ssl, custom_url):
    if custom_url != "":
        return custom_url
    if str(ip) == "" or str(port) == "":
        displayError("1")
    else:
        if use_ssl == "true":
            return "https://"+str(ip)+":"+str(port)
        else:
            return "http://"+str(ip)+":"+str(port)


def GetApiKey(ip, port, use_ssl, username, password, custom_url):
    # Get API key from webserver using official API request.
    base_url = createURL(ip, port, use_ssl, custom_url)
    api_key = ''
    try:
        url = base_url + '/getkey/?u=' + username + '&p=' + password
        response = sickbeard.GetUrlData(url, False)
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
def GetApiKeyScraper(ip, port, use_ssl, username, password, custom_url):
    # Get API key from Sickbeark
    base_url = createURL(ip, port, use_ssl, custom_url)
    if username and password:
        try:
            request = urllib2.Request(base_url + '/config/general/')
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % base64string)
            resp = urllib2.urlopen(request)
            result = resp.readlines()
            #auth_url = base_url + "/login/"
            #url = base_url + '/config/general/'
            #login_data = urllib.urlencode({'username' : username, 'password' : password})
            #cj = cookielib.CookieJar()
            #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            #urllib2.install_opener(opener)
            #opener.open(auth_url, login_data)
            #resp = opener.open(url)
            #result = resp.readlines()
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


# Set constants.
__addon__ = xbmcaddon.Addon(id='plugin.video.sickrage')
__ip__ = __addon__.getSetting('SickRage IP')
__port__= __addon__.getSetting('SickRage Port')
__ssl_bool__= __addon__.getSetting('Use SSL')
__servertype__ = __addon__.getSetting('ServerType')
__username__ = __addon__.getSetting('SickRage Username')
__password__= __addon__.getSetting('SickRage Password')
__url_bool__= __addon__.getSetting('CustomURL')
__api_key__=__addon__.getSetting('SickRage API Key')
if __url_bool__ == "true":
    __custom_url__= __addon__.getSetting('SickRage URL')
else:
    __custom_url__= ""
__history_max__=__addon__.getSetting('HistoryMax')
if (int(__history_max__) > 99):
    __addon__.setSetting('HistoryMax', '99')
    __history_max__ = 99
__show_log__= __addon__.getSetting('ShowLog')
__show_clearcache__= __addon__.getSetting('ShowClearCache')


# Show error pop up then exit plugin.
def messageWindow(header, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(header, message)


# Show error pop up then exit plugin.
def errorWindow(header, message):
    dialog = xbmcgui.Dialog()
    dialog.ok(header, message)
    sys.exit()


# Display the correct error message based on error code.
def displayError(error_code, err=""):
    if error_code == "1":
        errorWindow("Error", "Must configure IP and port settings before use.")
    elif error_code == "2":
        errorWindow("Error", "Invalid username or password.")
    elif error_code == "3":
        errorWindow("Error", "Unable to connect to SickRage webserver.\nCheck the IP and port settings.")
    elif error_code == "4":
        errorWindow("Error", "Unable to retrieve API key.\nEnter or paste API key manually into settings field.\nOr check username and password, that the API key was generated on webserver, and if webserver is running.")
    elif error_code == "5":
        errorWindow("Exception Error", str(err))


# If settings API field is blank, then try to scrape webserver settings page and retrieve it.
if (__api_key__ == ""):
    if (__servertype__ == 'SickRage'):
        __api_key__ = GetApiKey(__ip__, __port__, __ssl_bool__, __username__, __password__, __custom_url__)
    else:
        __api_key__ = GetApiKeyScraper(__ip__, __port__, __ssl_bool__, __username__, __password__, __custom_url__)
    __addon__.setSetting('SickRage API Key', __api_key__)
    
# Create the URL used to access webserver.
if __ssl_bool__ == "true":
    __url__='https://'+__ip__+':'+__port__+'/api/'+__api_key__+'/'
else:
    __url__='http://'+__ip__+':'+__port__+'/api/'+__api_key__+'/'
