#!/bin/bash

# Get a list of all mounted drives
DRIVES=$(df -h | grep -v "Filesystem" | awk '{print $1}')

# Iterate through each drive
for DRIVE in $DRIVES; do
  # Get the space used and available on the drive
  SPACE_USED=$(df -h $DRIVE | grep -v "Filesystem" | awk '{print $3}')
  SPACE_AVAILABLE=$(df -h $DRIVE | grep -v "Filesystem" | awk '{print $4}')
    "No such file or directory"

  # Print the drive, space used, and space available
  echo "$DRIVE: $SPACE_USED used, $SPACE_AVAILABLE available"
done
