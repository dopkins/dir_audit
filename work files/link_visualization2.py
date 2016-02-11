# -*- coding: iso-8859-1 -*-
import os, re, codecs
import urllib2

    
# Select the type of log event... avoids a million if statements
def add_(type_html, text, cont):
    if type_html == 'index':
        cont['index_files'].append(text)
    elif type_html == 'impressum':
        cont['impressum_files'].append(text)
    else:
        cont['misc_htmls'].append(text)
    return cont

# recursively go through a path and analyze the links in the html files
def list_htmls(path, cont={}):
    cont.setdefault('err_internal_links',[])
    cont.setdefault('err_external_links',[])
    cont.setdefault('email_list',[])
    cont.setdefault('index_files',[])
    cont.setdefault('impressum_files',[])
    cont.setdefault('misc_htmls',[])
        
    for f in os.listdir(path):
        type_html = '' # index_, impressum_, other?
        if os.path.isdir(os.path.join(path,f)):
            list_htmls(os.path.join(path, f), cont)
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
                    #if '"' in extracted: # should deal with links like <a href="blah blah blah"target="blank_">
                        #print '" found, something went wrong ' + extracted
                        #extracted = extracted[:extracted.index('"')]

                    if extracted.startswith('http'): # links to external websites
                        try:
                            #urllib2.urlopen(extracted)
                            cont = add_(type_html, '------%s</td><td>' % extracted, cont)
                        except urllib2.HTTPError, e:
                            cont = add_(type_html, '------%s</td><td bgcolor="red">---- HTTP ERROR' % extracted, cont)
                        except urllib2.URLError, e:
                            cont = add_(type_html,  '------%s</td><td bgcolor="red">---- URL ERROR' % extracted, cont)
                            
                    elif extracted.startswith('mailto:'): #email links, log but don't test
                        cont = add_(type_html, '------%s</td><td>-- EMAIL LINK' % extracted[7:], cont)
                        cont['email_list'].append(os.path.join(path, f) + '</td><td>' + extracted[7:])
                        
                    else: # link type ../../etc, test links to installers/documents/other pages
                        temp_path = os.path.join(path, extracted).decode('utf8')
                        if os.path.exists(temp_path):
                            cont = add_(type_html, '------%s</td><td>' % temp_path, cont)
                        else:                        
                            cont = add_(type_html, '------%s</td><td bgcolor="red">---- NICHT GEFUNDEN' % temp_path, cont)
                            if type_html != 'other':
                                cont['err_internal_links'].append(temp_path)
            htmlfile.close()
            if type_html != 'other':
                cont = add_(type_html, '</td></tr></table><hr><table><tr><td>', cont)

    return cont
    
        

#create logfile/insert header data
def write_log(startfolder, cont):
    
    log = codecs.open('linklist_%s.html' % startfolder, 'w', 'iso-8859-1')
    log.write('<!DOCTYPE html>\n<html>\n<head>\n')
    log.write('<style>table, th, td {border: 1px solid black; border-collapse: collapse;}\n')
    log.write('</style></head>\n<body>\n')
    log.write('<h1>HTML Protokoll: %s</h1><hr>' % startfolder)
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
