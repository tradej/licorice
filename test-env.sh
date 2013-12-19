#!/usr/bin/sh

# This is a script that builds and installs licorice into virtualenv for
# quick testing

rm -rf env dist *.egg-info
pyvenv-3.3 env
./setup.py sdist

cp dist/*.gz env
cd env
source bin/activate
easy_install ./*.gz --user

sh

