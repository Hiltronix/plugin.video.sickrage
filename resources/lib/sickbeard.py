# -*- coding: utf-8 -*-

import xbmc
import os
import sys
import json
import requests
import cache
import common
import settings


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
    

def getFromDict(dataDict, mapList, default_result=None):
# Similar to dictionary '.get' but for nested dictionaies.
# Example: getFromDict(dataDict, ["b", "v", "y"])
# Returns 'None' if not found, unless a default result is provided.
    try:
        value = reduce(lambda d, k: d[k], mapList, dataDict)
        if value:
            return value
        else:
            return default_result
    except Exception:
        return default_result


def GetUrlData(url=None, headers={}, proxies={}, verify=False, log=None):
    # Fetches data from "url" (http or https) and return it as a string, with timeout.
    # Supply any headers and proxies as dict.
    # A default User-Agent will be added if the headers dict doesn't contain one.
    # Set "verify" True if you want SSL certs to be verified.
    # If using logging, pass your log handle.
    try:
        if not headers.get('User-Agent'):
            headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'

        response = requests.get(url, headers=headers, proxies=proxies, verify=verify, timeout=5.0)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except requests.Timeout:
        common.messageWindow('Network Connection', 'The request timed out.[CR]The server may be busy or unavailable.')
        return None
    except Exception, e:
        #print e
        xbmc.log('sickrage.sickbeard.GetUrlData: {0}'.format(e), xbmc.LOGERROR)
        if log:
            log.debug('*** Exception ***', exc_info=1)
        err = 'Exception: {0}'.format(e)
        common.messageWindow('Network Connection', err)
        return None


