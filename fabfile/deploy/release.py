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
        self.release_name = env.release = settings.PROJECT_NAME + '_release_' + time.strftime('%Y%m%d-%H%M%S')
        
    def perform(self, source = 'local', destination = 'prod'):
        if self.dry_run:
            print(':: -==- DRY RUN MODE ENABLED -==-')
            print(':: None of the commands will be executed, they will be printed to the display.')
            print(':: Certain functionality might not be possible in dry-run mode, we\'ll let ') 
            print(':: you know when that happens though.')
            print(':: ------------------------------------')
                    
        print('## Triggering pre_perform hook... ##')
        #self.pre_perform(destination)
        # Push files from source webroot to destination repo
        env.host_string = settings.hosts.get(source)

        dest_dirs = settings.dirs.get(destination)
        #webroot = dest_dirs.get('webroot')
        releases = dest_dirs.get('releases')
        source_dirs = settings.dirs.get(source)

        # this is the to-be-updated code, which does indeed work:
        print('## Pushing repo to destination... ##')
        with cd(source_dirs.get('webroot')):
            run('pwd')
            if self.dry_run:
                print('[DRY RUN: %s] Preparing to push git repo from %s to %s' % (source, source, destination))
            else:
                print('Preparing to push git repo from %s to %s' % (source, destination))
                

            # Right here, it is absolutely critical that my local git repo has a remote named "prod".
            cmd = 'git push %(dest)s %(local_branch)s:%(dest_branch)s' % {
                'dest': destination,
                'local_branch': source_dirs.get('git_branch', 'master'),
                'dest_branch': dest_dirs.get('git_branch', 'master'),
            }
            if self.dry_run:
                print(('[DRY RUN: %s] ' % source) + cmd)
            else:
                run(cmd)
            
        # Pull files from destination repo to destination webroot
        env.host_string = settings.hosts.get(destination)                            
        cmd_data = {
            'repo': dest_dirs.get('git_repo'),
            'branch':dest_dirs.get('git_branch','master'),
            'releases':releases,
            'release':self.release_name,
            #'webroot':webroot,
        }
        prep_commands = [
            'git clone --branch=%(branch)s %(repo)s %(releases)s/%(release)s' % cmd_data,
            'rm -rf %(releases)s/%(release)s/.git*' % cmd_data,
            'ln -s %(releases)s/%(release)s %(releases)s/new' % cmd_data,
        ]
        transition_commands = [
            'rm -rf %(releases)s/previous' % cmd_data,
            'mv %(releases)s/current %(releases)s/previous && mv %(releases)s/new %(releases)s/current' % cmd_data,
        ]
        confirm_msg = 'About to clone the repo on the destination server, and unlink/re-link the webroot. Proceed?'
        if self.dry_run:
            confirm_msg = ('[DRY RUN: %s] ' % destination) + confirm_msg
            
        if confirm(confirm_msg):
            print('## Executing prep_commands ... ##')
            for cmd in prep_commands:
                if self.dry_run:
                    print(('[DRY RUN: %s] ' % destination ) + cmd)
                else:
                    run(cmd)

            print('## Triggering pre_transition hook... ##')
            self.pre_transition(destination)

            print('## Executing transition_commands actions... ##')
            for cmd in transition_commands:
                if self.dry_run:
                    print(('[DRY RUN: %s] ' % destination ) + cmd)
                else:
                    run(cmd)
            print('## Release completed successfully. ##')
        else:
            print('Release cancelled. Exiting...')
            sys.exit(0)
            
        self.post_perform(destination)
        
    def pre_perform(self, location):
        # Custom stuff would go here, backing up static files, whatever.
        # if self.dry_run:
        # else:
        pass

    def pre_transition(self, location):
        # Custom stuff would go here, like sym-linking stuff into place, etc
        pass
        
    def post_perform(self, location):
        # Custom stuff would go here, like if you need to symlink some stuff into place, etc.
        # if self.dry_run:
        # else:
        pass