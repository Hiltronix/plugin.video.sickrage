#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
#
# TVdb Library.
#
# (c) Carey Hildebrand 2016
#
# TVdb Requirements:
#   Login credentials with TheTVdb web service.
#   Enter the credentials either in the project __init__ file,
#   or manually in the imports section below.
#
# Socks5 Proxy Requirements for Python Requests:
#   Enter the proxy settings either in the project __init__ file,
#   or manually in the imports section below.
#   Module Requirements:
#       pip install requests[socks] --upgrade
#       pip install urllib3[socks] --upgrade
#       For Windows you must also install:
#           pip install win_inet_pton

import io
import os
import json
import time
import shutil

try:
    import requests
except ImportError, e:
    print e

try:
    import MediaInfo
    isMediaInfoAvail = True
except ImportError:
    isMediaInfoAvail = False

try:
    # Try to import the proxy settings.
    from __init__ import proxies
except ImportError, e:
    proxies = {}
    # If the proxy settings are not available, then don't use a proxy, or add them manually here.
    #proxies = {
    #    'http': 'socks5://user:pass@host:port),
    #    'https': 'socks5://user:pass@host:port)
    #}

try:
    # Try to import the TVdb settings.
    from __init__ import tvdb_api_key, tvdb_user_name, tvdb_account_id
except ImportError, e:
    # If the TBdb settings are not available, then add them manually here.
    # Your TVdb login credentials:
    tvdb_api_key = ''
    tvdb_user_name = ''
    tvdb_account_id = ''

# TheTVdb API and Image locations:
TvdbApi1_url = 'https://thetvdb.com/api'
TvdbApi2_url = 'https://api.thetvdb.com'
TvdbImageLoc = 'https://thetvdb.com/banners/'

# Define 'null' as None, since TVdb returns null in some occasions.
null = None


def LangNameFromAbbrev(code):
    lang_dict = {"zh": "Chinese",
                 "en": "English",
                 "sv": "Swedish",
                 "no": "Norwegian",
                 "da": "Danish",
                 "fi": "Finnish",
                 "nl": "Dutch",
                 "de": "German",
                 "it": "Italian",
                 "es": "Spanish",
                 "fr": "French",
                 "pl": "Polish",
                 "hu": "Hungarian",
                 "el": "Greek",
                 "tr": "Turkish",
                 "ru": "Russian",
                 "he": "Hebrew",
                 "ja": "Japanese",
                 "pt": "Portuguese",
                 "cs": "Czech",
                 "sl": "Slovenian",
                 "hr": "Croatian",
                 "ko": "Korean",
                 }
    return lang_dict.get(code, 'Unknown')


def LongDate(dt, fmt='%Y-%m-%d'):
# Converts a date string to a long number value in seconds.
# This is not UTC time, it's a local time value, no time zone is taken into effect.
# Format for example date: '2016-12-11 8:12 PM' would be: '%Y-%m-%d %I:%M %p'
    try:
        d = datetime.strptime(dt, fmt)
        value = int(time.mktime(d.timetuple()))
        return value
    except Exception, e:
        print e
        return 0


def GetDateTimeString():
# Returns YYYY-MM-DD MM:MM:SS in 24 hour clock format.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


