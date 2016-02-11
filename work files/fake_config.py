# file just copies the entries on 'dvd_path' in an EXISTING CONFIGURATION
# into the 'fs_path'. Only to be used for testing.

import xml.etree.ElementTree as ET
import codecs

configfile = codecs.open('config.xml', 'r', 'utf-8')

tree = ET.parse(configfile)
xmlroot = tree.getroot()

for item in xmlroot.iter('item'):
    item.find('fs_path').text = item.find('dvd_path').text

newconfig = codecs.open('confignew.xml', 'w', 'utf-8')
newconfig.write(ET.tostring(xmlroot, 'utf-8'))
print 'done'
