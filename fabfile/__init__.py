# Fabfile for Wordpress, by YellowShark (yellowsharkmt@gmail.com / twitter.com/yellowshark)
# - Use "fab -l" to view list of commands.
# - IMPORTANT: All settings & options are in settings.py.
#
# This fabfile is mostly used for shuffling around Wordpress databases, from production
# to dev, or vice-versa. It has functions to export, migrate, and import databases, as well
# as to transfer them between environments. Also, there's a function to download the contents
# of the Wordpress uploads directory. It should be noted that there are no cleanup functions for
# dumped/exported files, both local & remote: they are left in place, and not deleted.
#
# What this fabfile does NOT (currently) have: VCS commands (commit/push/pull/etc.) & deployment schemes.
#
# Typical usage:
# - fab deploy
# - fab migrate
# - fab update
# - fab dump

from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

# Import Settings:
try:
	from .settings import dirs, hosts, WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION
except:
	print('Unable to load settings file. Have you created one yet? See fabfile/settings_example.py file for more info.')
	sys.exit(0)

import db
# Import Release module (attempt to find extended version first)
try:
	from .extend.deploy.release import ReleaseCustom as Release
except:
	from .deploy.release import Release

# Import Backup module
from .deploy.backup import Backup

# Leaving this as True is generally harmless, it simply allows you to enter a connection
# name from your .ssh/config file as a value for env.host_string (set this in settings.hosts)
env.use_ssh_config = True

#############################################################################
## Public functions for the Fab commands.
@task
def deploy(source = 'prod', destination = 'local'):
	""" Executes migrate and update. Default direction is prod to local. (:source, :destination) """
	execute(migrate, source, destination)
	execute(update, source, destination)
	

@task
def migrate(source = 'prod', destination = 'local'):
	""" Executes database migration. Default direction is prod to local. (:source, :destination) """
	print('-----------------------------------------')
	print('Migrating database from %s to %s' % (source, destination))
	fn_to_execute = 'import_%s_to_%s' % (source, destination)
	execute(getattr(db, fn_to_execute))
	#getattr(db, fn_to_execute)()
	print('-----------------------------------------')

		
@task
def update(source = 'prod', destination = 'local'):
	""" Executes code migration. Default direction is prod to local. (:source, :destination) """
	print('-----------------------------------------')
	print('Updating code from %s to %s' % (source, destination))
	fn_to_execute = 'sync_%s_to_%s' % (source, destination)
	execute(getattr(sys.modules[__name__], fn_to_execute))
	print('-----------------------------------------')
	
	
@task
def dump(location = 'prod', fetch = False)	:
	""" Dumps location database to archive folder. Fetch default is false. (:location, :fetch) """
	print('-----------------------------------------')
	if fetch:
		print('Dumping/fetching %s database.' % (location))
		fn_to_execute = 'fetch_%s_db' % (location)
		dump_fn = execute(getattr(db, fn_to_execute))
	else:
		print('Dumping %s database.' % (location))
		fn_to_execute = 'dump_%s_db' % (location)
		dump_fn = execute(getattr(db, fn_to_execute))
		
	print('Filename: %s' % dump_fn)
	print('-----------------------------------------')	

@task
def backup(source = 'local', destination = 'backup'):
	""" Performs backup operation. See README for exact details. (:source, :destination) """
	# This function might need a bit more explanation, it actually backs up a number of things:
	# - production db: dumps, fetches.
	# - local db: dumps.
	# - archives folder that now contains those 2 databases: rsync'd to the backup server
	# - wordpress uploads folder: rsync'd from prod to local, then from local to backup
	# - git repo: pushes local repo to backup server.
	print('-----------------------------------------')
	backup = Backup(source, destination)
	print('Completed backing up production & local servers to the backup server.')
	print('-----------------------------------------')

# TODO: migrate these into Classes, get them out of the __init__ module.
def sync_prod_to_local():
	""" Syncs files from prod to local. """
	sync_uploads_prod_to_local()

def sync_local_to_prod():
	""" Syncs files from local to prod. """
	release = Release(git = True)
	release.perform()
	pass
	
def sync_uploads_prod_to_local():
	""" Uses rsync to pull down uploads from Prod to Local """
	rsync_command = ('rsync -ravz %s %s' % (WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION))
	local(rsync_command)	
	