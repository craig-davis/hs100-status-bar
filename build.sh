#!/usr/bin/env bash

pip install -r ./requirements.txt
python setup.py py2app;
cp icon.png dist/ac_control.app/Contents/Resources/;
open dist/ac_control.app
