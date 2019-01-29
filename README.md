# Home Temperature Station

The hardware is:
<ul>
	<li>Raspberry Pi</li>
	<li>DS18B20 for temperature (±0.1°C)</li>
	<li>DHT-11 for Humidity (5% accuracy) and temperature (±2°C accuracy)</li>
</ul>
The data is stored on sqlite3.
<p>Check on line https://tsaklidis.gr/home/index.php</p>
<p>Sqlite3 file is available <a href="https://tsaklidis.gr/home/home_data.sqlite3">here</a> </p>


> TODO:
> <ul>
>	<li>On data loss, save all the data saved to pickle file</li>
>	<li>Remove 'sh: 1: modprobe: not found' from info.log (printed from DS18B20)</li>
> </ul>


I use the system's cron to run the script and monitor the output. To edit the cron use 

```shell
crontab -e
```
And run the script every 5 minutes
```shell
*/5 * * * * python ~/send_data.py >> ~/info.log 2>&1
```

The system cycle is:
```mermaid
graph TD;
  DS18B20-->Raspberry;
  DHT11-->Raspberry;
  Raspberry-->Server;
  Server-->Browser;
```
![](screens/1.png)