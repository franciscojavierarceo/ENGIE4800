#!/bin/bash

function Clean() {
 cd $1
 unzip -o \*.zip
 rm *.zip
 echo "Files in folder zipped and zipfiles removed"
}

echo "*******************"
echo "      Begin        "
echo "*******************"

Clean /Volumes/MyMac/ENGIE4800/Data/2014/
Clean /Volumes/MyMac/ENGIE4800/Data/2013/

echo "*******************"
echo "      End          "
echo "*******************"
