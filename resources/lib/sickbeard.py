# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib2
import socket
import json
import settings
import xbmc
import xbmcgui


# Get data from a dictionary with position provided as if it were a list.
# Example: test = getFromDict(result['data'], ['75897', 'show_name'])
def getFromDict(dataDict, mapList):
    try:
        return reduce(lambda d, k: d[k], mapList, dataDict)
    except:
        return None


# Replace troublesome characters, that effect sorting.
def FixBadChar(text):
    text = text.replace(u'\u2019', u"'")  # Replace curved apostrophe � with standard ' apostrophe.
    text = text.replace(u'\u2010', u"-")  # Replace wide dash with standard hyphen.
    text = text.replace(u'\u2011', u"-")  # Replace wide dash with standard hyphen.
    text = text.replace(u'\u2012', u"-")  # Replace wide dash with standard hyphen.
    text = text.replace(u'\u2013', u"-")  # Replace wide dash with standard hyphen.
    text = text.replace(u'\u2014', u"-")  # Replace wide dash with standard hyphen.
    text = text.replace(u'\u2015', u"-")  # Replace wide dash with standard hyphen.
    return text
    

def GetUrlData(url=None, add_useragent=False, encodeType='utf-8'):
    # Fetches data from "url" (http or https) and return it as a string, with timeout.
    # Set "encodeType" to None for image and binary files.
    attempts = 0
    request = urllib2.Request(url)
    if add_useragent:
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:32.0) Gecko/20100101 Firefox/32.0'}
        for (key, value) in headers.iteritems():
            request.add_header(key, value)
    # Try up to 3 times to make connection.
    while (attempts < 5) and (not xbmc.abortRequested):
        try:
            # Wait 5 seconds for connection.
            response = urllib2.urlopen(request, timeout=5)
            if encodeType == None:
                data = response.read()
                return data
            else:
                encoding = response.headers.getparam('charset')
                print 'Encoding: ' + encoding
                data = response.read().decode(encoding)
                return data.encode(encodeType, 'ignore')
        except urllib2.URLError, e:
            print "URLError Msg: %s   Getting data from: %s" %(e, url)
            xbmc.sleep(500)
            if xbmc.abortRequested:
                break
            attempts += 1
        except socket.timeout, e:
            print "Socket Timeout Error Msg: %s   Getting data from: %s" %(e, url)
            xbmc.sleep(500)
            if xbmc.abortRequested:
                break
            attempts += 1
    return None


