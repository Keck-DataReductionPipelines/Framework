#!/bin/sh

FULLPATH=`readlink -f $0`
PROGDIR=`dirname $FULLPATH`
PROGDIR=`dirname $PROGDIR`

PYTHONPATH="$PROGDIR:${HOME}/hq/git/Framework/prototype:$PYTHONPATH"
export PYTHONPATH

echo $PYTHONPATH $PROGDIR

python $*
