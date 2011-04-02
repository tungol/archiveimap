#!/usr/bin/env python

'''
Archiveimap is a tool to keep an email account in version control. It's a
pretty simple wrapper around offlineimap and git. The commit message is what
offlineimap prints to stdout while running.

To use:
Make sure offlineimap and git are both installed and that offlineIMAP is
properly configured. If you want to archive all accounts in offlineIMAP,
using config files in the default locations and the system git author,
this is all that is needed. For other configurations, options can be set in
a configuration file or at the command line. The command line takes
precedence over the configuration file.

The configuration file defaults to ~/.archiveimaprc and has a single section
named Settings. The following options are available:

accounts: a comma seperated list of accounts to sync and put in git.
          Accounts must be defined in the offlineimap configuration file.
          Defaults to whatever accounts offlineimap is configured to sync.
offlineimap-config: the path to the offlineimap configuration file. Defaults
                    to ~/.offlineimaprc
author: The author to use when making commits in git. Defaults to whatever
        git is configured to use by default.
quiet: True or False. Controls whether to output status to stdout as well as
       logging to git commit message. Defaults to False.

Commandline options can be examined by running ./archiveimap.py -h
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


def get_directories(accounts, config_file):
    '''
    Examine the offlineimap config file. If accounts is None, find what
    accounts offlineimap syncs by default. Find what directories the
    accounts listed in accounts are synced to. Return accounts (because it
    might have changed) and the directories associated with them.
    '''
    parser = SafeConfigParser()
    parser.read(config_file)
    directories = []
    if accounts is None:
        accounts = parser.get('general', 'accounts')
        accounts = [account.strip() for account in accounts.split(',')]
    for account in accounts:
        local_name = parser.get('Account ' + account, 'localrepository')
        local_folder = parser.get('Repository ' + local_name, 'localfolders')
        directories.append(expanduser(local_folder))
    return accounts, directories


def parse_config_file(config_file):
    '''
    If config_file exists, return a dictionary of settings from it.
    Otherwise, return an empty dictionary.
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


def run_offlineimap(accounts, config_file=None, log=None, quiet=False):
    '''Run OfflineIMAP.'''
    args = ['offlineimap', '-u', 'Noninteractive.Basic']
    if accounts is not None:
        args += ['-a', ','.join(accounts)]
    if config_file is not None:
        args += ['-c', config_file]
    call(args, log, quiet)


def git_commit(directories, author=None, log=None, quiet=False):
    '''
    For each directory named, commit any changes to git.
    '''
    for directory in directories:
        os.chdir(directory)
        call(['git', 'add', '-A'], log)
        log.close()
        args = ['git', 'commit', '-F', log.name]
        if author is not None:
            args.append('--author="%s"' % author)
        else:
            call(args, quiet=quiet)


def get_settings(overrides):
    '''
    Resolve settings from three sources, in order of precedence:
    1. from the command line
    2. from the config file
    3. built-in defaults
    
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


def archive_imap(overrides={}):
    '''Call offlineimap and put the results in a git repository.'''
    settings = get_settings(overrides)
    accounts, author, config_file, quiet = settings
    accounts, directories = get_directories(accounts, config_file)
    log = NamedTemporaryFile(delete=False)
    init(directories, log, quiet)
    run_offlineimap(accounts, config_file, log, quiet)
    git_commit(directories, author, log, quiet)


def parse_args():
    '''
    Build an ArgumentParser instance and return the parsed arguments as a
    dictionary.
    '''
    parser = ArgumentParser(description='Keep your email archived in git.')
    parser.add_argument('-q', '--quiet', dest='quiet', const=True,
                        action='store_const', help='be quiet')
    parser.add_argument('-v', '--verbose', dest='quiet', const=False,
                        action='store_const', help='be verbose [default]')
    parser.add_argument('-a', '--accounts', metavar='account', nargs='+',
                        dest='accounts',
                        help='specify accounts to archive. Must be listed in '
                             'the offlineimap configuration file.')
    parser.add_argument('-c', '--config-file', metavar='filename',
                        dest='config_file',
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
