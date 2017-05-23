#!/usr/bin/env python

from setuptools import setup
from quartz_browser import __version__

setup(
      name='quartz-browser',
      version=__version__,
      description='Fast Lightweight web browser written in PyQt4',
      long_description='''To run it you need PyQt4 module.  
Install python-qt4 (for PyQt4 module) in debian based distros''',
      keywords='pyqt pyqt4 browser qtwebkit',
      url='http://github.com/ksharindam/quartz-browser',
      author='Arindam Chaudhuri',
      author_email='ksharindam@gmail.com',
      license='GNU GPLv3',
#      install_requires=['PyQt4',      ],
      classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Environment :: X11 Applications :: Qt',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Operating System :: POSIX :: Linux',
      'Programming Language :: Python :: 2.7',
      'Topic :: Internet :: WWW/HTTP :: Browsers',    
      ],
      packages=['quartz_browser', 'quartz_browser.pytube'],
      entry_points={
          'console_scripts': ['quartz=quartz_browser.main:main',
                              'pytube=quartz_browser.pytube.__main__:main'],
      },
      data_files=[
                 ('share/applications', ['files/quartz.desktop']),
                 ('share/icons', ['files/quartz-browser.png'])
      ],
      #include_package_data=True,
      zip_safe=False)
