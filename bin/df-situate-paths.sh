#!/bin/bash
#
# 
#
# Usage:
#   export PATH=$PATH`$DATAFAQS_HOME/bin/df-situate-paths.sh`
#   (can be repeated indefinately, once paths are in PATH, nothing is returned.)

missing=""

if [ ! `which df-epoch.sh` ]; then
   missing=":"
   missing=$missing$DATAFAQS_HOME/bin
fi

if [[ ! `which tdbloader` && -d "$TDBROOT" ]]; then
   if [ ${#missing} -gt 0 ]; then
      missing=$missing":"
   fi
   missing=$missing$TDBROOT/bin
fi

#if [ ! `which pcurl.sh` ]; then export PATH=$PATH:$DATAFAQS_HOME/bin/util
#   if [ ${#missing} -gt 0 ]; then
#      missing=$missing":"
#   fi
#   missing=$missing$DATAFAQS_HOME/bin/util
#fi
#
#if [ ! `which vload` ]; then
#   if [ ${#missing} -gt 0 ]; then
#      missing=$missing":"
#   fi
#   missing=$missing$DATAFAQS_HOME/bin/util/virtuoso
#fi

echo $missing

#for path in `echo ${PATH//://  }`; do
#   echo $path
#done
