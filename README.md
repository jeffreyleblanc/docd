# Docd Overview

## 1. About and Motivation

`docd` is a tool for building documentation from markdown and other source files.


## 2. Dependencies and Installation

> More "modern" dependency and installation methods are on the TODO list

```sh
$ sudo apt-get install \
    make rsync \
    python3-tornado \
    python3-markdown \
    python3-toml \
    python3-lunr
```

You can easily just run docd out of this repository, but to install/uninstall:

```sh
$ make install
$ make uninstall
```

This adds `docd-cli.py` as `/usr/local/bin/docd` and syncs the contents of `docd/` into `/usr/lib/python3/dist-packages/docd`.

Note that some cli commands must be run from within this repository, though all basic operations work with either method.


## 3. Project Structure

A project folder that `docd` works on should have the following structure:

```sh
docd.toml   # Config file, see below
docs/
    _media/
        # Place any media here, it will be rsynced into _dist
    # ... other files and folders
_dist/
    # Will get build by docd for you, see section below on it's structure
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


## 4. Basic Usage

From within a repo using installed `docd`:

```sh
docd
    build-all           Build the entire system
    build-clean         Clean out the docd site
    build-pages         Build the rendered pages
    build-search        Build the search index
    build-spa           Build the dist spa
    filter-check        Check docs for filter phrases
    push-to-site        Push docs to a remote site
```

Running from the docd repo:

```sh
# To build entire site
$ ./docd-cli.py -R PATH_TO_DOCS_REPO build-all

# To use the dev server
$ ./docd-cli.py -R PATH_TO_DOCS_REPO devserver
```


## 5. Structure of the `_dist` Output

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


## 6. Caddy SPA Server Config

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


## 7. UI Development Setup

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

In order to build the js/css for deployment within `docd/`:

```sh
$ ./docd-cli.py developer clear-spa-framework
$ ./docd-cli.py developer build-spa-framework
```

Note you will need `nodejs` and `npm` installed.

