#!/bin/sh

PROGDIR="/Users/lrizzi/PythonProjects/Framework/prototype"

PYTHONPATH="$PROGDIR:$PYTHONPATH"
export PYTHONPATH

echo $PYTHONPATH $PROGDIR

python $*
