from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

import fabfile.settings as settings

class Git:
	dirs = settings.dirs
	
	def __init__(self):
		pass