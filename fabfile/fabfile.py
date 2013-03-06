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
# - fab import_db import_uploads (imports/migrates remote database, pulls down uploads.)
# - fab fetch_remote_db (dumps remote/prod db to remote/prod archive folder, downloads it to local archive folder)
# - fab export_db (does: migrate for prod, dumps, uploads, imports db to prod. Only for the brave.)

from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

## Import custom settings
from .settings import db_settings, dirs, hosts, PROJECT_NAME, LOCAL_URL, PROD_URL, WP_FOLDER, WP_PREFIX, WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION

# Leaving this as True is generally harmless, it simply allows you to enter a connection
# name from your .ssh/config file as a value for env.host_string (set this in settings.hosts)
env.use_ssh_config = True

## Attempt to load the MySQLdb module.
try:	
	import MySQLdb
	print("MySQLdb module found.")
	use_db = True
except:
	print("No MySQLdb module found. All local MySQL queries will be done via bash.")
	print("For info on installing MySQLdb for Python, see http://stackoverflow.com/a/7461662/844976")
	use_db = False
	
	
#############################################################################
## _prod() and _local() assign the appropriate options from the settings file.
def _prod_server():
	env.host_string = hosts.get('prod')

def _local_server(): # Note: we use _local_server() so there's ZERO confusion with Fabric's local() function.
	env.host_string = hosts.get('local')	


#############################################################################
## Public functions for the Fab commands.
def import_db():
	""" Imports Prod db to Local. (Shortcut for import_prod_to_local) """
	import_prod_to_local()

def export_db():
	""" Exports Local db to Prod, (Shortcut for import_local_to_prod) """
	import_local_to_prod()

def import_uploads():
	""" Uses rsync to pull down uploads from Prod to Local """
	rsync_command = ('rsync -ravz %s %s' % (WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION))
	local(rsync_command)	

def import_prod_to_local():
	""" Imports Wordpress database from Prod to Local. """
	dump_local_fn = fetch_prod_db()
	
	db = db_settings.get('local')
	bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), dump_local_fn)
	local('mysql -u %s -p%s -h %s %s < %s' % bash_cmd_vars)
	run_db_migration('local')

def import_local_to_prod():
	""" Imports Wordpress database from Local to Prod. """
	dump_remote_fn = push_local_db()

	_prod_server()
	db = db_settings.get('prod')
	bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), dump_remote_fn)
	run('mysql -u %s -p%s -h %s %s < %s' % bash_cmd_vars)

def fetch_prod_db():
	""" Dumps the Prod database, then downloads it to Local. """
	dump_remote_fn, dump_fn = dump_prod_db()
	
	# Set to Local info for the download & import
	dump_local_fn = ('%s/%s' % (dirs.get('local').get('archive'), dump_fn))
	get(dump_remote_fn, dump_local_fn)
	return dump_local_fn

def push_local_db():
	""" Dumps local database (already migrated to prod settings), uploads to Prod """
	dump_local_fn, dump_fn = dump_local_db_for_deploy()

	# Set to Prod info for the upload & import
	dump_remote_fn = ('%s/%s' % (dirs.get('prod').get('archive'), dump_fn))
	_prod_server()
	put(dump_local_fn, dump_remote_fn)
	return dump_remote_fn

# Returns tuple: db_dump_full, db_dump (filenames: full, short)
def dump_prod_db():
	""" Dumps Prod database to remote archive folder. """
	_prod_server()

	db = db_settings.get('prod')
	dump_fn = db.get('db','unknowndb') + '.dump_' + str(time.time()) + '.sql'
	dump_full_fn = dirs.get('prod').get('archive', '~/archive') + '/' + dump_fn

	bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), dump_full_fn)
	cmd = ('mysqldump -u %s -p%s -h %s %s > %s' % bash_cmd_vars)
	run(cmd)
	return (dump_full_fn, dump_fn)

def dump_local_db():
	""" Dumps Local database to local archive folder. """
	_local_server()

	db = db_settings.get('local')
	dump_fn = db.get('db','unknowndb') + '.dump_' + str(time.time()) + '.sql'
	dump_full_fn = dirs.get('local').get('archive', '~/archive') + '/' + dump_fn

	bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), dump_full_fn)
	cmd = ('mysqldump -u %s -p%s -h %s %s > %s' % bash_cmd_vars)
	run(cmd)
	return (dump_full_fn, dump_fn)

def dump_local_db_for_deploy():
	""" Wrapper for dump_local_db. Runs migration to prod, dumps, then migrates back to local. """
	run_db_migration('prod')
	result = dump_local_db()
	run_db_migration('local')
	return result

def run_db_migration(dest='local'):
	""" Executes MySQL commands for migrating Wordpress from one environment to another. Parameter defaults to "local", but any environment defined in the settings.db dictionary (default: local, prod) can be used. """
	# Check for whether to use MySQLdb or bash. If MySQLdb, set up the connection.
	if use_db:
		# Force this to work on local databases only!
		db = db_settings.get('local')
		db_conn = MySQLdb.connect(db.get('host'), db.get('user'), db.get('pass'), db.get('db'))
		cursor = db_conn.cursor()

	# Here's the MySQL commands to update Wordpress. At the simplest, `site_url` and `home` need to be updated, in the wp_options
	# table. However, you could write any SQL you like here, for example a search/replace for the PROD_URL and the LOCAL_URL,
	# like if you wanted all attachments/images to be served from your local server, instead of the prod server. Generally
	# attachments aren't much of a problem, and I tend to only update the bare minimum to make Wordpress run locally.
	wp_url = LOCAL_URL if (dest == 'local') else PROD_URL
	sql = [
		('UPDATE %s_options SET option_value="%s/%s" WHERE option_name="siteurl"' % (WP_PREFIX, wp_url, WP_FOLDER)),
		('UPDATE %s_options SET option_value="%s/" WHERE option_name="home"' % (WP_PREFIX, wp_url)),
		# Add new commands below:
		#('UPDATE something yadda yadda.....')
	]

	for query in sql:
		if not use_db:
			# Do MySQL via bash
			bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), query)
			cmd = ('mysqldump -u %s -p%s -h %s %s < "%s"' % bash_cmd_vars)
			local(cmd) # again, forcing this command to run only on local server, NOT prod/remote
		else:
			# Do MySQL via MySQLdb
			try:
				cursor.execute(query)
			except:
				print(cursor)
				print('Migration query failed. Exiting...')
				sys.exit(0)

	# Clean up the database connection if using MySQLdb
	if use_db:
		db_conn.close()