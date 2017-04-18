#!/usr/bin/env python

from setuptools import setup

setup(
      name='quartz-browser',
      version='1.8.7',
      description='Fast Lightweight web browser written in PyQt4',
      long_description='''To run it you need PyQt4 module and notify-send command.  
Install python-qt4 (for PyQt4 module) and libnotify-bin(for notify-send command) in debian based distros''',
      keywords='pyqt pyqt4 browser qtwebkit',
      url='http://github.com/ksharindam/quartz-browser',
      author='Arindam Chaudhuri',
      author_email='ksharindam@gmail.com',
      license='GNU GPLv3',
      packages=['quartz_browser'],
#      install_requires=['PyQt4',      ],
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: X11 Applications :: Qt',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python :: 2.7',
      'Topic :: Internet :: WWW/HTTP :: Browsers',    
      ],
      entry_points={
          'console_scripts': ['quartz=quartz_browser.main:main'],
      },
#      include_package_data=True,
      zip_safe=False)
