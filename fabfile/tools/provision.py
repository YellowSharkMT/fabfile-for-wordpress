from __future__ import with_statement
import time, random, string, sys
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
from fabfile import settings as fab_settings

@task
def do_it(host):
  p = Provision(host)

class Provision:
    dirs = False
    host = False

    def __init__(self, host):
        self.dirs = fab_settings.dirs.get(host)
        self.host = host

        if confirm('This will attempt to provision the remote server for deploying your app with FWP. Proceed?'):
            self._activate_host()
            self.create_folders()
            self.setup_releases_folder()
            if confirm('Would you like to create an empty git repository on the remote server?'):
                self.create_git_repo()


    def _activate_host(self):
        env.host_string = fab_settings.hosts.get(self.host)


    def create_folders(self):
        for loc in ['archive','releases','git_repo']:
            if not exists(self.dirs.get(loc)):
                run('mkdir -p %s' % self.dirs.get(loc))
            else:
                print('The %s folder already exists.' % loc)


    def create_git_repo(self):
        with cd(self.dirs.get('git_repo')):
            run('git init --bare')


    def setup_releases_folder(self):
        with cd(self.dirs.get('releases')):
            run('touch previous')
            run('mkdir current')
            run('ln -s %s/current %s' % (self.dirs.get('releases'),self.dirs.get('webroot')))
        pass
