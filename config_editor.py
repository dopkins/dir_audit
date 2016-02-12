# -*- coding: cp1252 -*-
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys, codecs, wx

class EDITOR:
    def prettify(self, elem):
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ')

    def parse_config(self,configfile):
        """read in the config file into a python dictionary"""
        dirlist = {}
        try:
            xmlroot = ET.parse(configfile).getroot()
        except:
            print 'Error encountered - try recreating the config file...'
            sys.exit(0)
        for item in xmlroot.iter('item'):
            dirlist[ item.find('dvd_path').text.strip() ] = item.find('fs_path').text.strip()
        return dirlist

    def write_config(self,dirlist):
        configfile = codecs.open('configddd.xml','w','utf-8')
        xmlroot = ET.Element('config')
        for key in dirlist.iterkeys():
            item = ET.SubElement(xmlroot, 'item')
            dvd_path = ET.SubElement(item, 'dvd_path')
            dvd_path.text = key
            fs_path = ET.SubElement(item, 'fs_path')
            if dirlist[key] == '':
                dirlist[key] = '  '
            fs_path.text = dirlist[key]
        configfile.write(self.prettify(xmlroot))
        print 'Config edited'


def selectDir(e):
    pass

def saveText(e): # happens when the entry in the combo box changes
    dickt[choices[dvdField.Selection]] = fieldFs.Value

def changeText(e):
    fieldFs.Value = dickt[choices[dvdField.Selection]]

def delEntry(e): # Probably going overboard with vars and actions by this point - refactoring possible
    currVal = dvdField.Selection
    del dickt[choices[currVal]]
    del choices[currVal]
    dvdField.Delete(currVal)
    dvdField.Value = choices[currVal] # new entry by now
    fieldFs.Value = dickt[choices[currVal]]

def saveConfig(e):
    EDITOR().write_config(dickt)
    

x = 'config.xml'


ed = EDITOR()

dickt = ed.parse_config(x)
choices = list(dickt.iterkeys())

app = wx.App()
win = wx.Frame(None, title='Config file editor', size = (800, 400))

bkg = wx.Panel(win)

dvdField = wx.ComboBox(bkg, id = 1, value = choices[0], style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=choices)
dvdField.Bind(wx.EVT_COMBOBOX_DROPDOWN, saveText)
dvdField.Bind(wx.EVT_COMBOBOX, changeText)

lblFs = wx.StaticText(bkg, label='Verzeichnis für den Vergleich: ')
fieldFs = wx.TextCtrl(bkg)
fieldFs.Value = dickt[choices[0]]
btnFs = wx.Button(bkg, id=2, label='Durchsuchen')
btnFs.Bind(wx.EVT_BUTTON, selectDir)

delButton = wx.Button(bkg, id=3, label='Eintrag löschen')
delButton.Bind(wx.EVT_BUTTON, delEntry)

saveButton = wx.Button(bkg, id=4, label='Config speichern')
saveButton.Bind(wx.EVT_BUTTON, saveConfig)

lineOne = wx.BoxSizer()
lineOne.Add(dvdField, proportion=1, flag=wx.EXPAND, border=5)

lineTwo = wx.BoxSizer()
lineTwo.Add(lblFs, proportion=0, flag=wx.LEFT, border=5)
lineTwo.Add(fieldFs, proportion=1, flag=wx.EXPAND, border=5)
lineTwo.Add(btnFs, proportion=0, flag=wx.LEFT, border=5)

lineThree = wx.BoxSizer()
lineThree.Add(delButton, proportion=0, flag=wx.LEFT, border=5)

lineFour = wx.BoxSizer()
lineFour.Add(saveButton, proportion=0, flag=wx.LEFT, border=5)


vBox = wx.BoxSizer(wx.VERTICAL)
vBox.Add(lineOne, proportion=0, flag=wx.EXPAND | wx.ALL, border = 10)
vBox.Add(lineTwo, proportion=0, flag=wx.EXPAND | wx.ALL, border= 5)
vBox.Add(lineThree, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
vBox.Add(lineFour, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
bkg.SetSizer(vBox)

win.Show()
app.MainLoop()

