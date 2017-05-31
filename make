#!/bin/sh

cd src
python setup.py build_ext --inplace
python Main.py
cd ..
