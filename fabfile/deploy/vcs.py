from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

import fabfile.settings as settings

# Note: this class does NOT change the env.host_string, it's up to you to set that properly before you execute
# any commands within the Git class. (For now, anyway...)
class Git:
	dirs = settings.dirs
	source = ''
	
	def __init__(self, source):
		self.source = source
		pass

	def push(self, destination = 'origin', branch = 'master', options = ''):
		""" Executes git push from the webroot of the server. (TODO: make this more flexible?) """
		cmd = 'git push %(destination)s %(branch)s %(options)s' % {
			'destination':destination,
			'branch':branch,
			'options':options,
		}

		with cd(settings.dirs.get(self.source).get('webroot')):
			run(cmd)

		print('Completed git push.')