class theTVDB:

    def __init__(self):
        self.RefreshToken()


    def GetLoginToken(self, apikey=None, username=None, userkey=None, log=None):
    # Performs authentication.
        try:
            data = {
                    "apikey": apikey,
                    "username": username,
                    "userkey": userkey
                   }

            headers = {'Content-Type': 'application/json',
                       'Content-Length': str(len(data))}

            response = requests.post(TvdbApi2_url + '/login', json.dumps(data), headers=headers, proxies=proxies)
            result = json.loads(response.content)
            return result.get('token', None)
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def RefreshToken(self, log=None):
    # Login token is good for 24 hours.
    # If login token is greater than 23 hours old, then refresh the token.
        data = self.LoadToken()
        # If token doesn't exist, fetch a new token from theTVdb API.
        if not data.get('token', None):
            self.jwt_token = self.GetLoginToken(apikey=tvdb_api_key, username=tvdb_user_name, userkey=tvdb_account_id)
            self.loginTime = time.time()
            if not self.SaveToken(self.loginTime, self.jwt_token):
                log.debug('ERROR: TVdb API Token save error!')
            return

        # Get the token from the saved dict.
        self.jwt_token = data.get('token', None)

        # If token is less than 23 hours old, then work with that token.
        if int(data.get('loginTime', 0)) + 82800 > time.time():
            return

        # We have a token but it has expired, so refresh it from theTVdb API.
        try:

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/refresh_token', headers=headers, proxies=proxies)
            result = json.loads(response.content)
            self.jwt_token = result.get('token', None)
            self.loginTime = time.time()
            # Save the updated token and current time stamp.
            if not self.SaveToken(self.loginTime, self.jwt_token):
                log.debug('ERROR: TVdb API Refreshed Token save error!')
            return
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
                log.debug('Unable to refresh the TVdb auth token, to access the TVdb API!')
            return None


    def LoadToken(self):
    # Loads the saved token (JSON file) as a dictionary.
        data = {}
        try:
            filename = __file__
            filename = str.replace(filename, filename.rpartition('.')[2], 'json')
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
        except Exception, e:
            print e
        finally:
            return data


    def SaveToken(self, loginTime, token):
    # Saves the token in a dictionary as a JSON file.
        try:
            data = {'loginTime': loginTime, 'token': token}
            filename = __file__
            filename = str.replace(filename, filename.rpartition('.')[2], 'json')
            with open(filename, 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4)
        except Exception, e:
            print e
            return False
        return True


    def SearchByName(self, name=None, log=None):
    # Returns a json result with possible shows by the given name.
    # Returns None if not found or error.
    # Dict results include: aliases[], banner, firstAired, id, network, overview, seriesName, status
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/search/series?name={}'.format(name), headers=headers, proxies=proxies)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                return None
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetSeries(self, series_id=None, log=None):
    # Returns a json result with the series records containing all information known about a particular series id.
    # Returns None if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/series/%s' %series_id, headers=headers, proxies=proxies)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                return None
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetEpisodesSummary(self, series_id=None, log=None):
    # Returns a json result summary of the episodes and seasons available for the series.
    # Returns None if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/series/%s/episodes/summary' %series_id, headers=headers, proxies=proxies)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                return None
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetEpisodes(self, series_id=None, page=1, log=None):
    # Returns json result of TV show episode based on knowing the episode_id.
    # Returns None if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/series/%s/episodes?page=%s' %(series_id, page), headers=headers, proxies=proxies)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                return None
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None



    def GetAllEpisodes(self, series_id=None, log=None):
    # Returns json result of TV show episode based on knowing the episode_id.
    # Returns all results, not limited to TVdb's 100 results per page limitation.
    # Returns None if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            data = []
            page = 0

            while True:

                page += 1

                response = requests.get(TvdbApi2_url + '/series/%s/episodes?page=%s' %(series_id, page), headers=headers, proxies=proxies)
                if response.status_code == 200:
                    results = json.loads(response.content)
                    for result in results['data']:
                        # Make sure episode is populated.
                        if result['episodeName'] and result['firstAired']:
                            data.append(result)
                    if results['links']['next'] == null:
                        break
                else:
                    return None

            if data:
                # Sort first by Season then by Episode number.
                data = sorted(data, key=lambda k: (k['airedSeason'], k['airedEpisodeNumber']), reverse=False)

            return data
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetEpisodeDetails(self, episode_id=None, log=None):
    # Returns json result of TV show episode based on knowing the episode_id.
    # Returns None if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/episodes/%s' %episode_id, headers=headers, proxies=proxies)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                return None
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetSeriesActors(self, series_id=None, log=None):
    # Returns json result of all actors for a TV show based on knowing the series_id.
    # Returns None if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}

            response = requests.get(TvdbApi2_url + '/series/%s/actors' %series_id, headers=headers, proxies=proxies)
            if response.status_code == 200:
                result = json.loads(response.content)
                return result
            else:
                return None
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetAllEpisodesWithDetails(self, series_id=None, log=None):
    # Returns json result of all the seasons of TV show, and all the episodes based on knowing the series_id.
    # This can take some time.  A long running series like The Simpsons can take around 3 minutes to query and compile details.
    # Returns None if not found or error.
        try:
            results = self.GetAllEpisodes(series_id=series_id, log=log)
            if results == None:
                return None

            data = []

            for result in results:
                ep_id = result.get('id')
                details = self.GetEpisodeDetails(episode_id=ep_id, log=log)
                if details:
                    data.append(details)

            return data
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetSpecificEpisodeDetails(self, series_id=None, season=0, episode=0, log=None):
    # Returns json result for a single episode of a TV show based on knowing the series_id, season and episode number.
    # Returns None if not found or error.
        try:
            results = self.GetAllEpisodes(series_id=series_id, log=log)
            if results == None:
                return None

            data = {}

            for result in results:
                aired_season = result.get('airedSeason')
                aired_episode = result.get('airedEpisodeNumber')
                ep_id = result.get('id')
                if aired_season == int(season) and aired_episode == int(episode):
                    data = self.GetEpisodeDetails(episode_id=ep_id)
                    return data

            return data
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return None


    def GetImageLinks(self, series_id=None, img_type='poster', thumbnail=False, log=None):
    # Returns the TV series image links in a list, in the voted order, of the type in "img_type"..
    # "img_type" can be: poster, fanart, season, seasonwide, series.
    # "series" are actually banner images.
    # Returns the list of smaller images if "thumbnail" is True.
    # Returns empty list if not found or error.
        try:
            self.RefreshToken(log)

            headers = {'Content-Type': 'application/json',
                       'Authorization': 'Bearer %s' %self.jwt_token}
            response = requests.get(TvdbApi2_url + '/series/%s/images/query?keyType=%s' %(series_id, img_type), headers=headers, proxies=proxies)
            if response.status_code == 200:
                results = json.loads(response.content)
                # Sort by highest to lowest ratings.
                results = sorted(results['data'], key=lambda k: k['ratingsInfo']['average'], reverse=True)
                data = []
                for result in results:
                    if thumbnail:
                        data.append(TvdbImageLoc + result.get('thumbnail'))
                    else:
                        data.append(TvdbImageLoc + result.get('fileName'))
                if not data:
                    return []
                return data
            else:
                return []
        except Exception, e:
            print e
            if log:
                log.debug('*** Exception ***', exc_info=1)
            return []


    def GetUpdatedShows(self, fromTime, toTime, log=None):
    # Returns a list of what TV shows (Series ID's) that have been updated between two date.
    # Dates are in UTC Unix Epoch values.
    # If dates exceed 1 week of data, data is truncated at 1 week.
    # Example: [{"id": 291288,"lastUpdated": 1495034062},{"id": 264458,"lastUpdated": 1495034160}]
            try:
                self.RefreshToken(log)

                headers = {'Content-Type': 'application/json',
                           'Authorization': 'Bearer %s' %self.jwt_token}

                response = requests.get(TvdbApi2_url + '/updated/query?fromTime={}&toTime={}'.format(int(fromTime), int(toTime)), headers=headers, proxies=proxies)
                if response.status_code == 200:
                    result = json.loads(response.content)
                    return result.get('data', None)
                else:
                    return None
            except Exception, e:
                print e
                if log:
                    log.debug('*** Exception ***', exc_info=1)
                return None


