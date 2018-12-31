#!/usr/bin/env python3
from influxdb import InfluxDBClient
import time
import datetime
import serial


DATABASE = 'sensor'
HOST = '10.0.0.190'
PORT = 8086
SERIAL_DEV = '/dev/ttyUSB0'
SERIAL_RATE = 115200
HOSTNAME = 'rpi3'


def meas(meas, fields, value, timestamp, tags):
    meas = {
        "measurement": meas,
        "tags": {
            "host": HOSTNAME,
        },
        "time": timestamp,
        "fields": {
            fields: value
        }
    }
    meas['tags'].update(tags)
    return meas


if __name__ == '__main__':
    s = serial.Serial(SERIAL_DEV, SERIAL_RATE)

    client = InfluxDBClient(host=HOST, port=PORT, database=DATABASE)
    client.create_database(DATABASE)

    print("RUN")

    while True:
        r = s.readline().rstrip().decode('ascii')
        l = r[1:len(r)-1].split(';')

        if len(l) != 12 and len(l) != 14:
            continue

        ctime = datetime.datetime.utcnow()
        sid = l[4]
        sensor_type = l[10]
        lqi = int(l[2])
        battery = float(l[5]) / 1000
        adc1 = float(l[8]) / 1000
        adc2 = float(l[9]) / 1000

        json_body = []

        if len(l) == 12:
            tags = {'sid' : sid, 'sensor_type': sensor_type}

            temperature = float(l[6]) / 100
            humidity = float(l[7]) / 100
            pressure = float(l[11])

            json_body.append(meas('system', 'lqi', lqi, ctime, tags))
            json_body.append(meas('system', 'battery', battery, ctime, tags))
            json_body.append(meas('system', 'adc1', adc1, ctime, tags))
            json_body.append(meas('system', 'adc2', adc2, ctime, tags))

            json_body.append(meas('sensor', 'temperature', temperature, ctime, tags))
            json_body.append(meas('sensor', 'humidity', humidity, ctime, tags))
            json_body.append(meas('sensor', 'pressure', pressure, ctime, tags))

        if len(l) == 14:
            sensor_mode = int(l[6])

            tags = {'sid' : sid, 'sensor_mode': sensor_mode, 'sensor_type': sensor_type}

            x = float(l[11]) / 10
            y = float(l[12]) / 10
            z = float(l[13]) / 10

            json_body.append(meas('system', 'lqi', lqi, ctime, tags))
            json_body.append(meas('system', 'battery', battery, ctime, tags))
            json_body.append(meas('system', 'adc1', adc1, ctime, tags))
            json_body.append(meas('system', 'adc2', adc2, ctime, tags))

            json_body.append(meas('sensor', 'x', x, ctime, tags))
            json_body.append(meas('sensor', 'y', y, ctime, tags))
            json_body.append(meas('sensor', 'z', z, ctime, tags))

        client.write_points(json_body)
        time.sleep(10)
