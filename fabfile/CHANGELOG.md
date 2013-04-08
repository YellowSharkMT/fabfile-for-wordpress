## 0.32b (April 8, 2013)

- Added dry-run functionality to the deploy/update process.
- Bug fixes
- Moved the USE_TOOLS settings from `fabfile/__init__.py` into `fabfile\settings_example.py`. Users will need to update their settings file and add this value, otherwise they will get an error that the settings file couldn't be loaded.


## 0.31b (April 8, 2013)

- Added new tasks to db module: `stash` & `unstash`. The `stash` task dumps the current database, and gives it a "stash" name, instead of a timestamp-based name. The `unstash` task will insert a "stashed" dump back into the database. (Note: it confirms whether you want to do this, and also it offers to make a backup of the current DB before overwriting it.)
- Bugfix: class Release needed to be typed to object
- Added tools module, has 2 tasks currently:
    1.) a "fix" on the code in the plugins directory (explained below).
    2.) testing functionality for the settings file: for each host, it checks the following:
        - connection: runs `uname -a`
        - directories: test if they exist or not, reports result
        - database: verifies MySQL connection


And as for the "fix" for the plugins directory that I referred to... In short, it addresses a problem that arises when you symlink your project root into the web root, versus actually putting your project into the actual web root. See, PHP returns the value of `__FILE__` as the actual filepath - not the symlinked path. This causes a rub with the core Wordpress function [`plugins_url()`](http://codex.wordpress.org/Function_Reference/plugins_url) and [`plugin_dir_url()`](http://codex.wordpress.org/Function_Reference/plugin_dir_url), which are supposed to return a URL for the plugins folder, or to an asset contained within. They do that with some funky `preg_replace`-ing, but it falls apart when things are symlinked, and what you wind up with is broken URLs to stuff in your plugins directory. Example of a broken URL:

http://www.xyzxyz.com/core/wp-content/plugins**/home/content/U/s/e/Username/versions/a_version/core/wp-content/plugins**/contact-form-7/includes/js/jquery.form.min.js

The correct URL should actually be:

http://www.xyzxyz.com/core/wp-content/plugins/contact-form-7/includes/js/jquery.form.min.js

Anyhow, I've got more to do on this to make it usable, and a blog-post on the matter is probably warranted. The end result is that I've added some custom functions to my Wordpress config file, `plugins_url_override()`, and `plugin_dir_url_override()`, and they are hand-crafted to return the correct URL for my symlinked Wordpress projects. And to bring it all back to this fabfile, and this function: it runs a search/replace on the whole plugins directory, and replaces calls to the WP functions with calls to my custom ones. Now whenever I update a plugin (like Jetpack, which updates several times a month, and has copious usage of these functions), I can just run this one fab task to fix things up. However, there's more to the picture than what I've got here, so apologies for releasing this without explaining exactly how to use it. Documentation will be forthcoming, if not a bigger fix.

## 0.3b (April 5, 2013)

- Deprecated WP_*_UPLOADS arguments in the settings file.


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