#!/bin/bash

lines=10

logins=$(last)

# Print the most recent logins
echo "$logins" | tail -n $lines

