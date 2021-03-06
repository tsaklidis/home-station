# Home Temperature Station

The hardware is:
<ul>
	<li>Raspberry Pi</li>
	<li>DS18B20 for temperature (±0.1°C)</li>
	<li>DHT-22 for Humidity (5% RH accuracy) and temperature (±0.5°C accuracy)</li>
</ul>
The data is stored on a remote server with the help of an API.
<p>API backend available here <a href="https://github.com/tsaklidis/LogingAPI">here</a> </p>

<p>Check the live version https://logs.tsaklidis.gr</p>


I use the system's cron to run the script and monitor the output. To edit the cron use 

```shell
crontab -e
```
And run the script every 5 minutes
```shell
*/5 * * * * python ~/send_data.py >> ~/info.log 2>&1
```

In order to run the fan.py script on each system start, add the file located at <a href="src/system/fan.service">src/system/fan.service</a>  to the lib folder
```shell
# nano /lib/systemd/system/fan.service

```


The flow is:
```mermaid
graph TD;
  DS18B20-->Raspberry;
  DHT11-->Raspberry;
  Raspberry-->API;
  API-->Browser;
```

I created an API system. You can use it in order to save your data. If you like sql + php version use the code on master.

> TODO:
> <ul>
>	<li>On data loss, save all the data saved to pickle file</li>
> </ul>

If you have any questions or problems running the scripts just contact me. 

![](photo/dark.png)

![](photo/dark_big_range.png)

![](photo/circuit.png)

<hr>

![](photo/case.jpg)

![](photo/board2.jpg)