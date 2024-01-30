#!/bin/bash

set -e

echo "uninstall"

sudo rm /usr/local/bin/docd-math

sudo rm /usr/local/lib/docd-math/template.html
sudo rmdir /usr/local/lib/docd-math

