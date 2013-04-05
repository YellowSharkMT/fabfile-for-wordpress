from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

import fabfile.settings as settings


# future: from .vcs import Git


class Release(object):
	dirs = settings.dirs
	git = False
	svn = False
	release_name = ''
	
	def __init__(self, git = False, svn = False):
		self.git = git
		self.svn = svn
		self.release_name = settings.PROJECT_NAME + '_release_' + str(time.time())
		
	def perform(self, source = 'local', destination = 'prod'):
		self.pre_perform()
		# Push files from source webroot to destination repo
		env.host_string = settings.hosts.get(source)

		# haven't test this yet...
		# git = Git(source)
		# git.push(destination, 'master')

		# this is the to-be-updated code, which does indeed work:
		with cd(settings.dirs.get(source).get('webroot')):
			# Right here, it is absolutely critical that my local git repo has a remote named "prod". 
			# TODO: be able to specify branches?
			run('git push %s master' % destination)
			
		# Pull files from destination repo to destination webroot
		env.host_string = settings.hosts.get(destination)							
		webroot = settings.dirs.get(destination).get('webroot')
		releases = settings.dirs.get(destination).get('releases')
		
		run('git clone %s %s/%s' % (settings.dirs.get(destination).get('git_repo'), releases, self.release_name))
		run('ln -s %s/%s %s.new' % (settings.dirs.get(destination).get('releases'), self.release_name, webroot))
		run('mv %(webroot)s %(webroot)s.old; mv %(webroot)s.new %(webroot)s; rm %(webroot)s.old' % {'webroot': webroot})
			
		self.post_perform(destination)
		
	def pre_perform(self):
		pass
		
	def post_perform(self, location):
		# Custom stuff would go here, like if you need to symlink some stuff into place, etc.
		pass
		
		
		
			
	
			





