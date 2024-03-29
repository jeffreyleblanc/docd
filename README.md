# Docd Overview

## About and Motivation

`docd` is a tool for building documentation from markdown and other source files.

It's designed to roughly mimic `mkdocs`, but have more flexbility.


## Setup and Installation TLDR

On a Debian/Ubuntu System:

```sh
# Install dependencies
sudo apt-get install make rsync python3-mistune python3-pygments python3-toml ripgrep
# Install
make install 
```

To full build from source:

```sh
# Install dependencies
sudo apt-get install make rsync python3-mistune python3-pygments python3-tomlripgrep
sudo apt-get install nodejs npm 
# Setup and build web
make setup-web
./docd-local.py build-web
# Install
make install 
```


## Setup and Installation Details

The following dependencies are required (assuming on Debian/Ubuntu):

```sh
sudo apt-get install \
    make rsync \
    python3-mistune python3-pygments python3-toml \
    nodejs npm
# The `check` method uses ripgrep
sudo apt-get install ripgrep
```

There are 2 Makefiles, one in the project root and one in `spa-src/`.
The main Makefile can call the other, so these are the commands:

```
install          Install the tools and libraries
uninstall        Uninstall the tools and libraries
setup-web        Setup node/npm tooling
```

`make install` populates:

```sh
/usr/local/bin/docd                     # main executable
/usr/local/lib/docd/support             # support html,js,css files
/usr/lib/python3/dist-packages/docd     # python
```

**NOTE**: You should currently run `make build-web` before `make install` to ensure the updated static js,css files are installed.


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


## Usage

You can run either installed `/usr/local/bin/docd` or from this repo with `./docd.py`.
If you run here, use `--repo-directory/-R` to specify the docs repo to act on.

From the command line:

```
build               Build the complete docd site
spa                 Make the docd spa scaffold
publish             Convert the source docs to html
clean               Clean out the docd site
serve               Serve the document
push                Push docs to a remote
check               Check docs for filter phrases
info                Print info on the repo config

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -R REPO_DIRECTORY, --repo-directory REPO_DIRECTORY
                        Root document repo directory. Defaults to cwd.
```


## Development Patterns

```sh
# Build the spa js/css
$ ./docd-local.py build-web

# Rebuild the spa or the entire site running from repo
$ ./docd.py -R PATH_TO_DOCS_REPO spa
$ ./docd.py -R PATH_TO_DOCS_REPO build
```
