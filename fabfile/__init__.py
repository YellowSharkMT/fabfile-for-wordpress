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

# Import our modules:
from .settings import dirs, hosts, WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION
import db
from .deploy.release import Release

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
	