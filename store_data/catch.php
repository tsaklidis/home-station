<?php
	if ($_SERVER['REQUEST_METHOD'] === 'POST') {

		$ip = gethostbyname('http://tsaklidis.noip.me/');

		if ($_SERVER['HTTP_CF_CONNECTING_IP'] = $ip) {
			// Get JSON as a string
			$json_str = file_get_contents('php://input');
			// Get as an object
			$data = json_decode($json_str, True);
			$db = new SQLite3('home_data.sqlite3', SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);

			$dht11 = $db->prepare('INSERT INTO "dht11" ("date", "time", "tempr", "humidity")
			    VALUES (:date_r, :time, :tempr, :humidity)');

			$dht11->bindValue(':date_r', $data["DHT11"][0]["date"]);
			$dht11->bindValue(':time', $data["DHT11"][0]["time"]);
			$dht11->bindValue(':tempr', $data["DHT11"][0]["tempr"]);
			$dht11->bindValue(':humidity', $data["DHT11"][0]["humidity"]);
			$dht11->execute();

			$ds18b20 = $db->prepare('INSERT INTO "ds18b20" ("date", "time", "tempr")
			    VALUES (:date_r2, :time2, :tempr2)');

			$ds18b20->bindValue(':date_r2', $data["DS18B20"][0]["date"]);
			$ds18b20->bindValue(':time2', $data["DS18B20"][0]["time"]);
			$ds18b20->bindValue(':tempr2', $data["DS18B20"][0]["tempr"]);
			$ds18b20->execute();

			$db->close();

		}
		else{
			echo "<h1>Not allowed</h1>";
		}

	}
	else{
		echo "<h1>Not allowed</h1>";
	}

?>