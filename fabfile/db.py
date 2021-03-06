import time, random, string, sys
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
## Import custom settings
from .settings import hosts, dirs, site_urls, db_settings, WP_FOLDER, WP_PREFIX, hosts

## Attempt to load the MySQLdb module.
try:
    #import MySQLdb
    #print("MySQLdb module found.")
    use_db = False
except:
    #print("No MySQLdb module found. All local MySQL queries will be done via bash.")
    #print("For info on installing MySQLdb for Python, see http://stackoverflow.com/a/7461662/844976")
    use_db = False

env.roledefs = {
    'prod': [hosts.get('prod')],
    'local': [hosts.get('local')],
}
#############################################################################
## _prod() and _local() assign the appropriate options from the settings file.
def _prod_server():
    env.host_string = hosts.get('prod')

def _local_server(): # Note: we use _local_server() so there's ZERO confusion with Fabric's local() function.
    env.host_string = hosts.get('local')


#############################################################################
## Public functions for the Fab commands.    
def import_prod_to_local(dry_run=False):
    """ Imports Wordpress database from Prod to Local. """
    result = fetch_prod_db()
    insert_database(result, 'local')
    run_db_migration('local')


def import_local_to_prod():
    """ Imports Wordpress database from Local to Prod. """
    _prod_server()
    insert_database(push_local_db('prod'), 'prod')
    run_db_migration('prod')


def insert_database(dump_fn, location = 'local'):
    """ Inserts Wordpress database to specified location (default is local). """
    # old: env.host_string = hosts.get(location), replaced by:
    execute(getattr(sys.modules[__name__], '_%s_server' % location))
    db = db_settings.get(location)
    # bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), dump_fn)
    # cmd = 'mysql -u %s -p%s -h %s %s < %s' % bash_cmd_vars
    vars = {
        'dump_fn':dump_fn,
        'user':db.get('user'),
        'pass':db.get('pass'),
        'host':db.get('host'),
        'db':db.get('db'),
    }
    cmd = 'gunzip < %(dump_fn)s | mysql -u %(user)s -p%(pass)s -h %(host)s %(db)s' % vars
    run(cmd)


def fetch_prod_db():
    """ Dumps the Prod database, then downloads it to Local. """
    result = dump_db('prod')
    dump_remote_fn, dump_fn = result
    # Set to Local info for the download & import
    dump_local_fn = ('%s/%s' % (dirs.get('local').get('archive'), dump_fn))
    _prod_server()
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


# Returns tuple: dump_full_fn, dump_fn (filenames: full, short)
def __dump_prod_db():
    """ Dumps Prod database to remote archive folder. """
    return dump_db('prod')


# Returns tuple: dump_full_fn, dump_fn (filenames: full, short)    
def __dump_local_db():
    """ Dumps Local database to local archive folder. """
    return dump_db('local')


def dump_local_db_for_deploy():
    """ Wrapper for dump_local_db. Runs migration to prod, dumps, then migrates back to local. """
    run_db_migration('prod')
    result = dump_db('local')
    run_db_migration('local')
    return result


def dump_db(host, filename = False):
    # Execute _prod_server() or _local_server()
    execute(getattr(sys.modules[__name__], '_%s_server' % host))

    db = db_settings.get(host)
    if not filename:
        dump_fn = db.get('db','unknowndb') + '.'+host+'.' + str(time.time()) + '.sql.gz'
    else:
        dump_fn = filename

    dump_full_fn = dirs.get(host).get('archive', '~/archive') + '/' + dump_fn

    vars = {
        'dump_fn':dump_full_fn,
        'user':db.get('user'),
        'pass':db.get('pass'),
        'host':db.get('host'),
        'db':db.get('db'),
    }
    cmd = 'mysqldump -u %(user)s -p%(pass)s -h %(host)s %(db)s | gzip > %(dump_fn)s' % vars

    run(cmd)
    return (dump_full_fn, dump_fn)


