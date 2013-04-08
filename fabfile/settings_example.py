# This is the example settings file for the Fabfile for Wordpress module. Save a copy of this file in this current
# directory, and name it settings.py.

# A handle that can be used for naming dump files and such. Can be anything you like.
PROJECT_NAME = 'myproject'

# Base URL for the local & prod environments. Used to update the wp_options.site_url, and wp_options.home values.
LOCAL_URL = 'http://local.myproject.com'
PROD_URL = 'http://myproject.com'

# Use the Tools module? No harm in including it, it can lead to a cluttered set in `fab -l` results though.
# See docs for what the tools module contains.
USE_TOOLS = True

# Host connection strings for Fabric. If env.use_ssh_config is set to True, you can use aliases assigned in
# your .ssh/config file.
hosts = {
	'prod':'user@prodhost.com',
	'local':'localhost',
	'backup':'user@backupserver.com', # OPTIONAL: For offsite backup. See the fabfile.deploy.backup module for more info.
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
	   	'uploads': '/www/myproject/wp-content/uploads', # OPTIONAL, "False" if not using rsync on uploads dirs.
	},
	'prod':{
		'archive': '/path/to/archive/folder',
		'releases': '/path/to/releases/folder', # OPTIONAL: Only needed for deploy.release module. False if not using that.
		'webroot': '/path/to/public_html',
		'git_repo': '/path/to/git/repo.git',
		'uploads': '/path/to/wordpress/uploads',  # OPTIONAL, "False" if not using rsync on uploads dirs.
	},
	'backup':{
		'archive': '/path/to/archive/folder',
		'releases': '/path/to/releases/folder', # Not needed (yet) for backup. Optional.
		'webroot': '/path/to/public_html', 		# Not needed (yet) for backup. Optional.
		'git_repo': '/path/to/git/repo.git',
		'uploads': '/path/to/wordpress/uploads', # OPTIONAL, "False" if not using rsync on uploads dirs.
	}
}

# Location of your Wordpress installation, relative to the site root. NO LEADING/TRAILING SLASH. Leave blank if
# Wordpress is installed at the same location as the LOCAL_URL/PROD_URL settings, for example if WP is installed
# at the site root. Specifcally, if your WP wp_options.siteurl is different than your wp_options.home (referring to your database's `wp_options` table), than you need to edit this value, and enter that location here. (This is used to.) No leading or trailing slashes.
WP_FOLDER = ''

# Wordpress table prefix, used for database migrations/operations. WP default is "wp"
WP_PREFIX = 'wp'
