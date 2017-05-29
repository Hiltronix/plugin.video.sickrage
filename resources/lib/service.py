import xbmc
import xbmcgui
import cache
import settings


# Logging level:
log_level = xbmc.LOGDEBUG       # Un-Comment this line for production.
#log_level = xbmc.LOGERROR       # Comment out this line for production.


def ResetServiceOptions():
# Reset service options state in settings here at start time:
    settings.my_addon.setSetting('TVdbUpdateAllEpisodesEnabled', 'false')
    settings.my_addon.setSetting('TVdbUpdateAllEpisodesRunning', 'false')
    settings.my_addon.setSetting('TVdbUpdateAllEpisodesProgress', '0')


if __name__ == '__main__':

    ResetServiceOptions()
    
    # If service not required, then quit.
    if not settings.my_addon.getSetting('ServiceEnabled') == 'true':
        exit()
        
    monitor = xbmc.Monitor()

    xbmc.log('Service Starting: {}'.format(settings.pluginID), level=log_level)

    # Run service startup one-time functions here:
    cache.UpdateUpcomingEpisodes()
    cache.UpdateAllShows(AllEpisodes=True)
    cache.CheckForTVdbUpdates()

    interval = int(settings.my_addon.getSetting('ServiceInterval'))
 
    while not monitor.abortRequested():
        # Sleep/wait delay between running service routine.
        # If Kodi exit is called, we terminate service here.
        if monitor.waitForAbort(interval * 60):
            # Abort was requested while waiting.  Service routine terminates now.
            ResetServiceOptions()
            xbmc.log('Service [{}] Terminated'.format(settings.pluginID), level=log_level)
            break

        # Add service code to run after this point, 
        # on a timed schedule defined above in seconds "monitor.waitForAbort(X)".
        xbmc.log('Service [{}] Routine Executed'.format(settings.pluginID), level=log_level)

        # Pop-up alert for debugging.  Comment out the next 2 lines for production.
        #dialog = xbmcgui.Dialog()
        #dialog.ok('Service Monitor', settings.pluginID)

        cache.UpdateUpcomingEpisodes()
        cache.UpdateAllShows(AllEpisodes=False)
        cache.CheckForTVdbUpdates()
        
        if settings.my_addon.getSetting('TVdbUpdateAllEpisodesEnabled') == 'true':
            cache.UpdateAllShows(AllEpisodes=True)

