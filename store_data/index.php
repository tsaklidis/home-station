<?php

function validateDate($date, $format = 'd-M-Y'){
    $d = DateTime::createFromFormat($format, $date);
    return $d && $d->format($format) == $date;
}

	$db = new SQLite3('home_data.sqlite3', SQLITE3_OPEN_CREATE | SQLITE3_OPEN_READWRITE);
	$ds18b20[] = array();
	$dht11[] = array();
	if(isset($_GET['date'])) {
		if (validateDate($_GET['date'])) {
			$now_date = $_GET['date'];
		}
		else{
			$now_date = date("d-M-Y");
		}
	}
	else{
		$now_date = date("d-M-Y");
	}

	if(isset($_GET['hours'])) {
		$hours_limit = $_GET['hours'];
		if (is_numeric($hours_limit) && ($hours_limit < 25 && $hours_limit >= 1)) { // 24 hours == 288 rows
		 	$hours_limit = round($hours_limit * 12); // 12 samples every 5 minutes
		 } 
		else{
			$hours_limit = 30;
		}
	}
	else{
		$hours_limit = 30;
	}


	$statement = $db->prepare('SELECT * FROM `ds18b20` where date = ? ORDER BY `id` DESC LIMIT '. $hours_limit .' ;');
	date_default_timezone_set('Europe/Athens');



	$statement->bindValue(1, $now_date);

	$result = $statement->execute();
	$result->finalize();


	while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
		$ds18b20[] = array("date"=>$row['date'], "time"=>$row['time'], "tempr"=>$row['tempr']);
	}

	// echo json_encode($dht11);

	$st_nd = $db->prepare('SELECT * FROM `dht11` where date = ? ORDER BY `id` DESC LIMIT '. $hours_limit .' ;');
	$st_nd->bindValue(1, $now_date);


	$rslt_nd = $st_nd->execute();
	$rslt_nd->finalize();


	while ($row = $rslt_nd->fetchArray(SQLITE3_ASSOC)) {
		$dht11[] = array("date"=>$row['date'], "time"=>$row['time'], "tempr"=>$row['tempr'], "humidity"=>$row['humidity']);
	}

	$st = $db->prepare('SELECT tempr FROM `ds18b20` where date = ? ORDER BY `id` DESC LIMIT 1;');
	$st->bindValue(1, $now_date);

	$last = $st->execute();
	$last->finalize();

	$last_tempr = $last->fetchArray(SQLITE3_ASSOC);

	$st_hum = $db->prepare('SELECT humidity FROM `dht11` where date = ? ORDER BY `id` DESC LIMIT 1;');
	$st_hum->bindValue(1, $now_date);

	$last_hum = $st_hum->execute();
	$last_hum->finalize();

	$last_humidity = $last_hum->fetchArray(SQLITE3_ASSOC);

	$db->close();

?>
<!DOCTYPE html>
<html>
<head>
	<title>Tsaklidis Home Live Temperatures</title>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta property="og:image" content="https://gitlab.com/steftsak/home-station/raw/master/screens/1.png"/>
	<link rel="shortcut icon" type="image/icon" href="favicon.ico"/>

	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.2.1/css/bootstrap.min.css">
	<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

	<script src="https://code.jquery.com/jquery-1.12.4.js"></script>
	<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

	<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.7.3/Chart.min.js"></script>

	<style type="text/css">
		#temperature_chart, #dht_11_hum, #temps_dht_11{
			max-width: 600px;
			display: inline-block !important;
		}
		#hours{max-width: 70px;}
		.text{
			color: #fdfdfd;
			background-color: #3e95cd;
			display: block;
			padding: 10px;
			max-width: 340px;
			margin: 15px auto;
			border-radius: 3px;
		}
		.circle {
			width: 100px;
		    height: 100px;
		    border-radius: 50%;
		    color: #fff;
		    line-height: 100px;
		    text-align: center;
		}
		.color_one{background: #f76464;}
		.color_two{background: #52aacc;}
		.wrp{display:inline-block;}
		.wrp div{display: block; margin:5px;}
	</style>
</head>
<body>
	<div class="container-fluid">

		<div class="row">
			<div class="col-lg-12 text-center">
				<p class="text">Values for <?php echo $now_date; ?></p>
			</div>
		</div>
		<div class="row">
			<div class="col-lg-12 text-center">
				<div class="wrp">
					<div>Temperature</div>
					<div class="circle color_one"><?php echo round($last_tempr["tempr"], 1);?>&#8451;</div>
				</div>
				<div class="wrp">
					<div>Humidity</div>
					<div class="circle color_two"><?php echo $last_humidity["humidity"]; ?>%</div>
				</div>
			</div>
		</div>
		
		<div class="row">
			<div class="col-lg-12 text-center">
				<canvas id="temperature_chart"></canvas>
				<canvas id="temps_dht_11"></canvas>
				<canvas id="dht_11_hum"></canvas>
			</div>
		</div>



		<div class="row">
			<div class="col-lg-12 text-center">
				<form method="get" action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]);?>">
					Change date: <input type="text" class="text-center" name="date" id="datepicker">
					Hours range: <input type="number" class="text-center" value="3" name="hours" id="hours">
					<button class="btn btn-sm btn-info">OK</button>
				</form>
			</div>
		</div>
	</div>
	<script>

		$(document).ready(function(){

			$('#datepicker').datepicker({
			    dateFormat: 'dd-M-yy',
			    maxDate: '0',
			});

		});


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

		var temps_dht_11 = [<?php 
			foreach ($dht11 as $val) {
				foreach ($val as $key => $value) {
					if ($key == 'tempr') {
						echo $value . ',';
					}

				}
			}
		?>];

		var times_dht_11 = [<?php 
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

		var ctx = document.getElementById("temperature_chart").getContext('2d');
		var ctx_dht_11_hum = document.getElementById("dht_11_hum").getContext('2d');
		var ctx_temps_dht_11 = document.getElementById("temps_dht_11").getContext('2d');

		var same_options = {
		    	responsive: true,
		        scales: {
		            yAxes: [{
		                ticks: {
		                    // beginAtZero:true,
		                }
		            }]
		        }
		    };

		var myChart = new Chart(ctx, {
		    type: 'line',
		    data: {
		        labels: times.reverse(), // from left to the right, db returns max date first
		        datasets: [{
		            label: 'Temperature (DS18B20)',
		            data: temps.reverse(),
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
		    options: same_options
		});


		var myChart = new Chart(ctx_dht_11_hum, {
		    type: 'line',
		    data: {
		        labels: times_dht_11.reverse(),

		        datasets: [{ 
		                data: hum.reverse(),
		                label: "Humidity (DHT-11 +-5%)",
		                borderColor: "#3e95cd",
		                fill: true
		              }, 
		            ]
		    },
		    options: same_options
		});

		
		var myChart = new Chart(ctx_temps_dht_11, {
		    type: 'line',
		    data: {
		        labels: times_dht_11,
		        datasets: [{
		            label: 'Temperature (DHT-11 +-2*C)',
		            data: temps_dht_11.reverse(),
		            "fill":false,
		            backgroundColor: [
		                'rgba(60, 150, 40, 0.6)',

		            ],
		            borderColor: [
		                'rgba(60, 150, 40, 1)',

		            ],
		            borderWidth: 1
		        }]

		    },
		    options: same_options
		});

	</script>
</body>
</html>