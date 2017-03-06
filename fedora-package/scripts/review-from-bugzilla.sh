#!/bin/bash

echo bug number is given as: $1
BUG=$1

re='^[0-9]+$'
if ! [[ $BUG =~ $re ]] ; then
   echo "error: give first argument as the Bugzilla number" >&2; exit 1
fi

cd ~
# remove any previous folder
rm -rf "$BUG-*"

# /usr/bin must be before /usr/sbin otherwise mock will throw error
PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin

fedora-review -b $BUG -m fedora-rawhide-x86_64

