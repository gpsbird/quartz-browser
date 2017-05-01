
# -*- coding: utf-8 -*-
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
#  pf.src='file://./printfriendly.js';
