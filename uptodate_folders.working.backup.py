# -*- coding: cp1252 -*-
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

##def check_dir(orig_path, check_path):
##    """Goes through a directory recursively and checks the hash value between
##the common files in both values. Returns ???"""
##    for f in os.listdir(orig_path):
##        
##        if os.path.isfile(

# Go through the dict of dvd dirs and fs dirs, hash check each directory

def list_unchecked_folders(dirlist, startfolder):
    """walks through the start folder one more time and creates a list of excluded dirs"""
    temp_dirs_dict = {}
    not_checked = []
    for root, dirs, files in os.walk(startfolder):
        for d in dirs:

            for f in os.listdir(os.path.join(root,d)):

                
                if os.path.isfile(os.path.join(root,d, f)) and not f.endswith('.pdf') and not f.endswith('.html'):
                    temp_dirs_dict[os.path.join(root,d)] = 'placeholder'
    for check_dir in temp_dirs_dict.iterkeys():
        print check_dir
        if check_dir[len(startfolder):] not in dirlist:
            not_checked.append(check_dir[len(startfolder):])
    print 'final dir check done'
    return not_checked


def check_sameness(dirlist, startfolder): # Note: maybe add "verbose" option later - probably not needed though...
    files_log = []
    #simplelog = open('test.txt', 'w')
    for each_dir in dirlist.iterkeys():
        for root, dirs, files in os.walk(os.path.join(startfolder,each_dir)):
            for f in files:
                #simplelog.write(os.path.join(root,f) + '\n')
                other_path_file = dirlist[each_dir] + '\\' + root[len(os.path.join(startfolder,each_dir)):] + '\\' + f
                # Note: can't use os.path.join for other_path_file because of \\  / mixing :-/
                #simplelog.write(other_path_file + '\n')

                # Extract path/subfolders from the starting folder, discard folders up to the subpath from key
                # Then put it on the end of the FS_path component and add the file
                if os.path.exists(other_path_file):
                    dvdmd5 = getMd5(os.path.join(root,f))
                    fsmd5 = getMd5(other_path_file)
                    #simplelog.write(dvdmd5 + '\n')
                    #simplelog.write(fsmd5 + '\n')
                    if dvdmd5 == fsmd5:
                        pass #simplelog.write('md5 match\n')
                    else:
                        files_log.append(os.path.join(root,f)[len(startfolder):] + '</td><td bgcolor="red">MD5 MISMATCH')
                        #simplelog.write('md5 NO MATCH\n')
                else:
                    files_log.append(os.path.join(root,f)[len(startfolder):] + '</td><td bgcolor="orange">Datei nicht gefunden!')
                    #simplelog.write('File on alt path doesn\'t exist!!!\n')
                #simplelog.write('\n\n')
    #simplelog.close()
    print 'hash check done'
    return files_log
    

# proper indentation function for config file
def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')


# create a dvd file map, if it doesn't yet exist
def create_config(startfolder):
    configfile = codecs.open('config.xml', 'w', 'utf-8')
    
    xmlroot = ET.Element('config')
    dirs_with_files = {}
    for root, dirs, files in os.walk(startfolder): # inefficiently create a dict entry for each dir* with a (non-PDF) file
        for d in dirs:
            for entry in os.listdir(os.path.join(root,d)):
                tmp_p = os.path.join(root,d,entry)
                print tmp_p
                if os.path.isfile(tmp_p) and not entry.endswith('.pdf') and tmp_p.count('\\') in [5,6] :
                    # *Note: only take 'level 6 Dateiebene' files into account. e.g.
                    # Start\Client\Java\Install\Java_linux\ELO_Java_Client_Linux.zip.
                    # IMPORTANT: all directories before "Start" must use forward slashes, or else you need to
                    # adjust the control.
                    dirs_with_files[os.path.join(root,d)[len(startfolder):].decode('cp1252')] = '  '
                    continue
    for key in dirs_with_files.iterkeys(): # convert dict to xml
        item = ET.SubElement(xmlroot, 'item')
        dvd_path = ET.SubElement(item, 'dvd_path')
        dvd_path.text = key
        fs_path = ET.SubElement(item, 'fs_path')
        fs_path.text = '  '
    configfile.write(prettify(xmlroot))
    print 'Config created'

# Check the config file against the DVD to make sure it contains all items
# Note: This is buggy and possibly undesirable.. remove?
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
    try:
        tree = ET.parse(configfile)
    except:
        print 'Error encountered - try recreating the config file...'
        sys.exit(0)
    xmlroot = tree.getroot()
    for item in xmlroot.iter('item'):
        dirlist[ item.find('dvd_path').text ] = item.find('fs_path').text
    return dirlist

def write_log(hash_results, unchecked_folders):
    """Create a log file with the results of the checks"""
    log = codecs.open('MD5_Check_Log_{0}.html'.format('replace_with_folder_name'), 'w', 'iso-8859-1')
    log.write('<!DOCTYPE html>\n<html>\n<head>\n')
    log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
    log.write('</style></head>\n<body>\n')
    log.write('<h1>Protokoll MD5 Vergleich: {0}</h1><hr>'.format('also replace with folder name'))
    log.write(u'<p><b>Hinweis</b>: der MD5-Vergleich umfasst nur in der Konfiguration angegebene Verzeichnisse. \
Nicht überwachte Verzeichnisse, die Dateien beinhalten, sind am Ende des Protokolls gelistet.')
    #Add table with check errors
    log.write('<h2>Fehler in dem MD5-Vergleich:</h2>')
    log.write('<table><th>Pfad/Dateiname</th><th>Fehler</th><tr><td>\n')
    log.write('</td></tr><tr><td>'.join(sorted(hash_results)))
    log.write('</td></tr></table><hr>')
    #Add table with possible folders that weren't checked - audit trail
    log.write(u'<h2>Nicht überprüfte Verzeichnisse:</h2>')
    log.write('<table><th>Pfad</th><tr><td>\n')
    log.write('</td></tr><tr><td>'.join(sorted(unchecked_folders)))
    log.write('</td></tr></table><hr>')
    log.close()

startfolder = './DVD_ELOprofessional_2015-07-29/'
configfile = 'config.xml'
if not os.path.exists(configfile):
    create_config(startfolder)
else:
    config = read_config(configfile)
    #update_config(config, configfile, startfolder)
    hash_results = check_sameness(config, startfolder)
    unchecked_folders = list_unchecked_folders(config, startfolder)
    write_log(hash_results, unchecked_folders)
    print 'Operations complete.'
    