@task
def stash(host = 'local', stash_name = False):
    """ Dumps the database on the specified host, bug gives it a "stash" name, so it can be pulled back in quickly via `unstash`. (:host) """
    db = db_settings.get(host)
    if not stash_name:
        filename = '%s.%s.stash.sql' % ( db.get('db','unknowndb'), host)
    else:
        filename = stash_name
    dump_db(host, filename)

@task
def unstash(host = 'local', stash_name = False):
    """ Inserts the "stash"-ed database on the specified host. (:host = local)"""
    execute(getattr(sys.modules[__name__], '_%s_server' % host))
    db = db_settings.get(host)
    if not stash_name:
        filename = '%s.%s.stash.sql' % ( db.get('db','unknowndb'), host)
    else:
        filename = stash_name
        
    dump_full_fn = dirs.get(host).get('archive', '~/archive') + '/' + filename
    if not exists(dump_full_fn):
        print('No stash file exists on the `%s` host.' % host)
        return
    else:
        if confirm('Are you sure you wish to insert the stash database to the `%s` host?' % host, False):
            if confirm('Do you wish to backup the current database before overwriting it?'):
                dump_db(host) # temporary-ish, this dumps a backup of the existing DB before un-stashing
            insert_database(dump_full_fn, 'local')

def run_db_migration(dest='local'):
    """ Executes MySQL commands for migrating Wordpress from one environment to another. Parameter defaults to "local", but any environment defined in the settings.db dictionary (default: local, prod) can be used. """
    # Check for whether to use MySQLdb or bash. If MySQLdb, set up the connection.
    db = db_settings.get('local')
    wp_url = site_urls.get(dest)
    wp_upload_path = dirs.get(dest).get('uploads')
    sql = make_update_sql(db, wp_url, wp_upload_path)

    if not use_db:
        perform_bash_update(db, sql)
    else:
        perform_mysqldb_update(db, sql)


def perform_bash_update(db, sql):
    for query in sql:
        # Do MySQL via bash
        bash_cmd_vars = (db.get('user'), db.get('pass'), db.get('host'), db.get('db'), query)
        cmd = ('mysql -u %s -p%s -h %s %s -e "%s"' % bash_cmd_vars)
        #print(cmd)
        run(cmd) # again, forcing this command to run only on local server, NOT prod/remote


def perform_mysqldb_update(db, sql):
    # Force this to work on local databases only!
    import MySQLdb
    db_conn = MySQLdb.connect(db.get('host'), db.get('user'), db.get('pass'), db.get('db'))
    cursor = db_conn.cursor()
    for query in sql:
        try:
            print('Updating db: %s' % query)
            cursor.execute(query)
        except:
            print(cursor)
            print('Migration query failed. Exiting...')
            sys.exit(0)
    db_conn.close()


def make_update_sql(db, wp_url, wp_upload_path = ''):
    # Here's the MySQL commands to update Wordpress. At the simplest, `site_url` and `home` need to be updated, in the wp_options
    # table. However, you could write any SQL you like here, for example a search/replace for the PROD_URL and the LOCAL_URL,
    # like if you wanted all attachments/images to be served from your local server, instead of the prod server. Generally
    # attachments aren't much of a problem, and I tend to only update the bare minimum to make Wordpress run locally.
    sql = [
        ("UPDATE %s.%s_options SET option_value='%s/%s' WHERE option_name='siteurl'" % (db.get('db'), WP_PREFIX, wp_url, WP_FOLDER)),
        ("UPDATE %s.%s_options SET option_value='%s/' WHERE option_name='home'" % (db.get('db'), WP_PREFIX, wp_url)),
        ("UPDATE %s.%s_options SET option_value='%s' WHERE option_name='upload_path'" % (db.get('db'), WP_PREFIX, wp_upload_path)),
        # Add new commands below:
        #('UPDATE something yadda yadda.....')
    ]
    return sql
