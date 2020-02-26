#!/bin/bash

set -e

# first check if we're passing flags, if so prepend with dispatch
# Example ./docker-entrypoint.sh -flag=1 server start
if [ "${1:0:1}" = '-' ]; then
	set -- dispatch "$@"
fi

# Intercept known "dispatch $command $sub-command" combinations and append them
# to the "dispatch" binary. Other parameters are passed through
# Example: "./docker-entrpoint.sh server start" becomes "dispatch server start"
case "${@:1:2}" in
	"server start" | "database upgrade" | "database downgrade" | "scheduler start" )
		set -- dispatch "$@"
		;;
esac

exec "$@"
