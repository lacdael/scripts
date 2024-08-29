#!/bin/bash
lines=5

log_files=$(ls /var/log)

# Iterate over the log files
for log_file in $log_files; do
  #echo "Log file: $log_file"

  # Use the "grep" command to search the log file for critical errors
  errors=$(grep -i -E "critical|fail" /var/log/$log_file)
  #errors=$(grep -i -E "error|critical|fail|alert" /var/log/$log_file)
  if [ -n "$errors" ]; then
    echo "$errors" | tail -n $lines
  fi
  # Print the most recent errors, up to the specified number of lines
done

