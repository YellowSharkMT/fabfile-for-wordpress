from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

import fabfile.settings as settings
import fabfile.db as db
from .vcs import Git


class Backup:
	release_name = False
	source = ''
	destination = ''

	def __init__(self, source, destination, perform = True):
		self.release_name = settings.PROJECT_NAME + '_release_' + str(time.time())
		self.source = source
		self.destination = destination
		if perform:
			env.host_string = settings.hosts.get(source)
			self.perform()

	def perform(self):
		print('Performing backup...')
		self.git_repo()
		self.wp_uploads()
		self.databases()
		self.archives()

	def git_repo(self):
		git = Git(self.source)
		git.push(settings.hosts.get('backup'), '', '--all')

	# NOTE! This only works from local to remote. From rsync: "The source and destination cannot both be remote"
	# So for now, the backup is a one-way thing, from the local to remote. In order to do a full backup of production,
	# one must first manually update prod to local, specifically the bit that rsyncs the wp uploads, and THEN run
	# the backup process.
	def wp_uploads(self):
		""" Synchronizes production to local, then local to backup. """

		# Prod to local:
		cmd = 'rsync -ravz %(source)s/ %(destination)s' % {
			'source': settings.hosts.get('prod') + ':' + settings.dirs.get('prod').get('uploads'),
			'destination': settings.dirs.get('local').get('uploads'),
		}
		run(cmd)

		# Local to backup:
		cmd = 'rsync -ravz %(source)s/ %(destination)s' % {
			'source': settings.dirs.get('local').get('uploads'),
			'destination': settings.hosts.get('backup') + ':' + settings.dirs.get('backup').get('uploads'),
		}
		run(cmd)

		print('Uploads folder synchronized.')

	def databases(self):
		db.fetch_prod_db()
		db.dump_local_db()
		
	def archives(self):
		cmd = 'rsync -ravz %(source)s/ %(destination)s' % {
			'source': settings.dirs.get('local').get('archive'),
			'destination': settings.hosts.get('backup') + ':' + settings.dirs.get('backup').get('archive'),
		}
		run(cmd)
		print('Local archives folder has been synchronized to the backup server.')