def SaveImageFile(url, path, img_name, log=None):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        ext = url.rpartition('.')[2]
        filename = os.path.join(path, img_name) + '.' + ext
        response = requests.get(url, stream=True, proxies=proxies)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response
    except Exception, e:
        print e
        if log:
            log.debug('*** Exception ***', exc_info=1)


def GetMetaDataDict(series_id, season, episode, vid_path_file, log=None):
# Pulls the episode show meta data from the TVDB.
# Returns all the data in a single dictionary.
# Returns "None" if error.
    try:
        tvdb = theTVDB()

        season = int(season)
        episode = int(episode)

        data = {}

        # Dictionary (file) version of this data format.
        data['Version'] = 2

        meta = tvdb.GetSeries(series_id=series_id)
        if meta and meta.get('data'):
            data['Show'] = meta.get('data', '')
        else:
            data['Show'] = {}
        #print json.dumps(data['Show'], sort_keys=False, indent=4)

        meta = tvdb.GetSpecificEpisodeDetails(series_id=series_id, season=season, episode=episode)
        if meta and meta.get('data'):
            data['Details'] = meta.get('data', '')
        else:
            data['Details'] = {}
        data['Details']['seasonNumber'] = season
        data['Details']['episodeNumber'] = episode
        #print json.dumps(data['Details'], sort_keys=False, indent=4)

        # Get links to show images:
        data['Images'] = {}
        data['Images']['poster'] = tvdb.GetImageLinks(series_id=series_id, img_type='poster', thumbnail=False)
        data['Images']['fanart'] = tvdb.GetImageLinks(series_id=series_id, img_type='fanart', thumbnail=False)
        data['Images']['banner'] = tvdb.GetImageLinks(series_id=series_id, img_type='series', thumbnail=False)

        meta = tvdb.GetSeriesActors(series_id=series_id)
        if meta and meta.get('data'):
            data['Actors'] = meta.get('data', '')
        else:
            data['Actors'] = {}
        #print json.dumps(data['Actors'], sort_keys=False, indent=4)

        if isMediaInfoAvail:
            data['Video'] = MediaInfo.GetVideoInfo(vid_path_file)
            #print json.dumps(data['Video'], sort_keys=False, indent=4)
        else:
            data['Video'] = {}

        # Expand episode thumbnail path if available.
        value = data['Details'].get('filename', '')
        if value:
            data['Details']['filename'] = TvdbImageLoc + value

        # Expand lanuage abbreviation.
        value = getFromDict(data, ["Details", "language", 'overview'], '')
        if value:
            value = LangNameFromAbbrev(value)
            data['Details']['language']['overview'] = value

        #print json.dumps(data, sort_keys=False, indent=4)

        return data
    except Exception, e:
        print e
        if log:
            log.debug('*** Exception ***', exc_info=1)
        return None


