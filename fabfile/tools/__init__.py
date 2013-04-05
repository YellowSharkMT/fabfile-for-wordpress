from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.context_managers import settings as fab_settings

import fabfile.settings as settings

@task
def update_code_plugins_dir():
  """ Runs search/replace on plugins folder for plugins_url and plugin_dir_url(). See docs for more info. """
  plugins_dir = settings.dirs.get('local').get('plugins')
  if plugins_dir != False:
    print('Switching to local directory "%s"' % plugins_dir)
    with lcd(plugins_dir):
      if confirm('About to search/replace a lot of files in the %s folder. Do you wish to continue?' % plugins_dir):
        with fab_settings(warn_only=True):
          sed_command = 'find . -type f -print0 | xargs -0 sed -i \'s/%(find)s/%(replace)s/g\'' % {
            'find':'plugins_url(',
            'replace':'plugins_url_override(',
            }
          #print('Command to run: ' + sed_command)
          local(sed_command)

          sed_command = 'find . -type f -print0 | xargs -0 sed -i \'s/%(find)s/%(replace)s/g\'' % {
            'find':'plugin_dir_url(',
            'replace':'plugin_dir_url_override(',
            }
          #print('Command to run: ' + sed_command)
          local(sed_command)

@task
def test_host(host):
  """ Runs .test_connection and test_directories on the specified host. :host """
  test_connection(host)
  test_directories(host)
  test_db(host)
  print('Completed testing host `%s.`' % host)


def test_connection(host):
  """ Runs `uname -a` on specified host from the settings file. :host """
  env.host_string = settings.hosts.get(host)

  print('Testing that the `%s` connection is valid, running `uname -a`...' % host)
  run('uname -a')


def test_directories(host):
  """ Checks that the directories exist on specified host from the settings file. :host """
  env.host_string = settings.hosts.get(host)

  print('Checking the directories on host `%s` to see that they exist...' % (host))
  for dir_type in settings.dirs.get(host):
    d = settings.dirs.get(host).get(dir_type)
    if not d:
      print('Director/file is disabled. (%s)' % dir_type)
    elif exists(d):
      print('Directory/file exists: %s (%s)' % (d, dir_type))
    else:
      print('Directory/file does NOT exist: %s (%s)' % (d, dir_type))
  print('Completed checking directories on host `%s`.' % (host))

def test_db(host):
  """ Tests access to the database on the specified host from the settings file. """
  env.host_string = settings.hosts.get(host)
  print("Testing MySQL connection from the bash command line (empty result is favorable; an error \nwill be thrown if the db info is incorrect.")
  run('mysql -u %(user)s -p%(pass)s -h %(host)s -e "USE %(db)s"' % settings.db_settings.get(host))

