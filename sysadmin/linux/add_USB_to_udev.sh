#!/bin/bash

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root."
  exit 1
fi

# Check arguments
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <USB device> <mount point>"
  echo "Example: $0 /dev/sda1 /mnt/myusb"
  exit 1
fi

USB_DEVICE=$1
MOUNT_POINT=$2

# Create the mount point if it doesn't exist
if [ ! -d "$MOUNT_POINT" ]; then
  echo "Creating mount point: $MOUNT_POINT"
  mkdir -p "$MOUNT_POINT"
  chmod 777 "$MOUNT_POINT"
fi

# Get the UUID of the USB device
UUID=$(blkid -s UUID -o value "$USB_DEVICE")
if [ -z "$UUID" ]; then
  echo "Error: Unable to determine UUID for $USB_DEVICE."
  exit 1
fi

# Create a udev rule
UDEV_RULE="SUBSYSTEM==\"block\", ENV{ID_FS_UUID}==\"${UUID}\", ACTION==\"add\", RUN+=\"/usr/bin/mount -o rw,umask=000 UUID=${UUID} ${MOUNT_POINT}\""

# Add the udev rule to the rules directory
RULE_FILE="/etc/udev/rules.d/99-usb-mount.rules"
echo "$UDEV_RULE" > "$RULE_FILE"

# Reload udev rules
udevadm control --reload-rules
udevadm trigger

# Verify the rule is added
if grep -q "$UUID" "$RULE_FILE"; then
  echo "Udev rule added successfully: $RULE_FILE"
  echo "Your USB device will now be mounted read/write for all users at $MOUNT_POINT on boot."
else
  echo "Failed to add udev rule."
fi

