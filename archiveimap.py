#!/usr/bin/env python

'''
Archiveimap is a tool to keep an email account in version control. It's a
pretty simple wrapper around offlineimap and git. The commit message is what
offlineimap prints to stdout while running.

To use:
Make sure offlineimap and git are both installed. First configure
offlineimap appropriately, and then set the configuration variables here.

ACCOUNTS is the name (or list of names) of the accounts in offlineimap you
wishto keep archived.

CONFIG_FILE is usually going to be the same, unless you're doing something
strange.

GIT_AUTHOR is the author that will be used to make git commits

Set STDOUT to True if you want output, False to not print anything.

Then drop it in cron, or however else you're using it.
'''

from __future__ import print_function
from tempfile import NamedTemporaryFile
from ConfigParser import SafeConfigParser
import os
from os.path import exists, expanduser, join
import subprocess
from sys import argv

__author__ = 'Stephen Morton'
__version__ = '0.1'
__license__ = '''
Copyright (c) 2011, Stephen Morton
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of other contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


def call(args, log=None, stdout=True):
    '''Call a command and log the results.'''
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    for line in process.stdout:
        if stdout:
            print(line, end='')
        if log is not None:
            log.write(line)


def init(directories, log, stdout=None):
    '''Make directories and initialize git, if neccesary.'''
    for directory in directories:
        if not exists(directory):
            os.mkdir(directory)
        if not exists(join(directory, '.git')):
            os.chdir(directory)
            call(['git', 'init'], log)


def get_archive_directories(accounts=None, config_file=None, **kwargs):
    '''Get the directories appropriate for accounts by examining
    CONFIG_FILE.'''
    # python gets confused about reference before assignment without the
    # explict global statement in this case
    parser = SafeConfigParser()
    parser.read(config_file)
    directories = []
    for account in accounts:
        local_name = parser.get('Account ' + account, 'localrepository')
        local_folder = parser.get('Repository ' + local_name, 'localfolders')
        directories.append(expanduser(local_folder))
    return directories


def get_settings(config_file=None):
    '''
    If config_file exists, return settings from there. Otherwise, return
    default settings. Returns a dict.
    '''
    settings = {'stdout': True,
                'config_file': '~/.offlineimaprc',
                'git_author': None,
                'accounts': None}
    if config_file is None:
        config_file = expanduser('~/.archiveimaprc')
    if exists(config_file):
        parser = SafeConfigParser(settings)
        parser.read(config_file)
        items = dict(parser.items('Settings'))
        for option in settings.keys():
            if option in items:
                settings.update({option: items[option]})
    settings['config_file'] = expanduser(settings['config_file'])
    return settings


def archive_imap(accounts=None):
    '''Call offlineimap and put the results in a git repository.'''
    settings = get_settings()
    if accounts is not None:
        settings.update({'accounts': accounts})
    log = NamedTemporaryFile(delete=False)
    archive_directories = get_archive_directories(**settings)
    init(archive_directories, log, settings['stdout'])
    if settings['accounts'] is not None:
        call(['offlineimap', '-u', 'Noninteractive.Basic', '-a',
            ','.join(accounts)], log, settings['stdout'])
    else:
        call(['offlineimap', '-u', 'Noninteractive.Basic'], log,
             settings['stdout'])
    for directory in archive_directories:
        os.chdir(directory)
        call(['git', 'add', '-A'], log)
        log.close()
        if settings['git_author'] is not None:
            call(['git', 'commit', '--author="%s"' % settings['git_athor'],
                  '-F', log.name], stdout=settings['stdout'])


if __name__ == '__main__':
    archive_imap(argv[1:])
