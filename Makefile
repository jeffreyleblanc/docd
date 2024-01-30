.PHONY: help install uninstall setup-web build-web clean-web

.DEFAULT=help
help:
	@echo "install          Install the tools and libraries"
	@echo "uninstall        Uninstall the tools and libraries"
	@echo "setup-web        Setup node/npm tooling"
	@echo "build-web        Build the css and js source into support"
	@echo "clean-web        Clean all built css and js from support"


install:
	# Note we probably need to clean this up
	# Install docd and support files
	sudo cp docd.py /usr/local/bin/docd
	sudo chmod 755 /usr/local/bin/docd
	sudo mkdir -p /usr/local/lib/docd/support
	sudo rsync -av --delete support/. /usr/local/lib/docd/support/.

	# Install the library methods
	sudo mkdir -p /usr/lib/python3/dist-packages/docd
	sudo rsync -av --delete --exclude='*.pyc' --exclude='__pycache__/' docd/. /usr/lib/python3/dist-packages/docd/.

uninstall:
	sudo rm -f /usr/local/bin/docd
	sudo rm -rf /usr/local/lib/docd/support
	sudo rm -rf /usr/lib/python3/dist-packages/docd

setup-web:
	cd spa-src && make setup

build-web:
	cd spa-src && make build

clean-web:
	cd spa-src && make clean
