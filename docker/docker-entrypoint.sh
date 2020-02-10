#!/bin/bash

set -e

# first check if we're passing flags, if so
# prepend with dispatch
if [ "${1:0:1}" = '-' ]; then
	set -- dispatch "$@"
fi

case "$1" in
	server start|database upgrade| database downgrade)
		set -- dispatch "$@"
	;;
esac

exec "$@"