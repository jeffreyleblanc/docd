.PHONY: help install uninstall

.DEFAULT=help
help:
	@echo "install          Install the tools and libraries"
	@echo "uninstall        Uninstall the tools and libraries"


install:
	# Note we probably need to clean this up
	# Install docd and support files
	sudo cp docd-cli.py /usr/local/bin/docd
	sudo chmod 755 /usr/local/bin/docd

	# Install the library methods
	sudo mkdir -p /usr/lib/python3/dist-packages/docd
	sudo rsync -av --delete --exclude='*.pyc' --exclude='__pycache__/' docd/. /usr/lib/python3/dist-packages/docd/.

uninstall:
	sudo rm -f /usr/local/bin/docd
	sudo rm -rf /usr/lib/python3/dist-packages/docd

