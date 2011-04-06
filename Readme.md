ArchiveIMAP
===========

ArchiveIMAP is a tool to keep an email account in version control. It's a
pretty simple wrapper around OfflineIMAP and git. The commit message is what
OfflineIMAP prints to stdout while running.

Usage
-----

Make sure OfflineIMAP and git are both installed and that OfflineIMAP is
properly configured. If you want to archive all accounts in OfflineIMAP,
using config files in the default locations and the system git author,
this is all that is needed. For other configurations, options can be set in
a configuration file or at the command line. The command line takes
precedence over the configuration file.

Configuration
-------------

The configuration file defaults to ~/.archiveimaprc and has a single section
named Settings. The following options are available:

* accounts: a comma seperated list of accounts to sync and put in git. Accounts must be defined in the offlineimap configuration file. Defaults to whatever accounts offlineimap is configured to sync.
* offlineimap-config: the path to the offlineimap configuration file. Defaults to ~/.offlineimaprc
* author: The author to use when making commits in git. Defaults to whatever git is configured to use by default.
* quiet: True or False. Controls whether to output status to stdout as well as logging to git commit message. Defaults to False.

See archiveimap -h for the command line options.