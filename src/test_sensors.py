import DHT11
import DHT22
import DS18B20


def check_data():
    data = [
        DHT11.read_humidity(),
        DHT11.read_temp(),
        DHT22.read_humidity(),
        DHT22.read_temp(),
        DS18B20.read_temp()
    ]
    return all(isinstance(x, (int, float)) for x in data)


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    d = check_data()
    if d:
        print 'Sensors are up\n'

