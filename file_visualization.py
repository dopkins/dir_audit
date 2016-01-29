# -*- coding: utf-8 -*-
import os, codecs

# This function goes through a directory and either recursively
def dir_walk(level, currdir, lCont):
    for f in os.listdir(currdir):
        if os.path.isdir(f):
            lCont.append( 'dir: ' + level+ f)
            dir_walk(level+'--',currdir + '/' + f, lCont)
        else:
            lCont.append( 'file: ' + level + f)

#initialize variables
level = 0
log = 'log.html'
currdir = './'
lCont = []

# initialize log file
lCont.append('<!DOCTYPE html><html>')
lCont.append('<head>')
lCont.append('<style>')
lCont.append('</style>')
lCont.append('</head>')
lCont.append('<body>')
lCont.append('asdf')
dir_walk('',currdir, lCont)
lCont.append('</body></html>')



logfile = codecs.open(log, mode='w', encoding='iso-8859-1')
logfile.write(codecs.encode('\n'.join(lCont), 'utf-8', 'ignore'))
logfile.close()
