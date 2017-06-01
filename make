#!/bin/sh
cd src
python setup.py build_ext --inplace
cd ..
echo "Build Done"