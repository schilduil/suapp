#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
echo 
echo Running tests in $DIR
cd ../
WDIR="$(pwd)"
echo Working directory: $WDIR
echo 
echo Creating virtual environment on .venv...
python3 -m venv .venv
echo Installing the requirements...
.venv/bin/pip install -r requirements.txt
echo Installing pytest and pytest-cov...
.venv/bin/pip install pytest-cov
echo Installing pytest-annotate
.venv/bin/pip install pytest-annotate
echo Done.
