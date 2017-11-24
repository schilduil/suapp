#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
echo 
echo Running tests in $DIR
cd ../
WDIR="$(pwd)"
echo Working directory: $WDIR
echo 
echo Enabling virtual environment on .venv
source .venv/bin/activate
echo Launching tests...
py.test $*

#FILES=$DIR/test_*.py
#for f in $FILES
#do
#    python3 $f
#done
