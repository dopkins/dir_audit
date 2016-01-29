import os, re
import urllib2

contents = []
email_list = []
index_files = []
misc_htmls = []

def add_(status, text):
    if status == True:
        index_files.append(text)
    else:
        misc_htmls.append(text)

# recursively go through a path and analyze the links in the html files
def list_htmls(path):
    for f in os.listdir(path):
        main = False # is it an index_lang file or not?
        if os.path.isdir(os.path.join(path,f)):
            list_htmls(os.path.join(path, f))
        elif f.endswith('.html'):
            if f.startswith('index'):
                index_files.append(f)
                main = True
            else:
                misc_htmls.append(f)

            htmlfile = open(os.path.join(path,f))
            urls = re.findall('href="(.+?)"', htmlfile.read())
            #urls = re.findall(r'.*"(.+\.com)', htmlfile.read())
            for url in urls:
                if 2 == 2:
                    extracted = url
                    #if '"' in extracted: # should deal with links like <a href="blah blah blah"target="blank_">
                        #print '" found, something went wrong ' + extracted
                        #extracted = extracted[:extracted.index('"')]

                    if extracted.startswith('http'):
                        try:
                            #urllib2.urlopen(extracted)
                            if main:
                                index_files.append('-- %s link works!' % extracted)
                            else:
                                misc_htmls.append('-- %s link works!' % extracted)
                        except urllib2.HTTPError, e:
                            if main:
                                index_files.append('---- %s HTTP ERROR' % extracted)
                            else:
                                misc_htmls.append('---- %s HTTP ERROR' % extracted)
                            #contents.append(str(e.code))
                        except urllib2.URLError, e:
                            if main:
                                index_files.append('---- %s URL ERROR' % extracted)
                            else:
                                misc_htmls.append('---- %s URL ERROR' % extracted)
                            #contents.append(str(e.args))
                    elif extracted.startswith('mailto:'):
                        if main:
                            index_files.append('--%s EMAIL LINK' % extracted[7:])
                        else:
                            misc_htmls.append('--%s EMAIL LINK' % extracted[7:])

                    else:
                        if os.path.exists(extracted):
                            if main:
                                index_files.append('-- %s' % extracted)
                            else:
                                misc_htmls.append('-- %s' % extracted)
                        else:
                            add_(main, '---- %s NOT FOUND' % extracted)                            

            htmlfile.close()

        
list_htmls('./')
log = open('logfile.txt', 'w')
log.write('\n'.join(contents))
log.write('Index files:\n-------------------\n')
log.write('\n'.join(index_files))
log.write('\n\n\nMisc_htmls:\n--------------------\n')
log.write('\n'.join(misc_htmls))
log.close()
print 'done'
