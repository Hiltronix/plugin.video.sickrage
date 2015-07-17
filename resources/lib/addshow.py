import sys
import xbmc
import xbmcgui
import sickbeard
import resources.lib.common as common


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
    search_results = Sickbeard.SearchShowName(text)
  finally:
    xbmc.executebuiltin("Dialog.Close(busydialog)")
  if search_results == []:
    common.CreateNotification(header="Show Search", message="No results for that query.", icon=xbmcgui.NOTIFICATION_INFO, time=5000, sound=True)
    return
    
  # Select one of the possible shows from the list.
  selected_show = ShowSelectMessage(search_results)
  if (selected_show == -1):
    return
  
  # "Pick the parent folder" prompt.
  # 1. Need to get sb.getrootdirs and select one... No adding/deleting for now, would need to browse remote dir :(  
  root_dir = SelectRootDirMessage()
  if (root_dir == -1):
    return

  # 2. sb.getdefaults for status of show eps.  Need to make each option selectable so you can change initial status, folders, quality.
  default_status, default_folders, default_quality = Sickbeard.GetDefaults()
  
  # "Set initial status of episodes" prompt.
  initial_status = SetInitialStatusMessage(default_status)
  if (initial_status == -1):
    return

  # "Use season folders?" prompt.
  use_season_folders = SetSeasonFolderMessage(default_folders)
  if (use_season_folders == -1):
    return

  # "Set initial status of episodes" prompt.
  quality = SetQualityMessage(default_quality)
  if (quality == -1):
    return
  
  tvdbid = search_results[selected_show]['tvdbid']
  ret = Sickbeard.AddNewShow(tvdbid, root_dir, initial_status, use_season_folders, quality)
  if ret == "success":
    ShowMessage("Add Show", "Successfully added "+search_results[selected_show]['name'])
  else:
    ShowMessage("Add Show", "Failed to add "+search_results[selected_show]['name'])


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


# Set initial status of show eps window
def SetInitialStatusMessage(status):
  status_list = ["wanted", "skipped", "archived", "ignored"]
  status_list_return = ["wanted", "skipped", "archived", "ignored"]
  for each in status_list:
    if each == status:
      index = status_list.index(status)
      status_list[index] = status+" (Default)"
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Set the initial status of already aired episodes", status_list)
  if (ret == -1):
    return ret
  else:
    return status_list_return[ret]


# Use season folders selection window
def SetSeasonFolderMessage(flatten_folders):
  if flatten_folders == 1:
    list = ["Yes", "No"]
  else:
    list = ["No", "Yes"]
  dialog = xbmcgui.Dialog()
  ret = dialog.select("Flatten Folders", list)
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
