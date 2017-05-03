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
        if len(dwnld) == 4:
            dwnld_list.append(dwnld)
            dwnld = []
    return dwnld_list

def writeDownloads(filepath, downloads):
    dl_text = ''
    for [filename, url, filesize, timestamp] in downloads:
        dl_text = dl_text+filename+'\n'+url+'\n'+filesize+'\n'+timestamp+'\n'
    dl_file = open(filepath, 'w')
    dl_file.write(dl_text)
    dl_file.close()

jsPrintFriendly = """
var pfHeaderImgUrl = '';
var pfHeaderTagline = '';
var pfdisableClickToDel = 0;
var pfHideImages = 0;
var pfImageDisplayStyle = 'right';
var pfDisablePDF = 0;
var pfDisableEmail = 1;
var pfDisablePrint = 0;
var pfCustomCSS = '';
var pfBtVersion='1';
(function(){
  var js,pf;
  pf=document.createElement('script');
  pf.type='text/javascript';
  pf.src='//cdn.printfriendly.com/printfriendly.js';
  document.getElementsByTagName('head')[0].appendChild(pf)})();
"""
