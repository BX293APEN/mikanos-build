#!/bin/sh -ex

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OSBOOK_DIR="${OSBOOK_DIR:-$(dirname "$SCRIPT_DIR")}"
DEVENV_DIR="$SCRIPT_DIR"
DISK_IMG=./disk.img

DISK_IMG=$DISK_IMG OSBOOK_DIR="$OSBOOK_DIR" $DEVENV_DIR/make_mikanos_image.sh "$@"
$DEVENV_DIR/run_image.sh $DISK_IMG
