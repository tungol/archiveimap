#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup
import archiveimap as package

setup(
      name = package.__name__,
      version = package.__version__,
      packages = package.__packages__,
      scripts = package.__scripts__,
      author = package.__author__,
      author_email = package.__author_email__,
      description = package.__description__,
      license = package.__license__,
      long_description = package.__doc__,
      platforms=package.__platforms__,
      url = package.__url__,
      classifiers = package.__classifiers__,
)
