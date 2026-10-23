#!/bin/sh
# Runs a command in the KiCad 9 container, in this directory, as the current user.
exec podman run --rm --userns=keep-id -e HOME=/tmp -v "$(dirname "$(readlink -f "$0")")":/w:Z -w /w -e TRACK_W -e CLEARANCE docker.io/kicad/kicad:9.0 "$@"
