#!/bin/bash

# Define the device (e.g., /dev/sda)
DEVICE="$1"

# Check if the device parameter is provided
if [ -z "$DEVICE" ]; then
  echo "Usage: $0 <device>"
  exit 1
fi

# Function to check smart status
check_smart_status() {
  if ! command -v smartctl &> /dev/null; then
    echo "smartctl could not be found. Please install smartmontools."
    exit 1
  fi

  echo "SMART status for $DEVICE:"
  sudo smartctl -H "$DEVICE"

  echo "Detailed SMART information for $DEVICE:"
  sudo smartctl -A "$DEVICE"
}

# Function to list block information
list_block_info() {
  if ! command -v lsblk &> /dev/null; then
    echo "lsblk could not be found. Please install the required package."
    exit 1
  fi

  echo "Block information for $DEVICE:"
  lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT "$DEVICE"
}

# Execute the functions
check_smart_status
list_block_info

