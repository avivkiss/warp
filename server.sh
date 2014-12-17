#!/bin/bash
WARPHOME=/opt/warp
MODNAME=opt-python
PRELOADED=$(echo ${LOADEDMODULES} | grep $MODNAME)
if [ -z $PRELOADED ]; then module load $MODNAME; fi
PYTHONPATH=${WARPHOME}:${PYTHONPATH} ${WARPHOME}/server.py $*
if [ -z $PRELOADED ]; then module unload $MODNAME; fi

