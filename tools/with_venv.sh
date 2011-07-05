#!/bin/bash
TOOLS=`dirname $0`
VENV=$TOOLS/../.backfire-venv
source $VENV/bin/activate && $@
