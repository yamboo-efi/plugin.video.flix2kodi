#!/bin/bash

# Get the directory this script is running in 

reldir=`dirname $0`
cd $reldir
directory=`pwd`

# Lower the volume a touch as otherwise Netflix will start very loud
pamixer --decrease 10

# Bind the keys using our custom xbindkeys_rc
xbindkeys --file $directory/xbindkeys_rc &
