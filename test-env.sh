#!/usr/bin/sh

if [ ! -f ~/.local/bin/virtualenv-3.3 ]; then exit; fi

rm -rf env dist *.egg-info
virtualenv-3.3 env
./setup.py sdist

cp dist/*.gz env
cd env
source bin/activate
easy_install ./*.gz

sh

