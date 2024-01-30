#!/bin/bash

set -e

echo "install"

sudo cp builder.py /usr/local/bin/docd-math
sudo chmod 755 /usr/local/bin/docd-math

sudo mkdir -p /usr/local/lib/docd-math/
sudo cp template.html /usr/local/lib/docd-math

