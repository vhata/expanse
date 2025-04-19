#!/bin/bash

# Add the current directory to PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# Run the daemon
python3 expanse/daemon.py 