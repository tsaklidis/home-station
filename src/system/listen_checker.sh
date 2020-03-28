#!/bin/bash

RIGHT_NOW=(date +"%F_%R")

if [ "`systemctl show -p ActiveState --value listen`" = "active" ]
then
    #service is currently running
    exit 0
fi

echo "$RIGHT_NOW listen (listen.service) wasnt running attempting restart" >> /home/$USER/Desktop/home-station/src/logs/listen.log

systemctl restart listen

exit 0