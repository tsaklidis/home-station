<?php
	if ($_SERVER['REQUEST_METHOD'] === 'POST') {

		$ip = gethostbyname('http://tsaklidis.noip.me/');  

		if ($_SERVER['HTTP_CF_CONNECTING_IP'] = $ip) { // Don't forget to disable this if you run on your project
			// Get JSON as a string
			$json_str = file_get_contents('php://input');
			// Get as an object
			$data = json_decode($json_str, True);
			$db = new SQLite3('home_data.sqlite3', SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);

			// The old table of dht11 is used for dht22 data
			$dht22 = $db->prepare('INSERT INTO "dht11" ("date", "time", "tempr", "humidity")
			    VALUES (:date_r, :time, :tempr, :humidity)');

			$dht22->bindValue(':date_r', $data["DHT22"][0]["date"]);
			$dht22->bindValue(':time', $data["DHT22"][0]["time"]);
			$dht22->bindValue(':tempr', $data["DHT22"][0]["tempr"]);
			$dht22->bindValue(':humidity', $data["DHT22"][0]["humidity"]);
			$dht22->execute();

			$ds18b20 = $db->prepare('INSERT INTO "ds18b20" ("date", "time", "tempr")
			    VALUES (:date_r2, :time2, :tempr2)');

			$ds18b20->bindValue(':date_r2', $data["DS18B20"][0]["date"]);
			$ds18b20->bindValue(':time2', $data["DS18B20"][0]["time"]);
			$ds18b20->bindValue(':tempr2', $data["DS18B20"][0]["tempr"]);
			$ds18b20->execute();

			$db->close();
			http_response_code(201);

		}
		else{
			echo "<h1>Not allowed</h1>";
			http_response_code(403);
		}

	}
	else{
		echo "<h1>Not allowed</h1>";
		http_response_code(403);
	}

?>
