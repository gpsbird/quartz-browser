# -*- coding: utf-8 -*-

def parsebookmarks(filename):
    try:
        bmkfile = open(filename, 'r')
    except:
        return [["Google", "http://www.google.com"], ["Facebook", "https://m.facebook.com"]]
    bmk_lines = bmkfile.readlines()
    bmkfile.close()
    bmk_list = []
    bmk = []
    for line in bmk_lines:
        line = line[:-1]
        bmk.append(line)
        if len(bmk) == 2:
            bmk_list.append(bmk)
            bmk = []
    return bmk_list

def writebookmarks(filename, bookmarks):
    bmkfile = open(filename, 'w')
    for item in bookmarks:
        bmk = item[0] + "\n" + item[1] + "\n"
        bmkfile.write(bmk)
    bmkfile.close()

def parseDownloads(filename):
    try:
        dwnld_file = open(filename, 'r')
    except:
        return []
    dwnld_lines = dwnld_file.readlines()
    dwnld_file.close()
    dwnld_list = []
    dwnld = []
    for line in dwnld_lines:
        line = line[:-1]
        dwnld.append(line)
        if len(dwnld) == 3:
            dwnld_list.append(dwnld)
            dwnld = []
    return dwnld_list

def writeDownloads(filepath, downloads):
    dl_text = ''
    for download in downloads:
        if download.complete==False:
            dl_text = dl_text+download.filepath+'\n'+download.url+'\n'+str(download.totalsize)+'\n'
    dl_file = open(filepath, 'w')
    dl_file.write(dl_text)
    dl_file.close()
