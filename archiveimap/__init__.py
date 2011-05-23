# encoding: utf-8
'''\
ArchiveIMAP is a tool to keep an email account in version control. It's a
pretty simple wrapper around OfflineIMAP and git. The commit message is what
OfflineIMAP prints to stdout while running.

To use:
Make sure offlineimap and git are both installed and that OfflineIMAP is
properly configured. If you want to archive all accounts in OfflineIMAP,
using config files in the default locations and the system git author,
this is all that is needed. For other configurations, options can be set in
a configuration file or at the command line. The command line takes
precedence over the configuration file.
'''


from .archiveimap import run

__all__ = ['run']
__version__ = '0.1'
__author__ = 'Stephen Morton'
__author_email__ = 'tungolcraft@gmail.com'
__description__ = 'Keep your email archived in git.'
__license__ = 'BSD'
__url__ = 'https://github.com/tungolcraft/archiveimap'
__packages__ = ['archiveimap']
__scripts__ = ['bin/archiveimap']
__platforms__ = 'any'
__classifiers__ = [
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