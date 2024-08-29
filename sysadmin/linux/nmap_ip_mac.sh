#!/bin/bash

# pass subnet as first arg e.g 192.168.1.0

sudo nmap -sn "$1/24" | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print " => "substr($0, index($0,$3)) }' | sort
