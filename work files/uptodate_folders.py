# -*- coding: cp1252 -*-
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os, codecs, hashlib, sys



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

def list_unchecked_folders(dirlist, startfolder, subpath=''):
    """walks through the start folder one more time and creates a list of excluded dirs"""
    dirs_in_config = [] # misnomer here, but used to generate list of all dirs with files to check against config
    dirs_really_not_in_config = []
    traverse_dir(startfolder, dirs_in_config, len(startfolder))
    for d in dirs_in_config:
        if d not in dirlist:
            dirs_really_not_in_config.append(d)
    print 'final dir check done'
    return dirs_really_not_in_config
    #return ['1','2']


def check_sameness(dirlist, startfolder, verbose=False): # Note: maybe add "verbose" option later - probably not needed though...
    files_log = []
    for each_dir in dirlist.iterkeys():
        for root, dirs, files in os.walk(os.path.join(startfolder,each_dir)):
            for f in files:
                other_path_file = dirlist[each_dir] + '\\' + root[len(os.path.join(startfolder,each_dir)):] + '\\' + f
                # Note: can't use os.path.join for other_path_file because of \\  / mixing...

                # Extract path/subfolders from the starting folder, discard folders up to the subpath from key
                # Then put it on the end of the FS_path component and add the file
                path_without_startfolder = os.path.join(root,f)[len(startfolder):]
                if os.path.exists(other_path_file):
                    dvdmd5 = getMd5(os.path.join(root,f))
                    fsmd5 = getMd5(other_path_file)
                    if dvdmd5 == fsmd5:
                        if verbose:
                            files_log.append( path_without_startfolder + '</td><td bgcolor="green">-- files match')
                        pass 
                    else:
                        files_log.append(path_without_startfolder + '</td><td bgcolor="red">MD5 MISMATCH')
                else:
                    files_log.append(path_without_startfolder + '</td><td bgcolor="orange">Datei nicht gefunden!')
    print 'hash check done'
    return files_log
    

# proper indentation function for config file
def prettify(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')

# find folders that contain files that aren't only html or pdf.
# once one of these folders is found, skip to next folder.
# needed because os.walk doesn't do the job for my purposes.
def traverse_dir(currfolder='.', dirs_in_config=[], len_cutoff=0):
    file_found = False
    for f in os.listdir(currfolder): # Add a dir to the list if it contains appropriate files and hasn't been added yet
        if os.path.isfile(os.path.join(currfolder,f)) and not f.endswith('.pdf') and not f.endswith('.html') and file_found == False:
            if len(currfolder) != len_cutoff: # don't stop the recursive check with the dvd base dir
                dirs_in_config.append(currfolder[len_cutoff:])
                file_found = True
    if file_found == False: # If the dir wasn't added to the list, go through the dir again and rerun the test on all child dirs
        for d in os.listdir(currfolder):
            if os.path.isdir(os.path.join(currfolder,d)):
                traverse_dir(os.path.join(currfolder,d), dirs_in_config, len_cutoff)
        
            

# create a dvd file map, if it doesn't yet exist
def create_config(startfolder):
    configfile = codecs.open('config.xml', 'w', 'utf-8')
    
    xmlroot = ET.Element('config')
    dirs_in_config = []
    #traverse_dir(os.path.join(startfolder,'Start'),dirs_in_config, len(startfolder)) # run the test from 'DVD_NAME'\'Start' or else it will stop in the root dir
    traverse_dir(startfolder,dirs_in_config,len(startfolder))
    for key in dirs_in_config: # convert dict to xml
        item = ET.SubElement(xmlroot, 'item')
        dvd_path = ET.SubElement(item, 'dvd_path')
        dvd_path.text = key
        fs_path = ET.SubElement(item, 'fs_path')
        fs_path.text = '  '
    configfile.write(prettify(xmlroot))
    print 'Config created'  

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

def write_log(hash_results, unchecked_folders, startfolder):
    """Create a log file with the results of the checks"""
    log = codecs.open('MD5_Check_Log_{0}.html'.format(startfolder), 'w', 'iso-8859-1')
    log.write('<!DOCTYPE html>\n<html>\n<head>\n')
    log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
    log.write('</style></head>\n<body>\n')
    log.write('<h1>Protokoll MD5 Vergleich: {0}</h1><hr>'.format(startfolder))
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

#startfolder = './DVD_ELOprofessional_2015-07-29/'
#configfile = 'config.xml'
##if not os.path.exists(configfile):
##    create_config(startfolder)
##else:
##    config = read_config(configfile)
##    hash_results = check_sameness(config, startfolder, True)
##    unchecked_folders = list_unchecked_folders(config, startfolder)
##    write_log(hash_results, unchecked_folders)
##    print 'Operations complete.'
    
