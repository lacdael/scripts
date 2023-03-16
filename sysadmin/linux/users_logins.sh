#!/bin/bash

#This script first sets the number of logins to display (in this case, it is set to 10 logins), and then uses the last command to get a list of recent logins. The last command displays a list of users who have logged in to the system, along with the time and date of their login.

#Next, the script prints the most recent logins from the list, up to the specified number of lines. This allows you to see the most recent logins on the system, which can be useful for monitoring user activity and identifying potential security issues.

#Note that the number of logins to display can be customized to suit your specific needs. You can also modify the script to display additional information about each login, such as the IP address or hostname of the computer from which the user logged in.

# Set the number of logins to display
lines=10

# Use the "last" command to get a list of recent logins
logins=$(last)

# Print the most recent logins, up to the specified number of lines
echo "$logins" | tail -n $lines

