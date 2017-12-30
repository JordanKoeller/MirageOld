#!/bin/bash

SOURCE_DIR='/home/Documents/Research/Pooley_Group/lensing_sinulator/src/'

while getopts ":rv" opt; do
	case ${opt} in
		r ) echo "Please enter the parameters file name."
		    read -e -p "> " infile
		    echo "Where should I save the data? Please enter a directory name."
		    read -e -p "> " outfile
#		    cd ${SOURCE_DIR}
		    cd src/
		    python Main.py --run ../$infile ../$outfile
		    ;;
		v ) cd src/
		    python Main.py --visualize
		    ;;
	esac
done
