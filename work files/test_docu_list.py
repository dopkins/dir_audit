# -*- coding: iso-8859-1 -*-
import codecs, sys, os, re
from PyPDF2 import PdfFileReader as pdfr
from PyPDF2 import pdf as pdf


doku_list = []

tlog = codecs.open('regex_.log', 'w', 'iso-8859-1')

for root, dirs, files in os.walk('./'):
    for f in files:
        if f.endswith('.pdf'):
            fullpath = os.path.join(root, f)
            printpath = fullpath.decode('iso-8859-1')
            docfile = open(fullpath, 'rb')
            doc = pdfr(docfile)
            try:
                page_1 = doc.getPage(0).extractText()
 
##                if re.search('en|de|fr(.*)]', ''.join(page_1)): # Handbuch
##                    res = re.search('en|de|fr(.*)\]', ''.join(page_1)).group(1)
##                    tlog.write(fullpath + ' ||||| ' + res + '\n')
                if re.search('(Programmversion|Program version|Version de programme).*:(.*)\]', ''.join(page_1)): # Entwicklerdoku
                    res = re.search('(Programmversion|Program version|Version de programme).*:(.*)\]', ''.join(page_1)).group(2)
                    #print  'Entwicklerdoku: ' + results
                    tlog.write(fullpath + ' ||| ' + res + '\n')
                #elif re.search('[0-9]{2}\.[0-9]{2}\.[0-9]{4}\.'
                else:
                    print fullpath
                    err_log = open('./errors/' + f + '.log', 'w')
                    err_log.write(page_1)
                    err_log.close()
                rawdate = doc.getDocumentInfo()['/CreationDate'][2:10]
                doku_list.append(printpath + "</td><td>{0}-{1}-{2}".format(rawdate[:4],rawdate[4:6],rawdate[6:]))
            except:
                doku_list.append(printpath + "</td><td bgcolor='red'>Couldn't get info")
            docfile.close()
tlog.close()


# write log file                      
log = codecs.open('PDF_List_%s.html' % 'replace_with_folder_name', 'w', 'iso-8859-1')
log.write('<!DOCTYPE html>\n<html>\n<head>\n')
log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
log.write('</style></head>\n<body>\n')
log.write('<h1>Protokoll Dokumentation: %s</h1><hr>' % 'also replace with folder name')
log.write(u'<p><b>Hinweis</b>: nur PDF-Dateien sind hier berücksichtigt.')


# Add documentation
log.write('<table><th>Pfad/Dateiname</th><th>Erstelldatum<tr><td>\n')
log.write('</td></tr><tr><td>'.join(doku_list))
log.write('</td></tr></table><hr>')


log.close()
print 'done'
