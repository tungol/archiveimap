'''
Archiveimap is a tool to keep an email account in version control. It's a
pretty simple wrapper around offlineimap and git.

To use:
Make sure offlineimap and git are both installed. First configure offlineimap
appropriately, and then set the configuration variables here.
ACCOUNTS is the name (or list of names) of the accounts in offlineimap you wish
to keep archived. 
CONFIG_FILE is usually going to be the same, unless you're doing something 
strange.
AUTHOR is the author that will be used to make git commits
LOGGING is the type of logging you want, values can be 'file' or 'stdout',
anything else will result in no logging.
LOGFILE is the name of the file to log to, if logging to a file.

Then drop it in cron, or however you're using it.
'''

__licence__ = '''
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

__version__ = '0.1'

__author__ = 'Stephen Morton'

import ConfigParser  # apparently this causes os.path import???
import os
import subprocess
import time


ACCOUNTS = 'Example'
CONFIG_FILE = '~/.offlineimaprc'
AUTHOR = 'Example <example@example.com>'
LOGGING = 'stdout'
LOGFILE = '~/.archiveimap.log'


def call(args, log):
    '''Call a command and log the results.'''
    process = subprocess.Popen(args, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    for line in process.stdout:
        log(line)


def init(directories, log):
    '''Start logging. If neccesary, make directories and initialize git.'''
    log('\n%s\n' % time.strftime('%a, %d %b %Y %H:%M:%S +0000'))
    for directory in directories:
        if not os.path.exists(directory):
            os.mkdir(directory)
        if not os.path.exists(os.path.join(directory, '.git')):
            os.chdir(directory)
            call(['git', 'init'], log)


def get_log_func():
    '''Determine and return the log function specified in LOGGING.'''
    logfile = os.path.expanduser(LOGFILE)
    
    def log_to_file(string):
        '''Log to a file.'''
        with open(logfile, 'a') as log:
            log.write(string)
    
    def log_to_stdout(string):
        '''Log to STDOUT.'''
        print string.strip()
    
    def no_logs(string):
        '''Don't log.'''
        pass
    
    if LOGGING == 'file':
        return log_to_file
    elif LOGGING == 'stdout':
        return log_to_stdout
    return no_logs


def get_archive_directories():
    '''Get the directories appropriate for ACCOUNTS by examining 
    CONFIG_FILE.'''
    # python gets confused about reference before assignment without the
    # explict global statement in this case
    global ACCOUNTS
    parser = ConfigParser.SafeConfigParser()
    parser.read(os.path.expanduser(CONFIG_FILE))
    if type(ACCOUNTS) in (str, unicode):
        ACCOUNTS = [ACCOUNTS]
    directories = []
    for account in ACCOUNTS:
        local_name = parser.get('Account ' + account, 'localrepository')
        local_folder = parser.get('Repository ' + local_name, 'localfolders')
        directories.append(os.path.expanduser(local_folder))
    return directories


def archive_imap():
    '''Call offlineimap and put the results in a git repository.'''
    log = get_log_func()
    archive_directories = get_archive_directories()
    init(archive_directories, log)
    call(['offlineimap', '-u', 'Noninteractive.Basic', '-a',
        ','.join(ACCOUNTS)], log)
    for directory in archive_directories:
        os.chdir(directory)
        call(['git', 'add', '-A'], log)
        call(['git', 'commit', '--author="%s"' % AUTHOR,
            '--message="Automatic commit."'], log)


if __name__ == '__main__':
    archive_imap()