# SickRage class which mas all API calls to SickRage.
class SB:

    CONNECT_ERROR = "Error: "

    
    # Get the list of shows.
    def GetShows(self):
        shows=[]
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=shows')
            if not response:
                return None
            result = json.loads(response)
            for each in result['data']:
                show = {}
                # Minimum required fields listed first.
                show['tvdbid'] = str(result['data'][each]['tvdbid'])
                show['show_name'] = FixBadChar(result['data'][each]['show_name'])
                show['paused'] = result['data'][each]['paused']
                show['status'] = result['data'][each]['status']
                try:
                    show['next_ep_airdate'] = result['data'][each]['next_ep_airdate']
                except Exception:
                    show['next_ep_airdate'] = ''
                try:
                    show['anime'] = result['data'][each]['anime']
                except Exception:
                    show['anime'] = ''
                try:
                    show['indexerid'] = str(result['data'][each]['indexerid'])
                except Exception:
                    show['indexerid'] = ''
                try:
                    show['language'] = result['data'][each]['language']
                except Exception:
                    show['language'] = ''
                try:
                    show['network'] = result['data'][each]['network']
                except Exception:
                    show['network'] = ''
                try:
                    show['next_ep_airdate'] = result['data'][each]['next_ep_airdate']
                except Exception:
                    show['next_ep_airdate'] = ''
                try:
                    show['quality'] = result['data'][each]['quality']
                except Exception:
                    show['quality'] = ''
                try:
                    show['sports'] = result['data'][each]['sports']
                except Exception:
                    show['sports'] = ''
                try:
                    show['subtitles'] = result['data'][each]['subtitles']
                except Exception:
                    show['subtitles'] = ''
                try:
                    show['tvrage_id'] = str(result['data'][each]['tvrage_id'])
                except Exception:
                    show['tvrage_id'] = ''
                try:
                    show['tvrage_name'] = result['data'][each]['tvrage_name']
                except Exception:
                    show['tvrage_name'] = ''
                shows.append(show)
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return shows
    

    # Get the show ID numbers
    def GetShowIds(self):
        show_ids=[]
        try:
            response = GetUrlData(url=settings.__url__+"?cmd=shows")
            if not response:
                return None
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
                response = GetUrlData(url=settings.__url__+'?cmd=show&tvdbid='+id)
                if not response:
                    return None
                result = json.loads(response)
                name = getFromDict(result, ['data', 'show_name'])
                paused = getFromDict(result, ['data', 'paused'])
                status = getFromDict(result, ['data', 'status'])
                show_info[name] = [id, paused, status]
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return show_info

    
    # Returns the details of a show from SickRage.
    def GetShowDetails(self, show_id):
        details = []
        total = []
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=show&tvdbid='+show_id)
            if not response:
                return None
            result = json.loads(response)
            details = result.get('data')
            
            response = GetUrlData(url=settings.__url__+'?cmd=show.stats&tvdbid='+show_id)
            if not response:
                return None
            result = json.loads(response)
            total = result['data']['total']
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))                   
        return details, total
    

    # Return a list of season numbers.
    def GetSeasonNumberList(self, show_id):
        season_number_list = []
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=show.seasonlist&tvdbid='+show_id)
            if not response:
                return
            result = json.loads(response)
            season_number_list = result.get('data')
            season_number_list.sort()
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return season_number_list
    

    # Get the list of episodes in a given season.
    def GetSeasonEpisodeList(self, show_id, season):
        season_episodes = []
        try:
            season = str(season)
            response = GetUrlData(url=settings.__url__+'?cmd=show.seasons&tvdbid='+show_id+'&season='+season)
            if not response:
                return
            result = json.loads(response)
            season_episodes = result.get('data')
              
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
    def GetShowPoster(self, show_id, update=False):
        image = None
        if show_id == '0':
            return ''
        file_path = cache.image_cache_dir + show_id + '.poster.jpg'
        if not os.path.exists(file_path) or update:
            # Download image from SB server.
            try:
                image = GetUrlData(url=settings.__url__+'?cmd=show.getposter&tvdbid='+str(show_id))
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
                f = open(file_path, 'wb+')
                f.write(image)
                f.close()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, str(e))
        return file_path


    # Check if there is a cached fanart image to use.
    # If not get image from server, and save in local cache.
    # Returns path to image if found.
    # If not found, or object is less than 1K meaning it's a json error message, then get generic image.
    def GetShowFanArt(self, show_id, update=False):
        image = None
        if show_id == '0':
            return ''
        file_path = cache.image_cache_dir + show_id + '.fanart.jpg'
        if not os.path.exists(file_path) or update:
            # Download image from SB server.
            try:
                image = GetUrlData(url=settings.__url__+'?cmd=show.getfanart&tvdbid='+str(show_id))
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
                f = open(file_path, 'wb+')
                f.write(image)
                f.close()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, str(e))
        return file_path


    # Check if there is a cached banner image to use.
    # If not get image from server, and save in local cache.
    # Returns path to image if found.
    # If not found, or object is less than 1K meaning it's a json error message, then get generic image.
    def GetShowBanner(self, show_id, update=False):
        image = None
        if show_id == '0':
            return ''
        file_path = cache.image_cache_dir + show_id + '.banner.jpg'
        if not os.path.exists(file_path) or update:
            # Download image from SB server.
            try:
                image = GetUrlData(url=settings.__url__+'?cmd=show.getbanner&tvdbid='+str(show_id))
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
                f = open(file_path, 'wb+')
                f.write(image)
                f.close()
            except Exception, e:
                settings.errorWindow(sys._getframe().f_code.co_name, str(e))
        return file_path


    # Get list of upcoming episodes
    def GetFutureShows(self):
        future_list = []
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=future&sort=date&type=today|soon|later')
            if not response:
                return None
            result = json.loads(response)
            future_list = result.get('data')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return future_list
    

    # Return a list of the last 'num_entries' snatched/downloaded episodes.
    def GetHistory(self, num_entries):
        history = []
        xbmc.log('sickbeard.GetHistory')
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=history&limit='+str(num_entries))
            if not response:
                return None
            result = json.loads(response)
            history = result.get('data')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return history
    

    # Search the tvdb for a show using the SickRage API.
    def SearchShowName(self, name):
        search_results = []
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=sb.searchtvdb&name='+name+'&lang=en')
            if not response:
                return None
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
            response = GetUrlData(url=settings.__url__+'?cmd=sb.getdefaults')
            if not response:
                return None
            result = json.loads(response)
            print result.keys()
            defaults_data = result.get('data')
            if defaults_data:
                defaults = [defaults_data['status'], defaults_data['flatten_folders'], str(defaults_data['initial'])]
            else:
                defaults = ['skipped', 1, ["sdtv", "sddvd", "hdtv", "rawhdtv", "fullhdtv", "hdwebdl", "fullhdwebdl", "hdbluray", "fullhdbluray", "unknown"]]
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return defaults
    

    # Return a list of the save paths set in SickRage.
    def GetRootDirs(self):
        directory_result = []
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=sb.getrootdirs')
            if not response:
                return None
            result = json.loads(response)
            result = result.get('data')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return result
    

    # Get the version of SickRage.
    def GetVersion(self):
        version = ""
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=sb')
            result = json.loads(response)
            api = getFromDict(result, ['data', 'api_version'], 'Unknown')
            version = getFromDict(result, ['data', 'sb_version'], 'Unknown')
            if version == 'Unknown':
                version = getFromDict(result, ['data', 'sr_version'], 'Unknown')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return api, version
    

    # Set the status of an episode.
    def SetShowStatus(self, tvdbid, season, ep, status):
        result = []
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=episode.setstatus&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep)+'&status='+status+'&force=True')
            if not response:
                return None
            result = json.loads(response)
            # No result is actually returned from this call.
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return result
    

    # Add a new show to SickRage.
    def AddNewShow(self, tvdbid, location, prev_aired_status, future_status, flatten_folders, quality):
        result = ""
        try:
            url = settings.__url__+'?cmd=show.addnew&tvdbid='+str(tvdbid)+'&location='+location+'&status='+prev_aired_status+'&future_status='+future_status+'&flatten_folders='+str(flatten_folders)+'&initial='+quality
            print 'Add Show Request:' + url
            response = GetUrlData(url=url)
            result = json.loads(response)
            success = result.get('result', 'Unknown result!')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return success
    

    def ForceSearch(self, show_id):
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=show.update&tvdbid='+show_id)
            if not response:
                return None
            result = json.loads(response)
            message = result.get('message')
            success = result.get('result')
            settings.errorWindow("Force Update", message + " ["+success+"]")
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))

    
    def SetPausedState(self, paused, show_id):
        message = ""
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=show.pause&indexerid='+show_id+'&tvdbid='+show_id+'&pause='+paused)
            if not response:
                return None
            result = json.loads(response)
            message = result.get('message')
            success = result.get('result')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return message
    

    def ForceDownload(self, tvdbid, season, ep):
        message = ""
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=episode.search&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep))
            if not response:
                return None
            result = json.loads(response)
            message = result.get('message')
            success = result.get('result')
            settings.errorWindow(sys._getframe().f_code.co_name, message + " ["+success+"]")
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return message
    

    def DeleteShow(self, tvdbid, removefiles):
        message = ""
        try:
            response = GetUrlData(url=settings.__url__+'?cmd=show.delete&tvdbid='+str(tvdbid)+'&removefiles='+str(removefiles))
            result = json.loads(response)
            message = result.get('message')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return message
      

    # Get the backlog list.
    def GetBacklog(self):
        results = [] 
        try:
            response = GetUrlData(url=settings.__url__+"?cmd=backlog")
            if not response:
                return None
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
            response = GetUrlData(url=settings.__url__ + '?cmd=logs&min_level=' + str(min_level))
            if not response:
                return None
            result = json.loads(response)
            log_list = result.get('data')
        except Exception, e:
            settings.errorWindow(sys._getframe().f_code.co_name, self.CONNECT_ERROR+str(e))
        return log_list
      