def CreateSageMetaData(series_id, season, episode, vid_path_file, log=None):
# Creates a ".my" and ".properties" SageTV formatted meta data files.
# The intention is to create the files for Imported Video purposes, not as a Sage Recording.
# Overwrites an existing file.
    try:
        tvdb = theTVDB()

        season = int(season)
        episode = int(episode)

        dict = tvdb.GetSeries(series_id=series_id)
        show = dict.get('data', None)
        #print json.dumps(show, sort_keys=False, indent=4)
        if not show:
            return False

        dict = tvdb.GetSpecificEpisodeDetails(series_id=series_id, season=season, episode=episode)
        details = dict.get('data', None)
        details['seasonNumber'] = season
        details['episodeNumber'] = episode
        #print json.dumps(details, sort_keys=False, indent=4)
        if not details:
            return False

        dict = tvdb.GetSeriesActors(series_id=series_id)
        actors = dict.get('data', None)
        #print json.dumps(actors, sort_keys=False, indent=4)
        if not actors:
            return False

        if isMediaInfoAvail:
            vidinfo = MediaInfo.GetVideoInfo(vid_path_file)
            #print json.dumps(vidinfo, sort_keys=False, indent=4)
        else:
            vidinfo = {}

        # Save the episode thumbnail if available.
        value = details.get('filename', '')
        if value:
            SaveImageFile(TvdbImageLoc + value, os.path.dirname(vid_path_file), os.path.basename(vid_path_file.rpartition('.')[0]), log=None)

        # Write ".my" meta data file.

        # Create the filename for ".my" based on the supplied video file name.
        filename = vid_path_file.rpartition('.')[0] + '.my'
        file = io.open(filename, mode='wt', encoding='cp1252')

        value = show.get('seriesName', '')
        file.write(u'title=%s\n' %value)

        value = details.get('episodeName', '')
        file.write(u'TVEpisode=%s\n' %value)

        value = details.get('seasonNumber', '')
        file.write(u'SeasonNumber=%s\n' %value)
        file.write(u'TVSeasonNumber=%s\n' %value)

        value = details.get('episodeNumber', '')
        file.write(u'EpisodeNumber=%s\n' %value)
        file.write(u'TVEpisodeNumber=%s\n' %value)

        value = details.get('overview', '')
        if value:
            value = value.replace('\n', '').replace('\r', '')
        else:
            value = ''
        file.write(u'TVOverview=%s\n' %value)
        file.write(u'overview=%s\n' %value)

        value = '/'.join(show.get('genre', ''))
        file.write(u'TVGenre=%s\n' %value)

        value = show.get('', '')
        file.write(u'TVChannelNumber=%s\n' %value)

        value = show.get('network', '')
        file.write(u'TVChannelName=%s\n' %value)

        value = show.get('', '')
        file.write(u'TVChannelDescription=%s\n' %value)

        value = ''
        for i, person in enumerate(actors):
            value += person.get('name', '') + ' -- '
            value += person.get('role', '')
            if len(actors) - 1 != i:
                 value +=  ', '
        file.write(u'TVActors=%s\n' %value)
        file.write(u'actors=%s\n' %value)

        value = ', '.join(details.get('guestStars', ''))
        file.write(u'TVGuest=%s\n' %value)

        value = ', '.join(details.get('directors', ''))
        file.write(u'TVDirector=%s\n' %value)

        value = ', '.join(details.get('writers', ''))
        file.write(u'TVWriter=%s\n' %value)

        value = ', '.join(details.get('producers', ''))
        file.write(u'TVExecutiveProducer=%s\n' %value)

        value = getFromDict(details, ["language", 'overview'], '')
        value = LangNameFromAbbrev(value)
        file.write(u'TVLanguage=%s\n' %value)

        value = details.get('firstAired', '0')
        file.write(u'TVOriginalAiringDate=%s\n' %value)
        file.write(u'TVStartDate=%s\n' %value)

        value = show.get('airsTime', '')
        file.write(u'TVStartTime=%s\n' %value)

        value = show.get('', '')
        file.write(u'TVEndTime=%s\n' %value)

        value = show.get('runtime', '0')
        file.write(u'TVDuration=%s\n' %value)

        value = details.get('', 'true')
        file.write(u'TVFirstRun=%s\n' %value)

        value = show.get('', 'false')
        file.write(u'TVFavorite=%s\n' %value)

        value = show.get('', 'false')
        file.write(u'TVManual=%s\n' %value)

        value = show.get('', 'true')
        file.write(u'TVLibrary=%s\n' %value)

        value = details.get('id', '')  # This must be blank so SageTV doesn't look it up and match to an existing DB entry.
        file.write(u'TVExternalID=%s\n' %value)

        value = vidinfo.get('summary', '')
        file.write(u'MediaFormatFull=%s\n' %value)

        value = vidinfo.get('file_type', '')
        file.write(u'MediaFormat=%s\n' %value)

        value = vidinfo.get('video_format', '')
        file.write(u'MediaVideo=%s\n' %value)

        value = vidinfo.get('aspect_ratio', '')
        file.write(u'MediaAspect=%s\n' %value)

        value = vidinfo.get('resolution', '')
        file.write(u'MediaResolution=%s\n' %value)

        value = vidinfo.get('audio_format', '')
        file.write(u'MediaAudio=%s\n' %value)

        value = vidinfo.get('audio_channels', '')
        file.write(u'MediaChannels=%s\n' %value)

        value = vid_path_file
        file.write(u'MediaFileFull=%s\n' %value)

        value = os.path.basename(vid_path_file)
        file.write(u'MediaFile=%s\n' %value)

        file.close()

        # Write ".properties" meta data file.

        filename = vid_path_file + '.properties'
        file = io.open(filename, mode='wt', encoding='cp1252')

        file.write(u'#Generator: VideoHB - %s\n' %GetDateTimeString())
        file.write(u'PropertiesWrittenBy=VideoHB\n')
        file.write(u'ScrapedBy=VideoHB\n')

        value = int(time.time()) * 1000
        file.write(u'ScrapedDate=%s\n' %value)

        value = show.get('seriesName', '')
        file.write(u'Title=%s\n' %value)

        value = details.get('episodeName', '')
        file.write(u'EpisodeName=%s\n' %value)

        value = details.get('seasonNumber', '')
        file.write(u'SeasonNumber=%s\n' %value)

        value = details.get('episodeNumber', '')
        file.write(u'EpisodeNumber=%s\n' %value)

        value = details.get('overview', '')
        if value:
            value = value.replace('\n', '').replace('\r', '')
        else:
            value = ''
        file.write(u'Description=%s\n' %value)

        value = '/'.join(show.get('genre', ''))
        file.write(u'Genre=%s\n' %value)

        value = details.get('firstAired', '0')
        value = LongDate(value) * 1000
        file.write(u'OriginalAiringDate=%s\n' %value)

        value = show.get('runtime', '0')
        value = int(value) * 60 * 1000
        file.write(u'RunningTime=%s\n' %value)

        value = ''
        for i, person in enumerate(actors):
            value += person.get('name', '') + ' -- '
            value += person.get('role', '')
            if len(actors) - 1 != i:
                 value +=  ';'
        file.write(u'Actor=%s\n' %value)

        value = ';'.join(details.get('guestStars', ''))
        file.write(u'Guest\ Star=%s\n' %value)

        value = ';'.join(details.get('directors', ''))
        file.write(u'Director=%s\n' %value)

        value = ';'.join(details.get('writers', ''))
        file.write(u'Writer=%s\n' %value)

        value = ';'.join(details.get('producers', ''))
        file.write(u'Executive\ Producer=%s\n' %value)

        value = getFromDict(details, ["language", 'overview'], '')
        value = LangNameFromAbbrev(value)
        file.write(u'Language=%s\n' %value)

        file.write(u'MediaProviderID=tvdb\n')

        value = show.get('id', '')
        file.write(u'SeriesInfoID=%s\n' %value)

        value = details.get('airedSeasonID', '')
        file.write(u'MediaProviderDataID=%s\n' %value)

        value = show.get('imdbId', '')
        file.write(u'SeriesIMDBID=%s\n' %value)

        value = details.get('imdbId', '')
        file.write(u'IMDBID=%s\n' %value)

        value = show.get('zap2itId', '')
        file.write(u'zap2itId=%s\n' %value)

        # This must be blank so SageTV doesn't look it up and match to an existing DB entry.
        # We want this show to be independent from Airings.
        # But normally this would be the 'zap2itId' value.
        value = details.get('id', '')
        file.write(u'ExternalID=%s\n' %value)

        value = show.get('rating', '')
        file.write(u'ParentalRating=%s\n' %value)

        file.close()

        return True
    except Exception, e:
        print e
        if log:
            log.debug('*** Exception ***', exc_info=1)
        return False


