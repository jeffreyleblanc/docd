# Docd Overview

## 1. About and Motivation

`docd` is a tool for building documentation from markdown and other source files.

It's designed to roughly mimic `mkdocs`, but have more flexbility.


## 2. Dependencies and Installation

> More "modern" dependency and installation methods are on the TODO list

```sh
$ sudo apt-get install make rsync python3-tornado python3-markdown python3-toml
```

You can easily just run docd out of this repository, but to install/uninstall:

```sh
$ make install
$ make uninstall
```

This adds `docd-cli.py` as `/usr/local/bin/docd` and syncs the contents of `docd/` into `/usr/lib/python3/dist-packages/docd`.

Note that some cli commands must be run from within this repository, though all basic operations work with either method.


## 3. Development Setup

Use a setup like this for easy dev:

```sh
# Pane for css/js building
$ cd spa-src
$ npx vite build --watch

# Pane for building pages/search
$ ./docd-cli.py -R PATH_TO_DOCS_REPO build-pages
$ ./docd-cli.py -R PATH_TO_DOCS_REPO build-search

# Pane to run the devserver
$ ./docd-cli.py -R PATH_TO_DOCS_REPO devserver
```

Note you will need `nodejs` and `npm` installed.


## 4. Structure of the Output

```sh
main_docs_repo/
    _dist/
        index.html # SPA html page (May not be present in dev mode)
        _resources
            pages-database.json
            media/
                ... media support
            pages-html/
                ... all the pages as rendered htm
            pages-txt/
                ... all the pages as raw text
            search/
                ... search index files
            static/
                ... static css/js SPA files # (May not be present in dev mode)
```


## 5. Caddy SPA Server Config

If you are using [Caddy](https://caddyserver.com/) as your webserver, you can use a block like this:

```
    # Support /docs/ docd single page app
    handle /docs/* {

        handle /docs/_resources/* {
            root * /var/www/html
            file_server
        }

        handle {
            root * /var/www/html
            try_files {path} /docs/index.html
            file_server
        }
    }
```

In this case `/var/www/html` is the root of the website's file system, so adjust accordingly.



# -- OLDER -------------------------------------------------------------------------------- #


## Project Structure

A project folder that `docd` works on should have the following structure:

```sh
docd.toml   # Config file
docs/
    _media/
        # Place any media here, it will be rsynced into _dist
    # ... other files and folders
_dist/ # Will get build by docd for you
    db/
        page-db.json    # database of all pages
        #... rendered markdown=>html files
    index.html
    _media/
        # rsync'd media
    static/
        # compiled js/css
```

The `docd.toml` file should look like:

```yaml
# optional
[source]
max_depth = 3 # default is 2. this is max directory depth that is parsed
[source.file_types]
".md"= "markdown"
".py" = "python"
#...etc, see `docd.py` for default list

[site]
name = "Joe's Docs"
title= "Joe's Code Documentation"
footer = "Copyright Joe. All Rights Reserved."
author = "Joe Smith"
# optional:
home_addr = "https://joes-page.com"

# remote is optional:
[remote]
user = "joe"
addr = "joes_ip_addr"
path = "/var/www/joes-page.com/html/docs/"

# check set is optional:
[check]
filter_phrases = '''
joe
smith
'''
```

