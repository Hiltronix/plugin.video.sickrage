from xml.dom.minidom import parse
import os
import shutil

# Create a backup of original file.
file_name = 'C:\\Users\\Carey\\AppData\\Roaming\\Kodi\\userdata\\advancedsettings.xml'
bak_file_name = new_file_name + ".bak"
shutil.copyfile(file_name, bak_file_name)

# Change text value of element.
try:
    doc = parse(file_name)
    #node = doc.getElementsByTagName('videolibrary\hideemptyseries')
    #node[0].firstChild.nodeValue = 'false'

    videolibrary = doc.getElementsByTagName("videolibrary")
    for item in videolibrary:
        hideemptyseries = item.getElementsByTagName("hideemptyseries")[0]

    print hideemptyseries.firstChild.data

    hideemptyseries.firstChild.data = 'true'

except:
    pass

# Persist changes to new file.
xml_file = open(new_file_name, "w")
doc.writexml(xml_file, encoding="utf-8")
xml_file.close()
