#!/bin/bash

#To get the exit code:
#sudo script -e -c ./drive_health.sh; echo $?

# Check if the "smartctl" command is available
if ! [ -x "$(command -v smartctl)" ]; then
  echo "Error: smartctl command not found. Please install the 'smartmontools' package and try again." >&2
  exit 1
fi

# Get a list of all mounted drives
drives=$(smartctl --scan | awk '{print $1}')

# Check the health of each drive
for drive in $drives; do
# Check the health status of the drive

    HEALTH=$(smartctl -H $drive | tail -n +5 );
    echo " $drive : $HEALTH";
    RSLT=$( ( grep "SMART overall-health self-assessment test result" <<< "$HEALTH" ) | awk '{print $6}')
    # Check if the drive is in bad health
    if [ "$RSLT" != "PASSED" ]; then
        echo "The drive /dev/$drive is in bad health. Please check and replace it as soon as possible."
        (exit 505)
    fi
done

