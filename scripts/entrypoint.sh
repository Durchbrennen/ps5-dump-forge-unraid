#!/bin/sh
set -eu
if [ ! -d /games ] || [ ! -r /games ] || [ ! -x /games ]; then
    echo "Mount a readable game share at /games." >&2
    exit 1
fi
if [ ! -w /config ]; then
    echo "/config must be writable by container user 99:100." >&2
    exit 1
fi
mkdir -p "$XDG_DATA_HOME" "$XDG_CONFIG_HOME"
exec /opt/forge/ps5-dump-forge serve --port 8095 --root /games "$@"
