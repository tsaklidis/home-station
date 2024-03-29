import os
import time
import datetime
import sqlite3
import RPi.GPIO as GPIO

start_tmp = 80


class FanDB:
    # data example
    # fan_data = {
    #     'date':'2019-05-06',
    #     'time':'17:15',
    #     'fan_status':1,
    #     'cpu':45.6,
    #     'gpu':70.4
    # }

    def __init__(self):

        create_tbl = """CREATE TABLE IF NOT EXISTS fan_logs(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            date TEXT,
                            time TEXT,
                            fan_status INTEGER,
                            cpu REAL,
                            gpu REAL);"""

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.conn = sqlite3.connect(dir_path + '/the_database.sqlite')
        self.cur = self.conn.cursor()

        self.cur.execute(create_tbl)
        self.conn.commit()

    def insert(self, fan_data):
        self.cur.execute('INSERT INTO fan_logs (date, time, fan_status, cpu, gpu) VALUES (?, ?, ?, ?, ?)',
                         (fan_data['date'], fan_data['time'], fan_data['fan_status'], fan_data['cpu'], fan_data['gpu']))
        self.conn.commit()

    def __del__(self):
        self.conn.close()


class FanControl:
    pin = 23
    status_led = 24
    spinning = False

    def _prepare(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.setup(self.status_led, GPIO.OUT)
            GPIO.setwarnings(False)
        except Exception as e:
            exit(e)

    def _power_led(self, power):
        GPIO.output(self.status_led, power)

    # Use this to log to file
    # def log_on_file(self, data):
        # fileLog = open('/home/pi/Desktop/sensors/fan.log', 'a+', 0)
        # t = time.time()
        # stamp = datetime.datetime.fromtimestamp(
        #     t).strftime('%Y/%m/%d %H:%M:%S - ')
        # fileLog.write(stamp + s + "\n")
        # fileLog.close()

        # use like log_on_file("Fan:" + str(power) + " CPU: " + str(cpu_temp) + " GPU: " + str(gpu_temp))  # noqa

    def log(self, data):
        t = time.time()
        date, that_time = datetime.datetime.fromtimestamp(
            t).strftime('%Y-%m-%d|%H:%M:%S').split('|')

        fan_db = FanDB()

        data['date'] = date
        data['time'] = that_time
        fan_db.insert(data)

    # Resets all GPIO ports used by this program
    def exitPin(self):
        GPIO.cleanup()

    def spin(self, power):
        self._prepare()
        # Inverting passed power, check circuit transistor to investigate
        # LOW starts the fan and HIGH stops fan
        GPIO.output(self.pin, not power)

        fan_data = {
            'fan_status': power,
            'cpu': cpu_temp,
            'gpu': gpu_temp
        }

        self.log(fan_data)
        self._power_led(power)
        self.spinning = power


fan = FanControl()
while True:
    # res_g has "temp=46.2'C\n"
    res_g = os.popen('/opt/vc/bin/vcgencmd measure_temp').readline()
    gpu_temp = float((res_g.replace("temp=", "").replace("'C\n", "")))

    # res_c has '43470\n'
    res_c = os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline()
    cpu_temp = round(float((res_c.replace("\n", ""))) / 1000, 1)

    if (cpu_temp > start_tmp) or (gpu_temp > start_tmp):
        if not fan.spinning:
            fan.spin(True)
    elif fan.spinning:
        fan.spin(False)
        fan.exitPin()

    if (cpu_temp > 50) or (gpu_temp > 50):
        # take some extra time to cool the cpu
        time.sleep(40)
    else:
        time.sleep(15)
