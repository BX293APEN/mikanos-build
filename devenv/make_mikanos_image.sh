#!/bin/sh -ex

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OSBOOK_DIR="${OSBOOK_DIR:-$(dirname "$SCRIPT_DIR")}"
EDK2DIR="${EDK2DIR:-$OSBOOK_DIR/edk2}"
DEVENV_DIR="$SCRIPT_DIR"
MOUNT_POINT=./mnt

if [ "$DISK_IMG" = "" ]
then
  DISK_IMG=./mikanos.img
fi

if [ "$MIKANOS_DIR" = "" ]
then
  if [ $# -lt 1 ]
  then
      echo "Usage: $0 <day>"
      exit 1
  fi
  MIKANOS_DIR="$OSBOOK_DIR/$1"
fi

LOADER_EFI="$EDK2DIR/Build/MikanLoaderX64/DEBUG_CLANG38/X64/Loader.efi"
KERNEL_ELF="$MIKANOS_DIR/kernel/kernel.elf"

$DEVENV_DIR/make_image.sh $DISK_IMG $MOUNT_POINT $LOADER_EFI $KERNEL_ELF
$DEVENV_DIR/mount_image.sh $DISK_IMG $MOUNT_POINT

if [ "$APPS_DIR" != "" ]
then
  sudo mkdir $MOUNT_POINT/$APPS_DIR
fi

for APP in $(ls "$MIKANOS_DIR/apps")
do
  if [ -f $MIKANOS_DIR/apps/$APP/$APP ]
  then
    sudo cp "$MIKANOS_DIR/apps/$APP/$APP" $MOUNT_POINT/$APPS_DIR
  fi
done

if [ "$RESOURCE_DIR" != "" ]
then
  sudo cp $MIKANOS_DIR/$RESOURCE_DIR/* $MOUNT_POINT/
fi

sleep 0.5
sudo umount $MOUNT_POINT
