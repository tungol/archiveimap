from setuptools import setup
import archiveimap

setup(
      name = 'archiveimap',
      version = archiveimap.__version__,
      packages = ['archiveimap'],
      author = archiveimap.__author__,
      author_email = archiveimap.__author_email__,
      description = archiveimap.__description__,
      license = archiveimap.__license__,
      long_description = archiveimap.__doc__,
      platforms='any',
      url = archiveimap.__url__,
      classifiers = [
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Communications :: Email',
      'Topic :: Software Development :: Version Control',
      'Topic :: System :: Archiving :: Backup',
      ]
)