# SickRage class which mas all API calls to SickRage.
class SB:

    CONNECT_ERROR = "I was unable to retrieve data.\n\nError: "

    
    # Get the list of shows.
    def GetShows(self):
        shows=[]
        try:
            response = GetUrlData(settings.__url__+'?cmd=shows', False)
            result = json.loads(response)
            for each in result['data']:
                show = {}
                show['anime'] = getFromDict(result['data'], [each, 'anime'])
                show['indexerid'] = str(getFromDict(result['data'], [each, 'indexerid']))
                show['language'] = getFromDict(result['data'], [each, 'language'])
                show['network'] = getFromDict(result['data'], [each, 'network'])
                show['next_ep_airdate'] = getFromDict(result['data'], [each, 'next_ep_airdate'])
                show['paused'] = getFromDict(result['data'], [each, 'paused'])
                show['quality'] = getFromDict(result['data'], [each, 'quality'])
                show['show_name'] = FixBadChar(getFromDict(result['data'], [each, 'show_name']))
                show['sports'] = getFromDict(result['data'], [each, 'sports'])
                show['status'] = getFromDict(result['data'], [each, 'status'])
                show['subtitles'] = getFromDict(result['data'], [each, 'subtitles'])
                show['tvdbid'] = str(getFromDict(result['data'], [each, 'tvdbid']))
                show['tvrage_id'] = str(getFromDict(result['data'], [each, 'tvrage_id']))
                show['tvrage_name'] = getFromDict(result['data'], [each, 'tvrage_name'])
                shows.append(show)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return shows
    

    # Get the show ID numbers
    def GetShowIds(self):
        show_ids=[]
        try:
            response = GetUrlData(settings.__url__+"?cmd=shows", False)
            result = json.loads(response)
            for each in result['data']:
                show_ids.append(each)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return show_ids
    

    # Get show info dict, key:show_name value:tvdbid
    def GetShowInfo(self, show_ids):
        show_info={}
        try:
            for id in show_ids:
                response = GetUrlData(settings.__url__+'?cmd=show&tvdbid='+id, False)
                result = json.loads(response)
                name = result['data']['show_name']
                paused = result['data']['paused']
                status = result['data']['status']
                show_info[name] = [id, paused, status]
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return show_info

    
    # Returns the details of a show from SickRage.
    def GetShowDetails(self, show_id):
        details = []
        total = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=show&tvdbid='+show_id, False)
            result = json.loads(response)
            details = result['data']
            
            response = GetUrlData(settings.__url__+'?cmd=show.stats&tvdbid='+show_id, False)
            result = json.loads(response)
            total = result['data']['total']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))                   
        return details, total
    

    # Return a list of season numbers.
    def GetSeasonNumberList(self, show_id):
        season_number_list = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=show.seasonlist&tvdbid='+show_id, False)
            result = json.loads(response)
            season_number_list = result['data']
            season_number_list.sort()
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return season_number_list
    

    # Get the list of episodes in a given season.
    def GetSeasonEpisodeList(self, show_id, season):
        season_episodes = []
        try:
            season = str(season)
            response = GetUrlData(settings.__url__+'?cmd=show.seasons&tvdbid='+show_id+'&season='+season, False)
            result = json.loads(response)
            season_episodes = result['data']
              
            for key in season_episodes.iterkeys():
                if int(key) < 10:
                    newkey = '{0}'.format(key.zfill(2))
                    if newkey not in season_episodes:
                        season_episodes[newkey] = season_episodes[key]
                        del season_episodes[key]
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))        
        return season_episodes
    

    # Check if there is a cached poster image to use.
    # If not get image from server, and save in local cache.
    # Returns path to image if found.
    # If not found, or object is less than 1K meaning it's a json error message, then get generic image.
    def GetShowPoster(self, show_id):
        image = None
        if show_id == '0':
            return ''
        file_path = xbmc.translatePath('special://temp/sb/cache/images/'+show_id+'.poster.jpg')
        if not os.path.exists(file_path):
            # Download image from SB server.
            try:
                image = GetUrlData(settings.__url__+'?cmd=show.getposter&tvdbid='+str(show_id), False, None)
                if (image == None) or (len(image) < 1024):
                    # Get generic image instead.
                    with open(xbmc.translatePath('special://home/addons/plugin.video.sickrage/resources/images/missing_poster.jpg'), mode='rb') as f:
                        image = f.read()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
                return ''
            # Write image file to local cache.
            try:
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                f = open(file_path, 'wb')
                f.write(image)
                f.close()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, str(e))
        return file_path


    # Check if there is a cached fanart image to use.
    # If not get image from server, and save in local cache.
    # Returns path to image if found.
    # If not found, or object is less than 1K meaning it's a json error message, then get generic image.
    def GetShowFanArt(self, show_id):
        image = None
        if show_id == '0':
            return ''
        file_path = xbmc.translatePath('special://temp/sb/cache/images/'+show_id+'.fanart.jpg')
        if not os.path.exists(file_path):
            # Download image from SB server.
            try:
                image = GetUrlData(settings.__url__+'?cmd=show.getfanart&tvdbid='+str(show_id), False, None)
                if (image == None) or (len(image) < 1024):
                    # Get generic image instead.
                    with open(xbmc.translatePath('special://home/addons/plugin.video.sickrage/resources/images/missing_fanart.jpg'), mode='rb') as f:
                        image = f.read()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
                return ''
            # Write image file to local cache.
            try:
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                f = open(file_path, 'wb')
                f.write(image)
                f.close()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, str(e))
        return file_path


    # Check if there is a cached banner image to use.
    # If not get image from server, and save in local cache.
    # Returns path to image if found.
    # If not found, or object is less than 1K meaning it's a json error message, then get generic image.
    def GetShowBanner(self, show_id):
        image = None
        if show_id == '0':
            return ''
        file_path = xbmc.translatePath('special://temp/sb/cache/images/'+show_id+'.banner.jpg')
        if not os.path.exists(file_path):
            # Download image from SB server.
            try:
                image = GetUrlData(settings.__url__+'?cmd=show.getbanner&tvdbid='+str(show_id), False, None)
                if (image == None) or (len(image) < 1024):
                    # Get generic image instead.
                    with open(xbmc.translatePath('special://home/addons/plugin.video.sickrage/resources/images/missing_banner.jpg'), mode='rb') as f:
                        image = f.read()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
                return ''
            # Write image file to local cache.
            try:
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                f = open(file_path, 'wb')
                f.write(image)
                f.close()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, str(e))
        return file_path


    # Clear all image files from the image cache.
    def ClearImageCache(self):
        path = xbmc.translatePath('special://temp/sb/cache/images/')
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.lower().endswith(".jpg"):
                    os.unlink(os.path.join(path, file))
            for file in os.listdir(path):
                if file.lower().endswith(".png"):
                    os.unlink(os.path.join(path, file))


    # Gets the show banner from SickRage.
    #def GetShowBanner(self, show_id):
    #    if settings.__ssl_bool__ == "true":
    #        return 'https://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.banner.jpg'
    #    else:
    #        return 'http://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.banner.jpg'
    

    # Check if there is a cached thumbnail to use, if not use SickRage poster.
    #def GetShowPoster(self, show_id):
    #    if settings.__ssl_bool__ == "true":
    #        return 'https://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.poster.jpg'
    #    else:
    #        return 'http://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.poster.jpg'
    

    # Get list of upcoming episodes
    def GetFutureShows(self):
        future_list = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=future&sort=date&type=today|soon|later', False)
            result = json.loads(response)
            future_list = result['data']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return future_list
    

    # Return a list of the last 'num_entries' snatched/downloaded episodes.
    def GetHistory(self, num_entries):
        history = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=history&limit='+str(num_entries), False)
            result = json.loads(response)
            history = result['data']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return history
    

    # Search the tvdb for a show using the SickRage API.
    def SearchShowName(self, name):
        search_results = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=sb.searchtvdb&name='+name+'&lang=en', False)
            result = json.loads(response)
            if result['result'] != 'success':
                return search_results
            for each in result['data']['results']:
                # Limit results to segments that contain an attribute 'tvdbid'.  SickRage webapi.py has a bug where it returns both tvdb and tvrage results together, even though they have separate search functions.
                if (each.get('tvdbid') != None):
                    search_results.append(each)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return search_results
    

    # Return a list of the default settings for adding a new show.
    def GetDefaults(self):
        defaults = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=sb.getdefaults', False)
            result = json.loads(response)
            print result.keys()
            defaults_data = result['data']
            defaults = [defaults_data['status'], defaults_data['flatten_folders'], str(defaults_data['initial'])]
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return defaults
    

    # Return a list of the save paths set in SickRage.
    def GetRoodDirs(self):
        directory_result = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=sb.getrootdirs', False)
            result = json.loads(response)
            result = result['data']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return result
    

    # Get the version of SickRage.
    def GetSickRageVersion(self):
        version = ""
        try:
            response = GetUrlData(settings.__url__+'?cmd=sb', False)
            result = json.loads(response)
            version = result['data']['sb_version']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return version
    

    # Set the status of an episode.
    def SetShowStatus(self, tvdbid, season, ep, status):
        result = []
        try:
            response = GetUrlData(settings.__url__+'?cmd=episode.setstatus&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep)+'&status='+status+'&force=True', False)
            result = json.loads(response)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return result
    

    # Add a new show to SickRage.
    def AddNewShow(self, tvdbid, location, prev_aired_status, future_status, flatten_folders, quality):
        result = ""
        try:
            url = settings.__url__+'?cmd=show.addnew&tvdbid='+str(tvdbid)+'&location='+location+'&status='+prev_aired_status+'&future_status='+future_status+'&flatten_folders='+str(flatten_folders)+'&initial='+quality
            print 'Add Show Request:' + url
            response = GetUrlData(url, False)
            result = json.loads(response)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return result['result']
    

    def ForceSearch(self, show_id):
        try:
            response = GetUrlData(settings.__url__+'?cmd=show.update&tvdbid='+show_id, False)
            result = json.loads(response)
            message = result['message']
            success = result['result']
            settings.errorWindow("Force Update", message + " ["+success+"]")
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))

    
    def SetPausedState(self, paused, show_id):
        message = ""
        try:
            response = GetUrlData(settings.__url__+'?cmd=show.pause&indexerid='+show_id+'&tvdbid='+show_id+'&pause='+paused, False)
            result = json.loads(response)
            message = result['message']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return message
    

    def ManualSearch(self, tvdbid, season, ep):
        message = ""
        try:
            response = GetUrlData(settings.__url__+'?cmd=episode.search&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep), False)
            result = json.loads(response)
            message = result['message']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return message
    

    def DeleteShow(self, tvdbid, removefiles):
        message = ""
        try:
            response = GetUrlData(settings.__url__+'?cmd=show.delete&tvdbid='+str(tvdbid)+'&removefiles='+str(removefiles), False)
            result = json.loads(response)
            message = result['message']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return message
      

    # Get the backlog list.
    def GetBacklog(self):
        results = [] 
        try:
            response = GetUrlData(settings.__url__+"?cmd=backlog", False)
            result = json.loads(response)
            for show in result['data']:
                show_name = show['show_name']
                status = show['status']
                for episode in show['episodes']:
                    episode['show_name'] = show_name
                    episode['status'] = status
                    results.append(episode)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return results


    # Get the log file.  min_level: ["error", "warning", "info", "debug"]
    def GetLog(self, min_level):
        log_list = []
        try:
            response = GetUrlData(settings.__url__ + '?cmd=logs&min_level=' + str(min_level), False)
            result = json.loads(response)
            log_list = result['data']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return log_list
      
