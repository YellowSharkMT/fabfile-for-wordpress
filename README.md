fabfile-for-wordpress
=====================

A small set of commands for managing Wordpress databases on production &amp; development servers, using the Python library [Fabric](http://fabfile.org).

This fabfile is mostly used for shuffling around Wordpress databases, from production to dev, or vice-versa. It has functions to export, migrate, and import databases, as well as to transfer them between environments. Also, there's a function to download the contents of the Wordpress uploads directory. It should be noted that there are no cleanup functions for dumped/exported files, both local & remote: they are left in place, and not deleted.

What this fabfile does NOT (currently) have: VCS commands (commit/push/pull/etc.) & deployment schemes (actually, one deployment scheme is in master right now, use at your own risk of course. Documentation to come...)

### To use: ###

- New to [Fabric](http://fabfile.org)? Check out [this crash course](https://gist.github.com/DavidWittman/1886632).
- Clone to your WordPress site root (or anywhere actually).
- Create a `fabfile/settings.py` by copying the `fabfile/settings_example.py`. Populate this new file with info specific to your Wordpress setup. (See file for more info.)

### Typical usage: ###

- fab deploy (TODO: provide explanation on default behavior. See the code, and `fab -l` for more info.)
- fab migrate
- fab update
- fab dump

### Notes: ###
- Security note: There's an .htaccess file containing "Deny from all" in the `fabfile` folder, however you'll want to be careful about putting this on a production/live server, specifically the settings.py file, so that you don't expose access to sensitive information. If you do put this code on a live server, you will *definitely* want to verify that those files are not accessible.
- As pointed out above, there's no cleanup mechanism for dumped databases.
