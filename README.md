fabfile-for-wordpress
=====================

A small set of commands for managing Wordpress databases on production &amp; development servers, using the Python library [Fabric](http://fabfile.org).

This fabfile is mostly used for shuffling around Wordpress databases, from production to dev, or vice-versa. It has functions to export, migrate, and import databases, as well as to transfer them between environments. Also, there's a function to download the contents of the Wordpress uploads directory. It should be noted that there are no cleanup functions for dumped/exported files, both local & remote: they are left in place, and not deleted.

**New:** Backup functionality. Backs up remote database, remote uploads folder, local database, and local archives folder to a remote server, good for creating off-site backups of your Wordpress project.

### To use: ###

- New to [Fabric](http://fabfile.org)? Check out [this crash course](https://gist.github.com/DavidWittman/1886632).
- Clone to your WordPress site root (or anywhere actually), for example `myproject/fabfile`.
- Create a `fabfile/settings.py` by copying the `fabfile/settings_example.py`. Populate this new file with info specific to your Wordpress setup. (See file for more info.)
- To upgrade from an older version, just place the contents of the newest `fabfile/` folder directly into your current `fabfile/` folder, overwriting existing files. Be sure to keep your `settings.py` file, and be sure to check the new version's `settings_example.py` for new/updated settings. View the changelog for detailed info.

### Typical commands: ###

- fab deploy (TODO: provide explanation on default behavior. See the code, and `fab -l` for more info.)
- fab migrate
- fab update
- fab dump
- fab backup

### Notes: ###
- Security note: There's an .htaccess file containing "Deny from all" in the `fabfile` folder, however you'll want to be careful about putting this on a production/live server, specifically the settings.py file, so that you don't expose access to sensitive information. If you do put this code on a live server, you will *definitely* want to verify that those files are not accessible.
- As pointed out above, there's no cleanup mechanism for dumped databases.
