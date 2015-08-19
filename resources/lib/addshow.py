import sys
import urllib
import xbmc
import xbmcgui
import sickbeard
import resources.lib.common as common
import resources.lib.settings as settings


# Initialize Sickbeard Class
Sickbeard = sickbeard.SB()


def showSearchDialog(show_name):
    # Get search text from user.
    if show_name:
        text = show_name
        return text
    keyboard = xbmc.Keyboard('', 'Find a show on the TVDB', False)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        text = keyboard.getText()
    else:
        text = ''
    return text  

  
# Add show main function. Shows the initial search window. 
def AddShow(show_name):
    text = showSearchDialog(show_name)
    if (text == ''):
        return
    
    # Search for the show using SB search API.
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        search_results = Sickbeard.SearchShowName(urllib.quote_plus(text))
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    if search_results == []:
        common.CreateNotification(header="Show Search", message="No results for that query.", icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=True)
        return
    
    # Select one of the possible shows from the list.
    selected_show = ShowSelectMessage(search_results)
    if (selected_show == -1):
        return
        
    print 'Selected Add Show: ' + search_results[selected_show]['name'] + ' ' + str(search_results[selected_show]['tvdbid'])

    # Check if show already exists in the show list.
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        shows = Sickbeard.GetShows()
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    for show in shows:
        if search_results[selected_show]['name'] == show['show_name']:
            header = 'Duplicate Show'
            msg = "'" + search_results[selected_show]['name'] + "' already exists in your show list."
            ShowMessage(header, msg)
            print header + ': ' + msg
            return

    # "Pick the parent folder" prompt.
    root_dir = SelectRootDirMessage()
    if (root_dir == -1):
        return
        
    print 'Add Show Root Dir: ' + root_dir

    # sb.getdefaults for status of show eps.  Need to make each option selectable so you can change initial status, folders, quality.
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        default_status, default_folders, default_quality = Sickbeard.GetDefaults()
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        
    print 'Add Show Retrieved Defaults'
    
    # Set status for previously aired episodes.
    prev_aired_status = SetStatus("Status for previously aired episodes", default_status)
    if (prev_aired_status == -1):
        return
        
    print 'Add Show Set Prev Status: ' + str(prev_aired_status)

    # Set status for future episodes.
    future_status = ''
    if (settings.__servertype__ == "SickRage"):
        future_status = SetStatus("Status for all future episodes", "wanted")
        if (future_status == -1):
            return

    print 'Add Show Set Future Status: ' + str(future_status)

    # "Use season folders?" prompt.
    flatten_folders = SetFlattenFolders(default_folders)
    if (flatten_folders == -1):
        return

    print 'Add Show Set Season Folders: ' + str(flatten_folders)

    # "Set initial status of episodes" prompt.
    quality = SetQualityMessage(default_quality)
    if (quality == -1):
        return
  
    print 'Add Show Set Quality: ' + str(quality)

    tvdbid = search_results[selected_show]['tvdbid']
    xbmc.executebuiltin("ActivateWindow(busydialog)")
    try:
        ret = Sickbeard.AddNewShow(tvdbid, root_dir, prev_aired_status, future_status, flatten_folders, quality)
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    header = 'Add Show'
    if ret == "success":
        msg = "Successfully added "+search_results[selected_show]['name']
        ShowMessage(header, msg)
        print header + ': ' + msg
    else:
        ShowMessage(header, msg)
        msg = "Failed to add "+search_results[selected_show]['name']
        print header + ': ' + msg


# Search results selection window
def ShowSelectMessage(shows):
    formatted_shows = []
    for show in shows:
        try:
            show_name = ""+show['name']
        except TypeError:
            continue
        try:
            first_aired = ""+show['first_aired']
        except TypeError:
            first_aired = "Unknown"
        formatted_shows.append(show_name+"  -  ("+first_aired+")")
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Search Results", formatted_shows)
    return ret


# Basic show message window
def ShowMessage(header, text):
    dialog = xbmcgui.Dialog()
    dialog.ok(header, text)


# Gets the root dirs from SB then shows selection window
def SelectRootDirMessage():
    directory_result = Sickbeard.GetRoodDirs()
    directories = []
    for location in directory_result:
        directories.append(location['location'])
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Pick the parent folder", directories)
    if (ret == -1):
        return ret
    else:
        return directories[ret]


# Set Status for previously aired episodes.
def SetStatus(title, status):
    org_list = ["wanted", "skipped", "archived", "ignored"]
    status_list = list(org_list)  # Make a copy of the list to alter for the menu.
    for each in status_list:
        if each == status:
            index = status_list.index(status)
            status_list[index] = status + " (Default)"
    dialog = xbmcgui.Dialog()
    ret = dialog.select(title, status_list)
    if (ret == -1):
        return ret
    else:
        return org_list[ret]


# Use season folders selection window
def SetFlattenFolders(flatten_folders):
    if flatten_folders == 1:
        list = ["Yes (no season folders)", "No (episodes folder-grouped by season)"]
    else:
        list = ["No (episodes folder-grouped by season)", "Yes (no season folders)"]
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Flatten files (no folders)", list)
    if (ret == -1):
        return ret
    elif (ret == 0):
        if flatten_folders == 1:
            return True
        else:
            return False
    elif (ret == 1):
        if flatten_folders == 1:
            return False
        else:
            return True
  

# Set initial episode quality window
def SetQualityMessage(quality):
    anyList = [u'sdtv', u'sddvd', u'hdtv', u'fullhdtv', u'hdwebdl', u'fullhdwebdl', u'hdbluray', u'fullhdbluray', u'unknown']
    sdList = [u'sdtv', u'sddvd']
    hdList = [u'hdtv', u'fullhdtv', u'hdwebdl', u'fullhdwebdl', u'hdbluray', u'fullhdbluray']
    if all(x in quality for x in anyList):
        quality_list = ["Any (Default)", "SD", "HD"]
    elif all(x in quality for x in sdList):
        quality_list = ["Any", "SD (Default)", "HD"]
    else:
        quality_list = ["Any", "SD", "HD (Default)"]
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Preferred quality of episodes to be downloaded", quality_list)
    if (ret == -1):
        return ret
    if (ret == 0):
        return 'sdtv|sddvd|hdtv|rawhdtv|fullhdtv|hdwebdl|fullhdwebdl|hdbluray|fullhdbluray|unknown'
    elif (ret == 1):
        return 'sdtv|sddvd'
    else:
        return 'hdtv|rawhdtv|fullhdtv|hdwebdl|fullhdwebdl|hdbluray|fullhdbluray'


if (sys.argv[1] == 'new'):
    # Execute the add show process
    AddShow("")
    # Refresh the directory listing after adding a show
    xbmc.executebuiltin("Container.Refresh")
