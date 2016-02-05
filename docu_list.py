# -*- coding: iso-8859-1 -*-
import codecs, sys, os
from PyPDF2 import PdfFileReader as pdf


doku_list = []

for root, dirs, files in os.walk('./'):
    for f in files:
        if f.endswith('.pdf'):
            fullpath = os.path.join(root, f)
            printpath = fullpath.decode('iso-8859-1')
            docfile = open(fullpath, 'rb')
            doc = pdf(docfile)
            try:
                rawdate = doc.getDocumentInfo()['/CreationDate'][2:10]
                doku_list.append(printpath + "</td><td>{0}-{1}-{2}".format(rawdate[:4],rawdate[4:6],rawdate[6:]))
            except:
                doku_list.append(printpath + "</td><td bgcolor='red'>Couldn't get info")
            docfile.close()


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
