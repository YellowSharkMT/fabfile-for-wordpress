"""
Fabfile For Wordpress Extension

Overrides Package: deploy.release
Be sure to rename this file & remove the "_example" stem from the filename (should be
"fabfile/extend/deploy/release.py").

Also note the EXAMPLE_pre_transition() method, can be used as a template fo commands
"""
from __future__ import with_statement
import time, random, string, sys
from fabric.api import *

import fabfile.settings as settings
from fabfile.deploy.release import Release


class ReleaseCustom(Release):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)


    def pre_perform(self, location):
        """
        This hook executes first, before pushing the git repository up to the remote server.
        """
        pass


    def pre_transition(self, location):
        """
        This hook executes AFTER the git push & webroot checkout, and BEFORE the new webroot is symlinked into place.
        This is a good place to perform any file cleanup on the new webroot, or to link static assets into place.
        """
        pass


    def post_perform(self, location):
        """
        This hook executes AFTER the new webroot has been symlinked into place.
        """
        pass


    def EXAMPLE_pre_transition(self, location):
        """
        Example of a pre_transition set of commands. You can use the same logic in the other hooks.
        """
        env.host_string = settings.hosts.get(location)
        dest_dirs = settings.dirs.get(location)
        webroot = dest_dirs.get('webroot')
        releases = dest_dirs.get('releases')

        # Vars to use in the commands...
        cmd_data = {
            'releases': releases,
            'release': self.release_name,  #'webroot':webroot,
        }

        cmds = [
            # This releases a bunch of common files: Gruntfile, package.json, the fabfile/ dir, and
            # python_env_requirements.txt file
            'rm -rf %(releases)s/%(release)s/{Gruntfile.js,package.json,python_env_requirements.txt,fabfile}' % cmd_data,

            # Link the uploads directory, which is outside of the webroot, into place. In this example, the uploads
            # folder is in one place, and the sitemaps & robots are in a nother location.
            'ln -s /path/to/wordpress_uploads %(releases)s/%(release)s/core/wp-content/uploads' % cmd_data,

            # Same thing with the sitemaps, and the robots.txt file: link those into the webroot.
            'ln -s /path/to/wordpress_static/sitemap.xml %(releases)s/%(release)s/sitemap.xml' % cmd_data,
            'ln -s /path/to/wordpress_static/sitemap.xml.gz %(releases)s/%(release)s/sitemap.xml.gz' % cmd_data,
            'ln -s /path/to/wordpress_static/robots-prod.txt %(releases)s/%(release)s/robots.txt' % cmd_data,
        ]

        for cmd in cmds:
            if self.dry_run:
                print(('[DRY RUN: %s] ' % location) + cmd)
            else:
                run(cmd)


