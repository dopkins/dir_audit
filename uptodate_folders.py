import xml.etree.ElementTree as ET
from xml.dom import minidom
import os, codecs, hashlib, sys

# list of dvd languages - add to arbitrarily later
def langs():
    return ['de','en','fr','all']

# function to check md5 hashes
def getMd5(filename):
    hashvalue = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    return hashvalue
    filename.close()

# Go through the dict of dvd dirs and fs dirs, hash check each directory
def check_sameness(dirlist, startfolder):
    simplelog = open('test.txt', 'w')
    for directory in dirlist.iterkeys():
        for f in os.listdir(os.path.join(startfolder,directory)):
            simplelog.write(os.path.join(startfolder,directory,f)+'\n')
    print 'done'
    

# proper indentation function for config file
def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')


# create a dvd file map, if it doesn't yet exist
def create_config(startfolder):
    configfile = codecs.open('config.xml', 'w', 'utf-8')
    
    xmlroot = ET.Element('config')
    #itme = ET.SubElement(xmlroot, 'item')
    for root, dirs, files in os.walk(startfolder):
        for d in dirs:
            if d.lower() in langs():
                 item = ET.SubElement(xmlroot, 'item')
                 dvd_path = ET.SubElement(item, 'dvd_path')
                 dvd_path.text = os.path.join(root,d)[len(startfolder):].decode('cp1252')
                 fs_path = ET.SubElement(item, 'fs_path')
                 fs_path.text = '  '
    
    configfile.write(prettify(xmlroot))
    print 'Config created'

# Check the config file against the DVD to make sure it contains all items
def update_config(dirlist, configfile, startfolder):
    try:
        tree = ET.parse(configfile)
    except:
        print 'problem encountered, exiting.'
        sys.exit(0)
    xmlroot = tree.getroot()
    reload_config = False
    for root, dirs, files in os.walk(startfolder):
        for d in dirs:
            if d.lower() in langs():
                foldername = os.path.join(root,d)[len(startfolder):].decode('cp1252')
                if foldername not in dirlist:
                    print 'added config item: ' + foldername
                    item = ET.SubElement(xmlroot, 'item')
                    dvd_path = ET.SubElement(item, 'dvd_path')
                    dvd_path.text = foldername
                    fs_path = ET.SubElement(item, 'fs_path')
                    fs_path.text = '  '
                    reload_config = True
    if reload_config:
        codecs.open(configfile, 'w', 'utf-8').write(xmlroot)
        read_config(configfile)
                    
                    

# read the config items into a dict
def read_config(configfile):
    dirlist = {}
    tree = ET.parse(configfile)
    xmlroot = tree.getroot()
    for item in xmlroot.iter('item'):
        dirlist[ item.find('dvd_path').text ] = item.find('fs_path').text
    return dirlist
    update_config(dirlist, xmlroot, startfolder)



startfolder = './DVD_ELOprofessional_2015-07-29/'
configfile = 'config.xml'
if not os.path.exists(configfile):
    create_config(startfolder)
else:
    config = read_config(configfile)
    update_config(config, configfile, startfolder)
    check_sameness(config, startfolder)
    
