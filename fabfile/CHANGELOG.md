## 0.3b (April 5, 2013)

- Deprecated WP_*_UPLOADS arguments in the settings file.
- Bugfix: class Release needed to be typed to object
- Added tools module, has 2 tasks currently:
    1.) a "fix" on the code in the plugins directory (explained below).
    2.) testing functionality for the settings file: for each host, it checks the following:
        - connection: runs `uname -a`
        - directories: test if they exist or not, reports result
        - database: verifies MySQL connection

## 0.3a (March 26, 2013)

Added an `extend` module, so end-users can write their own customized classes to extend our own. An example of the intended usage is included in `fabfile/extend/deploy/release_example.py`, demonstrating how to add your own actions to the post-release function (the example shows how to symlink a directory into the new webroot).


## 0.2 (March 25, 2013)

Added a backup task, which does the following, out-of-the box:

- Production db: dumps, fetches.
- Local db: dumps.
- Archives folder that now contains those 2 databases: rsync'd to the backup server
- Wordpress uploads folder: rsync'd from prod to local, then from local to backup
- Git repo: pushes local repo to backup server.

Note: updated structure for the settings file. See settings_Example.py for more info.

**Deprecation warning for next version:** In the settings file, the 2 variables for the Wordpress uploads directory are going to be removed (WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION), in favor of adding them to the settings.dirs value. Again, see settings_example.py for more info.