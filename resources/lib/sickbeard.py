import urllib
import socket
import json
import settings

timeout = 45
socket.setdefaulttimeout(timeout)

# SickRage class which mas all API calls to SickRage
class SB:
  # Get the show ID numbers
  def GetShowIds(self):
      show_ids=[]
      result=json.load(urllib.urlopen(settings.__url__+"?cmd=shows"))
      for each in result['data']:
          show_ids.append(each)
      return show_ids

  # Get show info dict, key:show_name value:tvdbid
  def GetShowInfo(self, show_ids):
      show_info={}
      for id in show_ids:
          result=json.load(urllib.urlopen(settings.__url__+'?cmd=show&tvdbid='+id))
          name = result['data']['show_name']
          paused = result['data']['paused']
          status = result['data']['status']
          show_info[name] = [id, paused, status]
      return show_info
    
  # Returns the details of a show from SickRage 
  def GetShowDetails(self, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show&tvdbid='+show_id))
      details=result['data']
      
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.stats&tvdbid='+show_id))
      total=result['data']['total']
      
      return details, total
    
  # Return a list of season numbers
  def GetSeasonNumberList(self, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.seasonlist&tvdbid='+show_id))
      season_number_list = result['data']
      season_number_list.sort()
      return season_number_list

  # Get the list of episodes ina given season
  def GetSeasonEpisodeList(self, show_id, season):
      season = str(season)
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.seasons&tvdbid='+show_id+'&season='+season))
      season_episodes = result['data']
          
      for key in season_episodes.iterkeys():
          if int(key) < 10:
              newkey = '{0}'.format(key.zfill(2))
              if newkey not in season_episodes:
                  season_episodes[newkey] = season_episodes[key]
                  del season_episodes[key]
      
      return season_episodes
    
  # Gets the show banner from SickRage  
  def GetShowBanner(self, show_id):
      if settings.__ssl_bool__ == "true":
        return 'https://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.banner.jpg'
      else:
        return 'http://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.banner.jpg'

  # Check if there is a cached thumbnail to use, if not use SickRage poster
  def GetShowPoster(self, show_id):
      if settings.__ssl_bool__ == "true":
        return 'https://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.poster.jpg'
      else:
        return 'http://'+settings.__ip__+':'+settings.__port__+'/cache/images/'+str(show_id)+'.poster.jpg'

  # Get list of upcoming episodes
  def GetFutureShows(self):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=future&sort=date&type=today|soon'))
      future_list = result['data']
      return future_list

  # Return a list of the last 20 snatched/downloaded episodes    
  def GetHistory(self):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=history&limit=20'))
      history = result['data']
      return history
  
  # Search the tvdb for a show using the SickRage API  
  def SearchShowName(self, name):
    search_results = []
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=sb.searchtvdb&name='+name+'&lang=en'))
    for each in result['data']['results']:
        # Limit results to segments that contain an attribute 'tvdbid'.  SickRage webapi.py has a bug where it returns both tvdb and tvrage results together, even though they have separate search functions.
        if (each.get('tvdbid') != None):
            search_results.append(each)
    return search_results
  
  # Return a list of the default settings for adding a new show
  def GetDefaults(self):
    defaults_result = json.load(urllib.urlopen(settings.__url__+'?cmd=sb.getdefaults'))
    print defaults_result.keys()
    defaults_data = defaults_result['data']
    defaults = [defaults_data['status'], defaults_data['flatten_folders'], str(defaults_data['initial'])]
    return defaults
  
  # Return a list of the save paths set in SickRage
  def GetRoodDirs(self):
    directory_result = json.load(urllib.urlopen(settings.__url__+'?cmd=sb.getrootdirs'))
    directory_result = directory_result['data']
    return directory_result

  # Get the version of SickRage
  def GetSickRageVersion(self):
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=sb'))
    version = result['data']['sb_version']
    return version
  
  # Set the status of an episode
  def SetShowStatus(self, tvdbid, season, ep, status):
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=episode.setstatus&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep)+'&status='+status))
    return result
  
  # Add a new show to SickRage
  def AddNewShow(self, tvdbid, location, status, use_folders, quality):
    result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.addnew&tvdbid='+str(tvdbid)+'&location'+location+'&status='+status+'&season_folder='+str(use_folders)+'&initial='+quality))
    return result['result']
    
  def ForceSearch(self, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.update&tvdbid='+show_id))
      message = result['message']
      success = result['result']
      settings.messageWindow("Force Update", message + " ["+success+"]")

  def SetPausedState(self, paused, show_id):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.pause&indexerid='+show_id+'&pause='+paused))
      message = result['message']
      return message
  
  def ManualSearch(self, tvdbid, season, ep):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=episode.search&tvdbid='+str(tvdbid)+'&season='+str(season)+'&episode='+str(ep)))
      message = result['message']
      return message    
  
  def DeleteShow(self, tvdbid, removefiles):
      result=json.load(urllib.urlopen(settings.__url__+'?cmd=show.delete&tvdbid='+str(tvdbid)+'&removefiles='+str(removefiles)))
      message = result['message']
      return message   