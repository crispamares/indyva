#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage: dev_process ROOTDIR"
    exit
fi

if [ -d $1 ]; then
    # To kill dnotify when close the process
    trap 'kill $(jobs -pr)' SIGINT
    cd $1
#    dnotify -Mr src/ -e make &
#    echo "dnotify auto make ..."
    python tools/autocompile.py src/ &
    python -m SimpleHTTPServer 8888 
else
    echo "Usage: dev_process ROOTDIR"
    exit    
fi
