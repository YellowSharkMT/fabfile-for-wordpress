# Fabfile For Wordpress Extension
#
# Overrides Package: deploy.release
# (Be sure to rename this file & remove the "_example" stem from the filename.)

from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

import fabfile.settings as settings
from fabfile.deploy.release import Release

class ReleaseCustom(Release):
	def __init__(self, *args, **kwargs):
		super(self.__class__, self).__init__(*args, **kwargs)

	def pre_perform(self):
		# Custom commands for pre-release.
		pass
		
	def post_perform(self, location):
		# Custom commands for post-release

		# Example: symlink a folder into the webroot
		# env.host_string = settings.hosts.get(location)
		# with cd(settings.dirs.get(location).get('webroot')):
		# 	run('ln -s /path/to/something ./something')
		pass
