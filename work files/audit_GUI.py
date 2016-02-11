# -*- coding: cp1252 -*-
# A simple gui to run the directory checks written 
import wx
import sys
import os
from types import *
import docu_list as DOC
import link_visualization2 as LINK
import uptodate_folders as MD5

def editMd5s(e):
    pass

def runChecks(e):
    if type(e) == StringType:
        runMD5check(e)
        runDokuList(e)
        runLinkList(e)
    else:
        if os.path.isdir(loadField.Value):
            print 'Determined value: ' + loadField.Value
            if chkDoku.Value == True: runDokuList(loadField.Value)
            if chkMd5.Value == True: runMD5check(loadField.Value)
            if chkLinkList.Value == True: runLinkList(loadField.Value)
            print 'Done!'

def runMD5check(startfolder, configfile='config.xml'):
    """use the methods in 'uptodate_folders.py' to generate an MD5 report"""
    if not os.path.exists(configfile):
        MD5.create_config(startfolder)
    else:
        config = MD5.read_config(configfile)
        hash_results = MD5.check_sameness(config, startfolder, False)
        unchecked_folders = MD5.list_unchecked_folders(config, startfolder)
        MD5.write_log(hash_results, unchecked_folders, startfolder)
        
def runDokuList(startfolder):
    docs = DOC.create_doku_list(startfolder)
    DOC.write_log(docs, startfolder)

def runLinkList(startfolder):
    links = LINK.list_htmls(startfolder)
    LINK.write_log(startfolder, links)



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

