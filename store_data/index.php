<?php

	$db = new SQLite3('home_data.sqlite3', SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);
	$ds18b20[] = array();
	$dht11[] = array();

	$statement = $db->prepare('SELECT * FROM `ds18b20` where date = ? ORDER BY `id` ASC LIMIT 0, 300;');
	date_default_timezone_set('Europe/Athens');
	$now_date = date("d-M-Y");
	$statement->bindValue(1, $now_date);


	$result = $statement->execute();
	$result->finalize();


	while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
		$ds18b20[] = array("date"=>$row['date'], "time"=>$row['time'], "tempr"=>$row['tempr']);
	}

	// echo json_encode($dht11);

	$st_nd = $db->prepare('SELECT * FROM `dht11` where date = ? ORDER BY `id` ASC LIMIT 0, 300;');
	$now_date = date("d-M-Y");
	$st_nd->bindValue(1, $now_date);


	$rslt_nd = $st_nd->execute();
	$rslt_nd->finalize();


	while ($row = $rslt_nd->fetchArray(SQLITE3_ASSOC)) {
		$dht11[] = array("date"=>$row['date'], "time"=>$row['time'], "tempr"=>$row['tempr'], "humidity"=>$row['humidity']);
	}

	$db->close();


?>



<!DOCTYPE html>
<html>
<head>
	<title>Tsaklidis Home temperatures</title>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.3/Chart.min.js"></script>
	<style type="text/css">
		#temperature_chart, #dht_11_hum, #temps_dht_11{max-width: 500px;display: inline-block !important;}
	</style>
</head>
<body>
	<p>Values for <?php echo $now_date; ?></p>
	<canvas id="temperature_chart" width="400" height="400"></canvas>
	<canvas id="temps_dht_11" width="400" height="400"></canvas>
	<canvas id="dht_11_hum" width="400" height="400"></canvas>
	<script>
		var temps = [<?php 
			foreach ($ds18b20 as $val) {
				foreach ($val as $key => $value) {
					if ($key == 'tempr') {
						echo $value . ',';
					}

				}
			}
		?>];

		var times = [<?php 
			foreach ($ds18b20 as $val) {
				foreach ($val as $key => $value) {
					if ($key == 'time') {
						echo "'" . $value . "',";
					}

				}
			}
		?>];
		var ctx = document.getElementById("temperature_chart").getContext('2d');
		var myChart = new Chart(ctx, {
		    type: 'line',
		    data: {
		        labels: times,
		        datasets: [{
		            label: 'Temperature (DS18B20)',
		            data: temps,
		            "fill":false,
		            backgroundColor: [
		                'rgba(255, 99, 132, 0.6)',

		            ],
		            borderColor: [
		                'rgba(255,99,132,1)',

		            ],
		            borderWidth: 1
		        }]
		    },
		    options: {
		    	responsive: true,
		        scales: {
		            yAxes: [{
		                ticks: {
		                    // beginAtZero:true,

		                }
		            }]
		        }
		    }
		});




		var temps_dht_11 = [<?php 
			foreach ($dht11 as $val) {
				foreach ($val as $key => $value) {
					if ($key == 'tempr') {
						echo $value . ',';
					}

				}
			}
		?>];

		var times_nd = [<?php 
			foreach ($dht11 as $val) {
				foreach ($val as $key => $value) {
					if ($key == 'time') {
						echo "'" . $value . "',";
					}

				}
			}
		?>];

		var hum = [<?php 
			foreach ($dht11 as $val) {
				foreach ($val as $key => $value) {
					if ($key == 'humidity') {
						echo "'" . $value . "',";
					}

				}
			}
		?>];

		var ctx = document.getElementById("dht_11_hum").getContext('2d');
		var myChart = new Chart(ctx, {
		    type: 'line',
		    data: {
		        labels: times_nd,

		        datasets: [{ 
		                data: hum,
		                label: "Humidity (DHT-11)",
		                borderColor: "#3e95cd",
		                fill: false
		              }, 
		            ]
		    },
		    options: {
		    	responsive: true,
		        scales: {
		            yAxes: [{
		                ticks: {
		                    // beginAtZero:true,

		                }
		            }]
		        }
		    }
		});

		var ctx = document.getElementById("temps_dht_11").getContext('2d');
		var myChart = new Chart(ctx, {
		    type: 'line',
		    data: {
		        labels: times_nd,
		        datasets: [{
		            label: 'Temperature (DHT-11)',
		            data: temps_dht_11,
		            "fill":false,
		            backgroundColor: [
		                'rgba(60, 99, 132, 0.6)',

		            ],
		            borderColor: [
		                'rgba(60,99,132,1)',

		            ],
		            borderWidth: 1
		        }]

		    },
		    options: {
		    	responsive: true,
		        scales: {
		            yAxes: [{
		                ticks: {

		                }
		            }]
		        }
		    }
		});

	</script>
</body>
</html>