# Quartz Browser
A useful fast Web Browser written in pyqt4

**Dependency** = python2.7, python-qt4  

### Description
This browser is aimed at ease of use, faster page loading, very short startup time.  
This has minimal settings to avoid confusion.Yet it has most useful settings, such as load images on/off, javascript on/off, change font.  
To save pages to read later, print feature can be used to save as pdf. And it can also export the whole page as png image.  

### Installation
To Install the browser open terminal inside quartz-browser-master directory.  
And then run following command..  
    `sudo pip install .`  
Quartz Browser will be automatically added to applications menu.  

To uninstall run..  
    `sudo pip uninstall quartz-browser`

### Download .deb Package
You can directly download debian package for debian based distros and install it.  
Download it [here](https://github.com/ksharindam/quartz-browser/releases)  

### Usage
To run after installing, type command..  
    `quartz`  
Or  
    `quartz http://www.google.com`  
If you want to run the browser without/before installing, then  
Open terminal and change directory to quartz-browser-master and run  
    `./run.sh`  
Or  
    `./run.sh http://www.google.com`  

### Important Features :  
 1. Turn Javascript, Load Images on/off  option in main menu  
 1. Save as PDF, Save print-friendly PDF  
 1. Export full page as PNG/JPEG image, HTML file  
 1. Custom User Agent  
 1. Internal Download Manager with pause/resume support  
 1. External Download Manager support (e.g - wget, uGet )  
 1. Resume incomplete files downloaded by other browsers  
 1. Play video with RTSP protocol using a media player (e.g omxplayer, mplayer)  
 1. YouTube video download support. (Download button automatically appears)  

