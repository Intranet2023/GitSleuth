#!/bin/bash
# Setup script to install dependencies before network access is disabled.
set -e

# Change to the directory of the script
cd "$(dirname "$0")"

pip install -r requirements.txt
