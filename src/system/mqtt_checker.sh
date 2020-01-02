if [ "`ps -aux | grep /usr/sbin/mosquitto | wc -l`" == "1" ]

then

        echo "mosquitto wasnt running so attempting restart" >> /home/$USER/Desktop/home-station/src/logs/mqtt_checker.log

        systemctl restart mosquitto

        exit 0

fi

echo "$SERVICE is currently running" >> /home/$USER/Desktop/home-station/src/logs/mqtt_checker.log

exit 0