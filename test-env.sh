#!/usr/bin/sh

# This is a script that builds and installs licorice into virtualenv for
# quick testing

if [ ! -f ~/.local/bin/virtualenv-3.3 ]; then exit; fi

rm -rf env dist *.egg-info
virtualenv-3.3 env
./setup.py sdist

cp dist/*.gz env
cd env
source bin/activate
easy_install ./*.gz

sh

