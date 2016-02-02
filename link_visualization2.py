# -*- coding: iso-8859-1 -*-
import os, re, codecs
import urllib2



contents = [] # maybe delete later.
err_internal_links = []
err_external_links = []
#sidebar = [] # Sidebar could be logged separately from other links, but it requires complicated logic - add later if needed
#err_sidebar = []
email_list = []
index_files = []
impressum_files = []
misc_htmls = []

# Select the type of log event... avoids a million if statements
def add_(type_html, text):
    if type_html == 'index':
        index_files.append(text)
    elif type_html == 'impressum':
        impressum_files.append(text)
    else:
        misc_htmls.append(text)

# recursively go through a path and analyze the links in the html files
def list_htmls(path):
    for f in os.listdir(path):
        type_html = '' # index_, impressum_, other?
        if os.path.isdir(os.path.join(path,f)):
            list_htmls(os.path.join(path, f))
        elif f.endswith('.html'):
            if f.startswith('index'):
                index_files.append(os.path.join(path, f) + '</td><td>')
                type_html = 'index'
            elif f.startswith('impressum'):
                impressum_files.append(os.path.join(path, f)+ '</td><td>')
                type_html = 'impressum'
            else:
                misc_htmls.append(os.path.join(path, f)+ '</td><td>')
                type_html = 'other'

            htmlfile = open(os.path.join(path,f))
            urls = re.findall('href="(.+?)"', htmlfile.read()) # regex to find a href=
            #urls = re.findall(r'.*"(.+\.com)', htmlfile.read())
            for url in urls:
                if type_html != 'other':
                    extracted = url
                    #if '"' in extracted: # should deal with links like <a href="blah blah blah"target="blank_">
                        #print '" found, something went wrong ' + extracted
                        #extracted = extracted[:extracted.index('"')]

                    if extracted.startswith('http'): # links to external websites
                        try:
                            #urllib2.urlopen(extracted)
                            add_(type_html, '------%s</td><td>' % extracted)
                        except urllib2.HTTPError, e:
                            add_(type_html, '------%s</td><td bgcolor="red">---- HTTP ERROR' % extracted)
                        except urllib2.URLError, e:
                            add_(type_html,  '------%s</td><td bgcolor="red">---- URL ERROR' % extracted)
                            
                    elif extracted.startswith('mailto:'): #email links, log but don't test
                        add_(type_html, '------%s</td><td>-- EMAIL LINK' % extracted[7:])
                        email_list.append(os.path.join(path, f) + '</td><td>' + extracted[7:])
                        
                    else: # link type ../../etc, test links to installers/documents/other pages
                        temp_path = os.path.join(path, extracted).decode('utf8')
                        if os.path.exists(temp_path):
                            add_(type_html, '------%s</td><td>' % temp_path)
                        else:                        
                            add_(type_html, '------%s</td><td bgcolor="red">---- NICHT GEFUNDEN' % temp_path)
                            if type_html != 'other':
                                err_internal_links.append(temp_path)
            htmlfile.close()
            if type_html != 'other':
                add_(type_html, '</td></tr></table><hr><table><tr><td>')



startpos = './'        
list_htmls(startpos)

#create logfile/insert header data
log = codecs.open('linklist_%s.html' % 'replace_with_folder_name', 'w', 'iso-8859-1')
log.write('<!DOCTYPE html>\n<html>\n<head>\n')
log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
log.write('</style></head>\n<body>\n')
log.write('<h1>HTML Protokoll: %s</h1><hr>' % 'also replace with folder name')
log.write(u'<p><b>Hinweis</b>: nur index_ und impressum_ Dateien sind hier berücksichtigt.')


# Add link errors to top of log
log.write('<h2>Fehlerhafte interne Links:</h2>\n')
log.write('<table><th>Pfad/Dateiname</th><tr><td bgcolor="red">\n')
log.write('</td></tr><tr><td bgcolor="red">'.join(err_internal_links))
log.write('</td></tr></table><hr>')

log.write('<h2>Fehlerhafte externe Links:</h2>\n')
log.write('<table><th>Pfad/Dateiname</th><tr><td bgcolor="red">\n')
log.write('</td></tr><tr><td bgcolor="red">'.join(err_external_links))
log.write('</td></tr></table><hr>')


#Add list of e-mail addresses on the pages
log.write('<h2>E-mail links in HTMLs:</h2>\n')
log.write('<table><th>Pfad/Dateiname</th><th>Adresse</th><tr><td>\n')
log.write('</td></tr><tr><td>'.join(email_list))
log.write('</td></tr></table><hr>')

#Add list of index_ files with complete list of links
log.write('<h2>In Index-Dateien befindliche Links:</h2>\n')
log.write('<table><th>Pfad/Dateiname/Link</th><th>Anmerkungen</th><tr><td>\n')
log.write('</td></tr><tr><td>'.join(index_files))
log.write('</td></tr></table><hr>')

#Add list of impressum_ files with complete list of links
log.write('<h2>In Impressum-Dateien befindliche Links:</h2>\n')
log.write('<table><th>Pfad/Dateiname/Link</th><th>Anmerkungen</th><tr><td>\n')
log.write('</td></tr><tr><td>'.join(impressum_files))
log.write('</td></tr></table><hr>')

#Add simple list of other htmls on the dvd
log.write('<h2>Andere HTML-Dateien:</h2>\n')
log.write('<table><th>Pfad/Dateiname</th><tr><td>\n')
log.write('</td></tr><tr><td>'.join(misc_htmls))
log.write('</td></tr></table><hr>')


log.close()
print 'done'
