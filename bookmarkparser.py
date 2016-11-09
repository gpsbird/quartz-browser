# -*- coding: utf-8 -*-

def parsebookmarks(filename):
    try:
        bmkfile = open(filename, 'r')
    except:
        return [["Google", "http://www.google.com"], ["Facebook", "https://m.facebook.com"]]
    bmklines = bmkfile.readlines()
    bmk_list = []
    line_no = 1
    for line in bmklines:
        line = line[:-1]
        if line_no % 2 != 0:
            group = [line]
        else:
            group.append(line)
            bmk_list.append(group)
            group = []
        line_no += 1
    bmkfile.close()
    return bmk_list

def writebookmarks(filename, bookmarks):
    bmkfile = open(filename, 'w')
    for item in bookmarks:
        bmk = item[0] + "\n" + item[1] + "\n"
        bmkfile.write(bmk)
    bmkfile.close()