def CreateTvShowNfo(series_id, path, log=None):
# Creates the series meta data:
#   Kodi style "tvshow.nfo" xml file.
#   Image files (the highest rated on tvdb.)
# Overwrites existing files.
    try:
        tvdb = theTVDB()

        dict = tvdb.GetSeries(series_id=series_id)
        show = dict.get('data', None)
        #print json.dumps(show, sort_keys=False, indent=4)
        if not show:
            return False

        dict = tvdb.GetSeriesActors(series_id=series_id)
        actors = dict.get('data', None)
        #print json.dumps(actors, sort_keys=False, indent=4)
        if not actors:
            return False

        poster = tvdb.GetImageLinks(series_id=series_id, img_type='poster', thumbnail=False)
        fanart = tvdb.GetImageLinks(series_id=series_id, img_type='fanart', thumbnail=False)
        banner = tvdb.GetImageLinks(series_id=series_id, img_type='series', thumbnail=False)
        season_all_poster = tvdb.GetImageLinks(series_id=series_id, img_type='season', thumbnail=False)
        season_all_banner = tvdb.GetImageLinks(series_id=series_id, img_type='seasonwide', thumbnail=False)

        if poster:
            SaveImageFile(poster[0], path, 'poster', log=log)

        if fanart:
            SaveImageFile(fanart[0], path, 'fanart', log=log)

        if banner:
            SaveImageFile(banner[0], path, 'banner', log=log)

        if season_all_poster:
            SaveImageFile(season_all_poster[0], path, 'season-all-poster', log=log)

        if season_all_banner:
            SaveImageFile(season_all_banner[0], path, 'season-all-banner', log=log)

        filename = os.path.join(path, 'tvshow.nfo')
        file = io.open(filename, mode='wt', encoding='cp1252')

        file.write(u'<tvshow>\n')

        value = show.get('seriesName', '')
        file.write(u'\t<title>%s</title>\n' %value)

        value = show.get('siteRating', '')
        file.write(u'\t<rating>%s</rating>\n' %value)

        value = show.get('firstAired', '')
        file.write(u'\t<year>%s</year>\n' %value[:4])

        value = show.get('firstAired', '')
        file.write(u'\t<premiered>%s</premiered>\n' %value)

        value = show.get('overview', '')
        if value:
            value = value.replace('\n', '').replace('\r', '')
        file.write(u'\t<plot>%s</plot>\n' %value)

        value = '%s/%s/series/%s/all/en.zip' %(TvdbApi1_url, tvdb_api_key, series_id)
        file.write(u'\t<episodeguide>%s</episodeguide>\n' %value)
        file.write(u'\t<episodeguideurl>%s</episodeguideurl>\n' %value)

        value = show.get('id', '')
        file.write(u'\t<id>%s</id>\n' %value)

        value = '1'
        file.write(u'\t<indexer>%s</indexer>\n' %value)

        value = show.get('network', '')
        file.write(u'\t<studio>%s</studio>\n' %value)

        value = show.get('rating', '')
        file.write(u'\t<mpaa>%s</mpaa>\n' %value)

        value = show.get('status', '')
        file.write(u'\t<status>%s</status>\n' %value)

        value = show.get('imdbId', '')
        file.write(u'\t<imdbid>%s</imdbid>\n' %value)

        for value in show.get('genre', ''):
            file.write(u'\t<genre>%s</genre>\n' %value)

        for actor in actors:
            file.write(u'\t<actor>\n')
            value = actor.get('name', '')
            file.write(u'\t\t<name>%s</name>\n' %value)
            value = actor.get('role', '')
            file.write(u'\t\t<role>%s</role>\n' %value)
            value = TvdbImageLoc + actor.get('image', '')
            file.write(u'\t\t<thumb>%s</thumb>\n' %value)
            file.write(u'\t</actor>\n')

        value = GetDateTimeString()
        file.write(u'\t<dateadded>%s</dateadded>\n' %value)

        file.write(u'</tvshow>\n')

        file.close()

        return True
    except Exception, e:
        print e
        if log:
            log.debug('*** Exception ***', exc_info=1)
        return False


