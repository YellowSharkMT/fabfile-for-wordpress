## 0.2 (March 25, 2013)

Added a backup task, which does the following, out-of-the box:

- Production db: dumps, fetches.
- Local db: dumps.
- Archives folder that now contains those 2 databases: rsync'd to the backup server
- Wordpress uploads folder: rsync'd from prod to local, then from local to backup
- Git repo: pushes local repo to backup server.

Note: updated structure for the settings file. See settings_Example.py for more info.

**Deprecation warning for next version:** In the settings file, the 2 variables for the Wordpress uploads directory are going to be removed (WP_UPLOADS_PROD_LOCATION, WP_UPLOADS_LOCAL_LOCATION), in favor of adding them to the settings.dirs value. Again, see settings_example.py for more info.