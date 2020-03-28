#!/bin/bash

# run with cron like
# */3 * * * * the/path/system/./listen_checker.sh  >> the/path/src/logs/cron_listen.log 2>&1
# dont forget "chmod +x listen_checker.sh"

RIGHT_NOW=$(date +"%F_%R")

if [ "`systemctl show -p ActiveState --value listen`" = "active" ]
then
    #service is currently running
    exit 0
fi

echo "$RIGHT_NOW listen (listen.service) wasnt running attempting restart"

systemctl restart listen

exit 0