def CreateEpisodeNfo(series_id, season, episode, vid_path_file, log=None):
# Creates the TV show episode meta data:
#   Kodi style "...nfo" xml file.
#   Thumbnail image file if available.
# Overwrites existing files.
    try:
        tvdb = theTVDB()

        dict = tvdb.GetSeries(series_id=series_id)
        show = dict.get('data', None)
        #print json.dumps(show, sort_keys=False, indent=4)
        if not show:
            return False

        dict = tvdb.GetSpecificEpisodeDetails(series_id=series_id, season=season, episode=episode)
        details = dict.get('data', None)
        details['seasonNumber'] = season
        details['episodeNumber'] = episode
        #print json.dumps(details, sort_keys=False, indent=4)
        if not details:
            return False

        dict = tvdb.GetSeriesActors(series_id=series_id)
        actors = dict.get('data', None)
        #print json.dumps(actors, sort_keys=False, indent=4)
        if not actors:
            return False

        # Save the episode thumbnail if available.
        value = details.get('filename', '')
        if value:
            SaveImageFile(TvdbImageLoc + value, os.path.dirname(vid_path_file), os.path.basename(vid_path_file.rpartition('.')[0]), log=None)

        # Create the filename for ".nfo" based on the supplied video file name.
        filename = vid_path_file.rpartition('.')[0] + '.nfo'
        file = io.open(filename, mode='wt', encoding='cp1252')

        file.write(u'<episodedetails>\n')

        value = details.get('episodeName', '')
        file.write(u'\t<title>%s</title>\n' %value)

        value = show.get('seriesName', '')
        file.write(u'\t<showtitle>%s</showtitle>\n' %value)

        value = details.get('siteRating', '')
        file.write(u'\t<rating>%s</rating>\n' %value)

        value = details.get('seasonNumber', '')
        file.write(u'\t<season>%s</season>\n' %value)

        value = details.get('episodeNumber', '')
        file.write(u'\t<episode>%s</episode>\n' %value)

        value = details.get('id', '')
        file.write(u'\t<uniqueid>%s</uniqueid>\n' %value)

        value = details.get('overview', '')
        if value:
            value = value.replace('\n', '').replace('\r', '')
        file.write(u'\t<plot>%s</plot>\n' %value)

        value = show.get('runtime', '')
        file.write(u'\t<runtime>%s</runtime>\n' %value)

        value = TvdbImageLoc + details.get('filename', '')
        file.write(u'\t<thumb>%s</thumb>\n' %value)

        value = show.get('firstAired', '')
        file.write(u'\t<premiered>%s</premiered>\n' %value)

        value = details.get('firstAired', '')
        file.write(u'\t<aired>%s</aired>\n' %value)

        value = show.get('network', '')
        file.write(u'\t<studio>%s</studio>\n' %value)

        value = show.get('rating', '')
        file.write(u'\t<mpaa>%s</mpaa>\n' %value)

        value = ', '.join(details.get('directors', ''))
        file.write(u'\t<director>%s</director>\n' %value)

        value = ', '.join(details.get('writers', ''))
        file.write(u'\t<credits>%s</credits>\n' %value)

        value = ', '.join(details.get('producers', ''))
        file.write(u'\t<producer>%s</producer>\n' %value)

        for value in details.get('guestStars', ''):
            file.write(u'\t<actor>\n')
            file.write(u'\t\t<name>%s</name>\n' %value)
            file.write(u'\t</actor>\n')

        for actor in actors:
            file.write(u'\t<actor>\n')
            value = actor.get('name', '')
            file.write(u'\t\t<name>%s</name>\n' %value)
            value = actor.get('role', '')
            file.write(u'\t\t<role>%s</role>\n' %value)
            value = TvdbImageLoc + actor.get('image', '')
            file.write(u'\t\t<thumb>%s</thumb>\n' %value)
            file.write(u'\t</actor>\n')

        value = GetDateTimeString()
        file.write(u'\t<dateadded>%s</dateadded>\n' %value)

        file.write(u'</episodedetails>\n')

        file.close()

        return True
    except Exception, e:
        print e
        if log:
            log.debug('*** Exception ***', exc_info=1)
        return False


