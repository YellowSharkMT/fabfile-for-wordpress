from __future__ import with_statement
import time, random, string, sys
from fabric.api import *
from fabric.contrib.console import confirm

import fabfile.settings as settings


# future: from .vcs import Git


class Release(object):
	dirs = settings.dirs
	git = False
	svn = False
	dry_run = False
	release_name = ''
	
	def __init__(self, git = False, svn = False, dry_run = False):
		self.git = git
		self.svn = svn
		self.dry_run = dry_run
		self.release_name = settings.PROJECT_NAME + '_release_' + str(time.time())
		
	def perform(self, source = 'local', destination = 'prod'):
		if self.dry_run:
			print(':: -==- DRY RUN MODE ENABLED -==-')
			print(':: None of the commands will be executed, they will be printed to the display.')
			print(':: Certain functionality might not be possible in dry-run mode, we\'ll let ') 
			print(':: you know when that happens though.')
			print(':: ------------------------------------')
					
		self.pre_perform()
		# Push files from source webroot to destination repo
		env.host_string = settings.hosts.get(source)

		# haven't test this yet...
		# git = Git(source)
		# git.push(destination, 'master')

		# this is the to-be-updated code, which does indeed work:
		with cd(settings.dirs.get(source).get('webroot')):
			if self.dry_run:
				print('[DRY RUN: %s] Preparing to push git repo from %s to %s' % (source, source, destination))
			else:
				print('Preparing to push git repo from %s to %s' % (source, destination))

			# Right here, it is absolutely critical that my local git repo has a remote named "prod".
			cmd = 'git push %(dest)s %(local_branch)s:%(dest_branch)s' % {
				'dest': destination,
				'local_branch': settings.dirs.get(source).get('git_branch', 'master'),
				'dest_branch': settings.dirs.get(destination).get('git_branch', 'master'),
			}
			if self.dry_run:
				print(('[DRY RUN: %s] ' % source) + cmd)
			else:
				run(cmd)
			
		# Pull files from destination repo to destination webroot
		env.host_string = settings.hosts.get(destination)							
		webroot = settings.dirs.get(destination).get('webroot')
		releases = settings.dirs.get(destination).get('releases')
		
		cmds = [
			'git clone %s %s/%s' % (settings.dirs.get(destination).get('git_repo'), releases, self.release_name),
			'cd %s/%s && git checkout %s' % (releases, self.release_name, settings.dirs.get(destination).get('git_branch'),'master'),
			'ln -s %s/%s %s.new' % (settings.dirs.get(destination).get('releases'), self.release_name, webroot),
			'mv %(webroot)s %(webroot)s.old; mv %(webroot)s.new %(webroot)s;' % {'webroot': webroot},
			'rm %(webroot)s.old' % {'webroot': webroot},
		]
		confirm_msg = 'About to clone the repo on the destination server, and unlink/re-link the webroot. Proceed?'
		if self.dry_run:
			confirm_msg = ('[DRY RUN: %s] ' % destination) + confirm_msg
			
		if confirm(confirm_msg):
			for cmd in cmds:
				if self.dry_run:
					print(('[DRY RUN: %s] ' % destination ) + cmd)
				else:
					run(cmd)
		else:
			print('Release cancelled. Exiting...')
			sys.exit(0)
			
		self.post_perform(destination)
		
	def pre_perform(self):
		# Custom stuff would go here, backing up static files, whatever.
		# if self.dry_run:
		# else:
		pass
		
	def post_perform(self, location):
		# Custom stuff would go here, like if you need to symlink some stuff into place, etc.
		# if self.dry_run:
		# else:
		pass