#!/usr/bin/env python

from setuptools import setup

setup(
      name='quartz',
      version='1.8.6',
      description='Fast Lightweight web browser written in PyQt4',
      keywords='pyqt4 browser',
      url='http://github.com/ksharindam/quartz-browser',
      author='Arindam Chaudhuri',
      author_email='ksharindam@gmail.com',
      license='GPLv3',
      packages=['quartz'],
#      install_requires=['PyQt4',      ],
      entry_points={
          'console_scripts': ['quartz=quartz.main:main'],
      },
#      include_package_data=True,
      zip_safe=False)
