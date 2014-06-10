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
from fabric.contrib.console import confirm
import db

# Import Settings:
try:
	from fabfile.settings import dirs, hosts, USE_TOOLS
except:
	print('Unable to load settings file. Have you created one yet? See fabfile/settings_example.py file for more info.')
	sys.exit(0)

# Optional Tools, (introduced 2013-04-05)
if USE_TOOLS:
	import tools

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
def deploy(source = 'prod', destination = 'local', dry_run=False):
	""" Executes migrate and update. Default direction is prod to local. (:source, :destination) """
	execute(migrate, source, destination, dry_run)
	execute(update, source, destination, dry_run)


@task
def migrate(source = 'prod', destination = 'local', dry_run=False):
	""" Executes database migration. Default direction is prod to local. (:source, :destination) """
	if confirm('You are about to migrate the %s database to %s. Is that ok?' % (source, destination)):
		print('-----------------------------------------')
		print('Migrating database from %s to %s' % (source, destination))
		fn_to_execute = 'import_%s_to_%s' % (source, destination)
		execute(getattr(db, fn_to_execute), dry_run)
		print('-----------------------------------------')
	else:
		print('Exiting...')

@task
def update(source = 'prod', destination = 'local', dry_run = False):
	""" Executes code migration. Default direction is prod to local. (:source, :destination, :dry_run = False) """
	print('-----------------------------------------')
	print('Updating code from %s to %s' % (source, destination))
	fn_to_execute = 'sync_%s_to_%s' % (source, destination)
	execute(getattr(sys.modules[__name__], fn_to_execute), dry_run)
	print('-----------------------------------------')


@task
def dump(location = 'prod', fetch = False)	:
	""" Dumps location database to archive folder. (:location = prod, :fetch = False) """
	print('-----------------------------------------')
	if fetch:
		print('Dumping/fetching %s database.' % (location))
		fn_to_execute = 'fetch_%s_db' % (location)
		dump_fn = execute(getattr(db, fn_to_execute))
	else:
		print('Dumping %s database.' % (location))
		fn_to_execute = 'dump_db'
		dump_fn = execute(getattr(db, fn_to_execute), location)

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
def sync_prod_to_local(dry_run = False):
	""" Syncs files from prod to local. """
	sync_uploads('prod', 'local')

def sync_local_to_prod(dry_run = False):
	""" Syncs files from local to prod. """
	release = Release(git = True, dry_run = dry_run)
	release.perform()
	pass

def sync_local_to_dev(dry_run = False):
	""" Syncs files from local to dev (aliases to sync_local_to_prod) """
	release = Release(git = True, dry_run = dry_run)
	release.perform(destination = 'dev')
	pass

def sync_uploads(source_host, dest_host):
	""" Uses rsync to pull down uploads from :source_host to :dest_host. (from the settings file) """

	# TODO: Improve the logic in this function. The problem is that rsync requires a connection between a local host,
	# and a remote one, so there's a bit of validation that should probably happen here, so that users get accurate
	# error info and can figure things out maybe a bit quicker. Big problem here though is that we're only testing for
	# prod & local hosts, where we should perhaps just be checking if one of the hosts is local, and then just use the
	# other one accordingly. There's a whole bunch of if/else blocks in all of that though, so I want to think on this
	# problem a bit before making a solution.
	rsync_vars = False
	if source_host == 'prod':
		rsync_vars = {
			'source': '%s:%s' % (hosts.get(source_host), dirs.get(source_host).get('uploads')),
			'dest': '%s' % (dirs.get(dest_host).get('uploads'))
		}
	elif source_host == 'local':
		rsync_vars = {
			'source': '%s' % (dirs.get(source_host).get('uploads')),
			'dest': '%s:%s' % (hosts.get(dest_host), dirs.get(dest_host).get('uploads'))
		}

	if not rsync_vars:
		print('Sorry, couldn\'t create the rsync command. Check the documentation for more info. This is relatively-new functionality, and will be improved in future releases.')
		return
	else:
		rsync_command = 'rsync -ravz %(source)s/ %(dest)s' % rsync_vars
		# Note: this is run on the local server, rsync requires that ONE of the servers is the local.
		local(rsync_command)
	