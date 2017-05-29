import xbmc
import json
import common


def GetTvShows():
# Kodi calls the TVdb ID "imdbnumber".
    try:
        json_param = '{"id": "libTvShows", "jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["imdbnumber", "title", "year"], "sort": {"order": "ascending", "method": "title"}}}'
        json_response = xbmc.executeJSONRPC(json_param)
        result = json.loads(json_response)
        return result
    except Exception, e:
        print e
        return None


def GetTvShowID(tvdbid):
# The "tvshowid" is the index ID that Kodi uses in it's database for referencing TV shows and movies.
# Kodi calls the TVdb ID "imdbnumber" in it's database.
    data = GetTvShows()
    shows = common.getFromDict(data,['result', 'tvshows'], [])
    for show in shows:
        if show.get('imdbnumber') == str(tvdbid):
            return show.get('tvshowid', '')
    return None


def GetEpisodeInfo(tvshowid):
# Gets json object of all episodes info for a given "tvshowid".
# "tvshowid" is the Kodi ID number for a TV show.
    try:
        json_param = '{"jsonrpc": "2.0", "id": "libEpisodes", "method": "VideoLibrary.GetEpisodes", "params":{"tvshowid": %s, "properties":["tvshowid","showtitle","title","season", "episode","plot","rating","firstaired","runtime","art","streamdetails","file","playcount","resume"]}}' %(tvshowid)
        json_response = xbmc.executeJSONRPC(json_param)
        result = json.loads(json_response)
        return result
    except Exception, e:
        print e
        return None


def GetEpisodePath(tvdbid, season, episode):
# The "tvshowid" is the index ID that Kodi uses in it's database for referencing TV shows and movies.
    tvshowid = GetTvShowID(tvdbid)
    if not tvshowid:
        return None
    data = GetEpisodeInfo(tvshowid)
    if not data:
        return None
    eps = common.getFromDict(data,['result', 'episodes'], [])
    for ep in eps:
        if ep.get('season') == int(season) and ep.get('episode') == int(episode):
            return ep.get('file', '')
    return None




