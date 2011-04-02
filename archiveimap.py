#!/usr/bin/env python

'''
Archiveimap is a tool to keep an email account in version control. It's a
pretty simple wrapper around offlineimap and git. The commit message is what
offlineimap prints to stdout while running.

To use:
Make sure offlineimap and git are both installed. First configure
offlineimap appropriately.

TODO: Describe config file here.

Commandline options:

usage: archiveimap.py [-h] [-q] [-a account [account ...]] [-c filename]
                      [--offlineimap-config filename]
                      [--author "Name <email@domain.com>"]

Keep your email archived in git.

optional arguments:
  -h, --help            show this help message and exit
  -q                    print no output
  -a account [account ...]
                        specify accounts to archive. Must be listed in the
                        offlineimap configuration file.
  -c filename           specify a configuration file to use instead of
                        ~/.archiveimaprc
  --offlineimap-config filename
                        specify offlineimap configuration file to use instead
                        of ~/.offlineimaprc
  --author "Name <email@domain.com>"
                        author to use for the git commit
'''

from __future__ import print_function
from argparse import ArgumentParser
from tempfile import NamedTemporaryFile
from ConfigParser import SafeConfigParser
import os
from os.path import abspath, exists, expanduser, join
import subprocess

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


def call(args, log=None, quiet=False):
    '''Call a command and log the results.'''
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    for line in process.stdout:
        if not quiet:
            print(line, end='')
        if log is not None:
            log.write(line)


def fixpath(path):
    '''
    If path starts with '~' return expanduser(path), otherwise return
    abspath(path)
    '''
    if path[0] == '~':
        return expanduser(path)
    else:
        return abspath(path)


def init(directories, log, stdout=None):
    '''Make directories and initialize git, if neccesary.'''
    for directory in directories:
        if not exists(directory):
            os.mkdir(directory)
        if not exists(join(directory, '.git')):
            os.chdir(directory)
            call(['git', 'init'], log, stdout)


def get_archive_directories(accounts, config_file):
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


def parse_config_file(config_file):
    '''
    If config_file exists, return a dictionary of settings from it. Otherwise,
    return an empty dictionary.
    '''
    settings = {}
    config_file = fixpath(config_file)
    if exists(config_file):
        parser = SafeConfigParser(settings)
        parser.read(config_file)
        settings = dict(parser.items('Settings'))
    translate = {'True': True, 'False': False, '': None}
    for key, value in settings.items():
        if value in translate:
            settings.update({key: translate[value]})
    return settings


def find_value(values):
    '''Return the first value in values that isn't None'''
    for value in values:
        if value is not None:
            return value


def resolve_overrides(overrides, defaults):
    '''
    Return return a dictionary with all the keys in defaults,
    with a value equal to the value from overrides if it exists and
    isn't None, otherwise with the value from defaults.
    '''
    settings = {}
    for key in defaults:
        if key in overrides:
            values = [overrides[key], defaults[key]]
            value = find_value(values)
        else:
            value = defaults[key]
        settings.update({key: value})
    return settings


def run_offlineimap(accounts, log=None, quiet=False):
    '''Run OfflineIMAP.'''
    if accounts is not None:
        call(['offlineimap', '-u', 'Noninteractive.Basic', '-a',
            ','.join(accounts)], log, quiet)
    else:
        call(['offlineimap', '-u', 'Noninteractive.Basic'], log,
             quiet)


def git_commit(archive_directories, author=None, log=None, quiet=False):
    '''
    Commit all changes in archive_directories to the appropriate git
    repository.
    '''
    for directory in archive_directories:
        os.chdir(directory)
        call(['git', 'add', '-A'], log)
        log.close()
        if author is not None:
            call(['git', 'commit', '--author="%s"' % author, '-F',
                  log.name], quiet=quiet)
        else:
            call(['git', 'commit', '-F', log.name], quiet=quiet)


def get_settings(overrides):
    '''
    Resolve settings from three sources, in order of precedence:
    1. from the command line
    2. from the config file
    3. built in defaults
    
    Returns a tuple of setting values, sorted on setting name.
    '''
    defaults = settings = {'quiet': False,
                'offlineimap_config': '~/.offlineimaprc',
                'author': None,
                'accounts': None}
    config_file = None
    if 'config_file' in overrides:
        config_file = overrides['config_file']
    if config_file is None:
        config_file = expanduser('~/.archiveimaprc')
    config_file = parse_config_file(config_file)
    defaults = resolve_overrides(config_file, defaults)
    settings = resolve_overrides(overrides, defaults)
    if type(settings['accounts']) in (str, unicode):
        settings['accounts'] = [settings['accounts']]
    settings['offlineimap_config'] = fixpath(settings['offlineimap_config'])
    keys = settings.keys()
    keys.sort()
    values = [settings[key] for key in keys]
    return values


def archive_imap(overrides):
    '''Call offlineimap and put the results in a git repository.'''
    settings = get_settings(overrides)
    accounts, author, config_file, quiet = settings
    archive_directories = get_archive_directories(accounts, config_file)
    log = NamedTemporaryFile(delete=False)
    init(archive_directories, log, quiet)
    run_offlineimap(accounts, log, quiet)
    git_commit(archive_directories, author, log, quiet)


def parse_args():
    '''
    Build an ArgumentParser instance and return the parsed arguments as a
    dictionary.
    '''
    parser = ArgumentParser(description='Keep your email archived in git.')
    parser.add_argument('-q', dest='quiet', const=True,
                        action='store_const', help='print no output')
    parser.add_argument('-a', metavar='account', nargs='+', dest='accounts',
                        help='specify accounts to archive. Must be listed in '
                             'the offlineimap configuration file.')
    parser.add_argument('-c', metavar='filename', dest='config_file',
                        help='specify a configuration file to use instead of '
                             '~/.archiveimaprc')
    parser.add_argument('--offlineimap-config', metavar='filename',
                        dest='offlineimap_config',
                        help='specify offlineimap configuration file to use '
                             'instead of ~/.offlineimaprc')
    parser.add_argument('--author', dest='author',
                        metavar='"Name <email@domain.com>"',
                        help='author to use for the git commit')
    return vars(parser.parse_args())


if __name__ == '__main__':
    archive_imap(parse_args())
