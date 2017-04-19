#!/usr/bin/env python3

from setuptools import setup
import glob

folders = glob.glob('./Dmeson/*/')

setup(name='HepPlot',
      version='1.0',
      description='Load and plot HepData-yaml database',
      author='Weiyao Ke',
      author_email='wk42@phy.duke.edu',
	  install_requires=['numpy>=1.8.0', 'pyyaml', 'matplotlib'],
      py_modules=['HepPlot'],
	  data_files=[('HepPlot/{}'.format(fo), glob.glob('{}/T*'.format(fo))) for fo in folders]
     )