def CacheActorImages(actors, cache_dir, force=False, log=None):
# Pass the Actors dict from theTVdb dict, and it will download
# the actor images to the "cache_dir" if those images don't exist yet.
# The actors dict is returned with the image locations modified.
    for actor in actors:
        if not actor.get('image', ''):
            continue
        id = str(actor.get('id'))
        link = actor.get('image')
        ext = link.rpartition('.')[2]
        local_file = os.path.join(cache_dir, id + '.' + ext)
        if force or not os.path.isfile(local_file):
            try:
                SaveImageFile(TvdbImageLoc + link, cache_dir, id, log=log)
            except Exception, e:
                print 'ERROR: SaveImageFile: {0}'.format(e)
        actor['thumbnail'] = local_file
    return actors


def GetNameFromTvdb(tvdbid, log=None):
# Get the TV show name for the TVdb ID.
    try:
        tvdb = theTVDB()

        dict = tvdb.GetSeries(series_id=tvdbid)
        show = dict.get('data', None)
        #print json.dumps(show, sort_keys=False, indent=4)
        if not show:
            return 'Unknown'

        name = show.get('seriesName', '')
        aired = show.get('firstAired', '')
        
        return '{} ({})'.format(name, aired[:4])

    except Exception, e:
        print e
        if log:
            log.debug('*** Exception ***', exc_info=1)
        return False


