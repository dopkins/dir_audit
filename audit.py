# -*- coding: cp1252 -*-
# A simple gui to run the directory checks written 
import wx,sys,os,codecs,re,urllib2,hashlib
from PyPDF2 import PdfFileReader as pdf
from types import *
import xml.etree.ElementTree as ET
from xml.dom import minidom



class MD5:
    # function to check md5 hashes
    def getMd5(self, filename):
        hashvalue = hashlib.md5(open(filename, 'rb').read()).hexdigest()
        return hashvalue
        filename.close()
        
    def list_unchecked_folders(self, dirlist, startfolder, subpath=''):
        """walks through the start folder one more time and creates a list of excluded dirs"""
        dirs_in_config = [] # misnomer here, but used to generate list of all dirs with files to check against config
        dirs_really_not_in_config = []
        self.traverse_dir(startfolder, dirs_in_config, len(startfolder))
        for d in dirs_in_config:
            if d not in dirlist: # if a dir is found that wasn't entered to the config
                dirs_really_not_in_config.append(d)

            elif dirlist[d].strip() == '': # if the config doesn't have anything for the check dir
                dirs_really_not_in_config.append(d)
        print 'final dir check done'
        return dirs_really_not_in_config

# Walk through a path and use the config to check whether the files on 2 paths are the same
    def check_sameness(self, dirlist, startfolder, verbose=False): 
        files_log = []
        for each_dir in dirlist.iterkeys():
            clean_config = each_dir.strip()
            if dirlist[each_dir].strip() != '':
                for root, dirs, files in os.walk(startfolder + clean_config):
                    
                    for f in files:
                        other_path_file = dirlist[each_dir].strip() + '\\' + root[len(startfolder + clean_config+'1'):] + '\\' + f
                        # Note: can't use os.path.join for other_path_file because of \\  / mixing...

                        # Extract path/subfolders from the starting folder, discard folders up to the subpath from key
                        # Then put it on the end of the FS_path component and add the file
                        path_without_startfolder = os.path.join(root,f)[len(startfolder):]
                        if os.path.exists(other_path_file):
                            dvdmd5 = self.getMd5(os.path.join(root,f))
                            fsmd5 = self.getMd5(other_path_file)
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
    def prettify(self, elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ')

    # find folders that contain files that aren't only html or pdf.
    # once one of these folders is found, skip to next folder.
    # needed because os.walk doesn't do the job for my purposes.
    def traverse_dir(self, currfolder='.', dirs_in_config=[], len_cutoff=0):
        file_found = False
        for f in os.listdir(currfolder): # Add a dir to the list if it contains appropriate files and hasn't been added yet
            if os.path.isfile(os.path.join(currfolder,f)) and not f.endswith('.pdf') and not f.endswith('.html') and file_found == False:
                if len(currfolder) != len_cutoff: # don't stop the recursive check with the dvd base dir
                    dirs_in_config.append(currfolder[len_cutoff:])
                    file_found = True
        if file_found == False: # If the dir wasn't added to the list, go through the dir again and rerun the test on all child dirs
            for d in os.listdir(currfolder):
                if os.path.isdir(os.path.join(currfolder,d)):
                    self.traverse_dir(os.path.join(currfolder,d), dirs_in_config, len_cutoff)

    # create a dvd file map, if it doesn't yet exist
    def create_config(self, startfolder):
        configfile = codecs.open('config.xml', 'w', 'utf-8')
        
        xmlroot = ET.Element('config')
        dirs_in_config = []
        self.traverse_dir(startfolder,dirs_in_config,len(startfolder))
        for key in dirs_in_config: # convert dict to xml
            item = ET.SubElement(xmlroot, 'item')
            dvd_path = ET.SubElement(item, 'dvd_path')
            dvd_path.text = key
            fs_path = ET.SubElement(item, 'fs_path')
            fs_path.text = '  '
        configfile.write(self.prettify(xmlroot))
        print 'Config created'

    # read the config items into a dict
    def read_config(self, configfile):
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

    def write_log(self, hash_results, unchecked_folders, startfolder):
        """Create a log file with the results of the checks"""
        log = codecs.open('MD5_Check_Log_{0}.html'.format(startfolder[startfolder.rfind('\\')+1:]), 'w', 'utf-8')
        log.write('<!DOCTYPE html>\n<html>\n<head><meta charset="UTF-8">\n')
        log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
        log.write('</style></head>\n<body>\n')
        log.write('<h1>Protokoll MD5 Vergleich: {0}</h1><hr>'.format(startfolder[startfolder.rfind('\\')+1:]))
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

        

class LINK:
    # Select the type of log event... avoids a million if statements
    def add_(self, type_html, text, cont):
        if type_html == 'index':
            cont['index_files'].append(text)
        elif type_html == 'impressum':
            cont['impressum_files'].append(text)
        else:
            cont['misc_htmls'].append(text)
        return cont

# recursively go through a path and analyze the links in the html files
    def list_htmls(self, path, cont={}):
        cont.setdefault('err_internal_links',[])
        cont.setdefault('err_external_links',[])
        cont.setdefault('email_list',[])
        cont.setdefault('index_files',[])
        cont.setdefault('impressum_files',[])
        cont.setdefault('misc_htmls',[])
            
        for f in os.listdir(path):
            type_html = '' # index_, impressum_, other?
            if os.path.isdir(os.path.join(path,f)):
                self.list_htmls(os.path.join(path, f), cont)
            elif f.endswith('.html'):
                if f.startswith('index'):
                    cont['index_files'].append(os.path.join(path, f) + '</td><td>')
                    type_html = 'index'
                elif f.startswith('impressum'):
                    cont['impressum_files'].append(os.path.join(path, f)+ '</td><td>')
                    type_html = 'impressum'
                else:
                    cont['misc_htmls'].append(os.path.join(path, f)+ '</td><td>')
                    type_html = 'other'

                htmlfile = open(os.path.join(path,f))
                urls = re.findall('href="(.+?)"', htmlfile.read()) # regex to find a href=
                #urls = re.findall(r'.*"(.+\.com)', htmlfile.read())
                for url in urls:
                    if type_html != 'other':
                        extracted = url

                        if extracted.startswith('http'): # links to external websites
                            try:
                                urllib2.urlopen(extracted)
                                cont = self.add_(type_html, '------%s</td><td>' % extracted, cont)
                            except urllib2.HTTPError, e:
                                cont = self.add_(type_html, '------%s</td><td bgcolor="red">---- HTTP ERROR' % extracted, cont)
                            except urllib2.URLError, e:
                                cont = self.add_(type_html,  '------%s</td><td bgcolor="red">---- URL ERROR' % extracted, cont)
                                
                        elif extracted.startswith('mailto:'): #email links, log but don't test
                            cont = self.add_(type_html, '------%s</td><td>-- EMAIL LINK' % extracted[7:], cont)
                            cont['email_list'].append(os.path.join(path, f) + '</td><td>' + extracted[7:])
                            
                        else: # link type ../../etc, test links to installers/documents/other pages
                            temp_path = os.path.join(path, extracted.decode('utf-8'))
                            
                            if os.path.exists(temp_path):
                                cont = self.add_(type_html, '------%s</td><td>' % temp_path, cont)
                            else:
                                cont = self.add_(type_html, '------%s</td><td bgcolor="red">---- NICHT GEFUNDEN' % temp_path, cont)
                                if type_html != 'other':
                                    cont['err_internal_links'].append(temp_path)
                htmlfile.close()
                if type_html != 'other':
                    cont = self.add_(type_html, '</td></tr></table><hr><table><tr><td>', cont)

        return cont

    #create logfile/insert header data
    def write_log(self, startfolder, cont):
        
        log = codecs.open('linklist_%s.html' % startfolder[startfolder.rfind('\\')+1:], 'w', 'utf-8')
        log.write('<!DOCTYPE html>\n<html>\n<head><meta charset="UTF-8">\n')
        log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
        log.write('</style></head>\n<body>\n')
        log.write('<h1>HTML Protokoll: %s</h1><hr>' % startfolder[startfolder.rfind('\\')+1:])
        log.write(u'<p><b>Hinweis</b>: nur index_ und impressum_ Dateien sind hier berücksichtigt.')


        # Add link errors to top of log
        log.write('<h2>Fehlerhafte interne Links:</h2>\n')
        log.write('<table><th>Pfad/Dateiname</th><tr><td bgcolor="red">\n')
        

        log.write('</td></tr><tr><td bgcolor="red">'.join(cont['err_internal_links']))
        log.write('</td></tr></table><hr>')

        log.write('<h2>Fehlerhafte externe Links:</h2>\n')
        log.write('<table><th>Pfad/Dateiname</th><tr><td bgcolor="red">\n')
        log.write('</td></tr><tr><td bgcolor="red">'.join(cont['err_external_links']))
        log.write('</td></tr></table><hr>')


        #Add list of e-mail addresses on the pages
        log.write('<h2>E-mail links in HTMLs:</h2>\n')
        log.write('<table><th>Pfad/Dateiname</th><th>Adresse</th><tr><td>\n')
        log.write('</td></tr><tr><td>'.join(cont['email_list']))
        log.write('</td></tr></table><hr>')

        #Add list of index_ files with complete list of links
        log.write('<h2>In Index-Dateien befindliche Links:</h2>\n')
        log.write('<table><th>Pfad/Dateiname/Link</th><th>Anmerkungen</th><tr><td>\n')
        log.write('</td></tr><tr><td>'.join(cont['index_files']))
        log.write('</td></tr></table><hr>')

        #Add list of impressum_ files with complete list of links
        log.write('<h2>In Impressum-Dateien befindliche Links:</h2>\n')
        log.write('<table><th>Pfad/Dateiname/Link</th><th>Anmerkungen</th><tr><td>\n')
        log.write('</td></tr><tr><td>'.join(cont['impressum_files']))
        log.write('</td></tr></table><hr>')

        #Add simple list of other htmls on the dvd
        log.write('<h2>Andere HTML-Dateien:</h2>\n')
        log.write('<table><th>Pfad/Dateiname</th><tr><td>\n')
        log.write('</td></tr><tr><td>'.join(cont['misc_htmls']))
        log.write('</td></tr></table><hr>')


        log.close()
        print 'Link-Protokoll fertig'

    
class DOC:
    def create_doku_list(self, startfolder):
        doku_list = []

        for root, dirs, files in os.walk(startfolder):
            for f in files:
                if f.endswith('.pdf'):
                    fullpath = os.path.join(root, f)
                    printpath = fullpath.encode('utf-8')
                    docfile = open(fullpath, 'rb')
                    doc = pdf(docfile)
                    try:
                        rawdate = doc.getDocumentInfo()['/CreationDate'][2:10]
                        doku_list.append(printpath + "</td><td>{0}-{1}-{2}".format(rawdate[:4],rawdate[4:6],rawdate[6:]))
                    except:
                        doku_list.append(printpath + "</td><td bgcolor='red'>Couldn't get info")
                    docfile.close()
        return doku_list

    # write log file
    def write_log(self, doku_list, startfolder):
            
        log = codecs.open('PDF_List_%s.html' % startfolder[startfolder.rfind('\\')+1:], 'w', 'utf-8')
        log.write('<!DOCTYPE html>\n<html>\n<head><meta charset="UTF-8">\n')
        log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
        log.write('</style></head>\n<body>\n')
        log.write('<h1>Protokoll Dokumentation: %s</h1><hr>' % startfolder[startfolder.rfind('\\')+1:])
        log.write(u'<p><b>Hinweis</b>: nur PDF-Dateien sind hier berücksichtigt.')


        # Add documentation
        log.write('<table><th>Pfad/Dateiname</th><th>Erstelldatum<tr><td>\n')

        log.write('</td></tr><tr><td>'.join(doku_list).decode('utf-8')) 
        log.write('</td></tr></table><hr>')


        log.close()
        print 'doku log erstellt'

def editMd5s(e):
    pass

def runChecks(e):
    if type(e) == StringType:
        runMD5check(unicode(e)) # The type of the input needs to match for encoding/decoding to work
        runDokuList(unicode(e))
        runLinkList(unicode(e))
    else:
        if os.path.isdir(loadField.Value):
            if chkDoku.Value == True: runDokuList(loadField.Value)
            if chkMd5.Value == True: runMD5check(loadField.Value)
            if chkLinkList.Value == True: runLinkList(loadField.Value)
            print 'Done!'

def runMD5check(startfolder, configfile='config.xml'):
    """use the methods in 'uptodate_folders.py' to generate an MD5 report"""
    if not os.path.exists(configfile):
        MD5().create_config(startfolder)
    else:
        md5inst = MD5()
        config = md5inst.read_config(configfile)
        try: # only can be set from GUI, I know, bad style but it works here.
            if chkVerbose.Value == True:
                hash_results = md5inst.check_sameness(config,startfolder, True)
            else:
                hash_results = md5inst.check_sameness(config, startfolder, False)
        except: # occurs every time if run from command line
            hash_results = md5inst.check_sameness(config, startfolder, False)
        unchecked_folders = md5inst.list_unchecked_folders(config, startfolder)
        md5inst.write_log(hash_results, unchecked_folders, startfolder)
        
def runDokuList(startfolder):
    doclist = DOC()
    docs = doclist.create_doku_list(startfolder)
    doclist.write_log(docs, startfolder)

def runLinkList(startfolder):
    linklist = LINK()
    links = linklist.list_htmls(startfolder)
    linklist.write_log(startfolder, links)



def selectDir(e):
    dlg = wx.DirDialog(None, 'Select Directory')
    if dlg.ShowModal() == wx.ID_OK:
        loadField.Value = dlg.GetPath()
        dlg.Destroy()

# either run the program with an argument (d-n-d or from command line)
# or as a GUI version
argument = sys.argv
if len(argument) > 1:
    print 'CLI argument: ' + argument[1]
    runChecks(argument[1])
    sys.exit(0)


# GUI elements
# Line 0: menu items
# Line 1: load dvd dir
# Line 2-n: CLI options
# Line 'last': Convert button
app = wx.App()
win = wx.Frame(None, title='Directory audit tools', size=(600,250))

# Initialize menu items
menubar = wx.MenuBar()
editMenu = wx.Menu()
editMenu.Append(100, '&MD5-Prüfungen bearbeiten')
win.Bind(wx.EVT_MENU, editMd5s, id=100)
menubar.Append(editMenu, '&Bearbeiten')
win.SetMenuBar(menubar)

bkg = wx.Panel(win)

loadLbl = wx.StaticText(bkg, label='DVD-Verzeichnis auswählen: ')
loadField = wx.TextCtrl(bkg)
loadBtn = wx.Button(bkg, id=1, label='Durchsuchen')
loadBtn.Bind(wx.EVT_BUTTON, selectDir)

# Options
chkDoku = wx.CheckBox(bkg, label='Liste der Dokumentationen erzeugen')
chkLinkList = wx.CheckBox(bkg, label='Liste der Links in HTML-Seiten erzeugen')
chkMd5 = wx.CheckBox(bkg, label='MD5-Prüfung durchführen')
chkVerbose = wx.CheckBox(bkg, label='Verbose (alle Dateien auflisten)')



# 'RUN!' button
convertBtn = wx.Button(bkg, label='Ausführen')
convertBtn.SetFont(wx.Font(12,wx.DEFAULT, wx.NORMAL, wx.BOLD))
convertBtn.Bind(wx.EVT_BUTTON, runChecks)



#horizontal-vertical layout
lineOne = wx.BoxSizer()
lineOne.Add(loadLbl, proportion=0, flag=wx.LEFT, border=5)
lineOne.Add(loadField, proportion=1, flag=wx.EXPAND, border=5)
lineOne.Add(loadBtn, proportion=0, flag=wx.LEFT, border=5)

lineTwo = wx.BoxSizer()
lineTwo.Add(chkDoku, proportion=0, flag=wx.LEFT, border=5)

lineThree = wx.BoxSizer()
lineThree.Add(chkLinkList, proportion=0, flag=wx.LEFT, border=5)

lineFour = wx.BoxSizer()
lineFour.Add(chkMd5, proportion=0, flag=wx.LEFT, border=5)
lineFour.Add(chkVerbose, proportion=0, flag=wx.LEFT, border=5)


lineLast = wx.BoxSizer()
lineLast.Add(convertBtn, proportion=0, flag=wx.LEFT, border=5)


vBox = wx.BoxSizer(wx.VERTICAL)
vBox.Add(lineOne, proportion=0, flag=wx.EXPAND | wx.ALL, border = 10)
vBox.Add(lineTwo, proportion=0, flag=wx.EXPAND | wx.ALL, border = 5)
vBox.Add(lineThree, proportion=0, flag=wx.EXPAND | wx.ALL, border = 5)
vBox.Add(lineFour, proportion=0, flag=wx.EXPAND | wx.ALL, border = 5)

vBox.Add(lineLast, proportion=0, flag=wx.EXPAND | wx.ALL, border = 5)

bkg.SetSizer(vBox)

win.Show()
app.MainLoop()

