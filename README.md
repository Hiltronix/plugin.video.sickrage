# plugin.video.sickrage
#### SickRage/SickBeard Interface Add-on for Kodi/XBMC  

This is an add-on/plugin for the Kodi/XBMC Home Theatre software.  
It allows the user to view and control SickRage or SickBeard from within Kodi/XBMC, add new shows and view show/episode details.

-----

## Kodi/XBMC Repo  
The repository for this add-on can be found here:  

https://github.com/Hiltronix/repo/

OR

https://hiltronix.com/xbmc/

-----

## Related Links

#### SickRage Website:  
https://www.sickrage.tv

#### SickRage Project on GitHub:  
https://github.com/SiCKRAGETV/SickRage

-----

## Plug-in API  

#### Add New Show by ID for theTVDB.com:  

    RunPlugin(plugin://plugin.video.sickrage?action=addshow&tvdb_id=TVDB_ID)

#### Add New Show by TV show title:  

    RunPlugin(plugin://plugin.video.sickrage?action=addshow&show_name=SHOW_NAME)

-----

## Known Issues  

#### TV Show Cast Members:  
- TV show information shows cast member names from theTVdb.com but no cast member images.  
- TV episode information shows neither cast member names or images.  
- This is a current limitation of the metahandler library I'm using from TV show/episode lookups.  The author Eldorado may add these features in an upcoming release.  

#### SickBeard Limitations & Issues:  
- Sickbeard does not (and devs won't add) a function call to retrieve the API key, so hackish screen scraping is required to auto-retrieve the API Key.  
  This may break, so manual entry of API Key may be required.  
- The SickBeard API returns images in thumbnail size (small/low-res) unless a startup parameter is used of '--noresize' without the quotes.  
- The SickBeard API does not allow for retrieving the backlog list at this time.  

-----

## Donations  

If you'd like to make a donation to help support this project and keep it current, please click [here](https://hiltronix.com/donations/).  

-----

## Images  

[![Screen Show 1](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_1sm.jpg)](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_1.jpg)  
[![Screen Show 2](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_2sm.jpg)](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_2.jpg)  
[![Screen Show 3](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_3sm.jpg)](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_3.jpg)  
[![Screen Show 4](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_4sm.jpg)](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_4.jpg)  
[![Screen Show 5](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_5sm.jpg)](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_5.jpg)  
[![Screen Show 6](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_6sm.jpg)](https://github.com/Hiltronix/repo/blob/master/images/sickrage_addon_6.jpg)  

-----

## Note  

This add-on/plugin for Kodi/XBMC is an updated version of the Sickbeard plugin originally created by Zach Moore.  It expands on his original work starting at his version 1.0.10.  
http://forum.kodi.tv/showthread.php?tid=124808   

