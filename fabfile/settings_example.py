# This is the example settings file for the Fabfile for Wordpress module. Save a copy of this file in this current
# directory, and name it settings.py.

# A handle that can be used for naming dump files and such. Can be anything you like.
PROJECT_NAME = 'myproject'

# Base URL for the local & prod environments. Used to update the wp_options.site_url, and wp_options.home values.
LOCAL_URL = 'http://local.myproject.com'
PROD_URL = 'http://myproject.com'

# Location of your Wordpress installation, relative to the site root. NO LEADING/TRAILING SLASH. Leave blank if
# Wordpress is installed at the same location as the LOCAL_URL/PROD_URL settings, for example if WP is installed
# at the site root. Otherwise, if Wordpress is in a subdirectory, enter that location here. (This is used to
# update the wp_options.site_url value.)
WP_FOLDER = ''

# Wordpress table prefix, used for database migrations/operations. WP default is "wp"
WP_PREFIX = 'wp'

# Optional settings, for the import_uploads functionality. I don't always keep the uploads folder under version
# control. Instead, I'll just run rsync to pull down the prod directory.
#
# Warning: this deletes local files in your uploads folder. 
#
# For this function to work, you'll need to provide info for the rsync command, in the form of SOURCE and
# DESTINATION. These can be ssh connection strings, any valid SOURCE/DESTINATION value actually, these just
# get passed straight into the rsync command. Absolute paths are best, rsync can be funny about how it uses the
# tilde/~ character in this context.

## !! WARNING: these two values are going to deprecated, in future versions of this software.
WP_UPLOADS_PROD_LOCATION = 'user@prodhost.com:/path/to/public_html/wordpress/wp-content/uploads/' # Include trailing slash!!
WP_UPLOADS_LOCAL_LOCATION = '/www/myproject/wordpress/wp-content/uploads' # No trailing slash here
## End WARNING

# Host connection strings for Fabric. If env.use_ssh_config is set to True, you can use aliases assigned in
# your .ssh/config file.
hosts = {
	'prod':'user@prodhost.com',
	'local':'localhost',
	'backup':'user@backupserver.com', # For offsite backup. See the fabfile.deploy.backup module for more info.
}

# Database settings for the Prod % Local servers.
db_settings = {
	'local':{
		'host':'localhost',
		'user':'user',
		'pass':'password',
		'db':'database'
	},
	'prod':{
		'host':'localhost',
		'user':'user',
		'pass':'password',
		'db':'database'
	}
}

## Archive folder is used for dumping data, and storing downloaded/uploaded files.
# Note: No trailing slashes, please. Things might not be 100% bullet-proof in that regards.
dirs = {
	'local':{
		'archive': '/www/_archive/myproject',
		'releases': False,
		'webroot': '/www/myproject',
	   	'uploads': '/www/myproject/wp-content/uploads',
	},
	'prod':{
		'archive': '/path/to/archive/folder',
		'releases': '/path/to/releases/folder', # Only needed for deploy.release module. False if not using that.
		'webroot': '/path/to/public_html',
		'git_repo': '/path/to/git/repo.git',
		'uploads': '/path/to/wordpress/uploads',
	},
	'backup':{
		'archive': '/path/to/archive/folder',
		'releases': '/path/to/releases/folder', # Not needed (yet) for backup. Optional.
		'webroot': '/path/to/public_html', 		# Not needed (yet) for backup. Optional.
		'git_repo': '/path/to/git/repo.git',
		'uploads': '/path/to/wordpress/uploads',
	}
}
