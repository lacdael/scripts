#!/bin/bash
#cron: 00 00 * * * /root/health.sh 2>&1 | /usr/sbin/ssmtp <email>

echo "To: <email>
From: <email>
Subject: HEALTH $(hostname -f)

============================================
$(uptime)
----LOGINS----------------------------------
$(./users_logins.sh)
----DRIVES----------------------------------
$(./drive_health.sh)
----ERRLOG----------------------------------
$(./logs_critical.sh)
============================================"
