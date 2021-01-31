#!/usr/bin/env python3

import traceback
import serial
import paho.mqtt.client as paho

MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883

def run():
    try:
        ser = serial.Serial('/dev/ttyAMA0', 38400)
        mqtt_client= paho.Client("current")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        line = ser.readline().decode('utf-8').strip()
        line_values = line.split()

        if len(line_values) >= 4:
            c_values = list(map(float, line_values[1:4]))
            for i,v in enumerate(c_values):
                mqtt_client.publish('/current/%d' % (i+1), v)   
    
    except:
        traceback.print_exc()
            
    finally:
        ser.close()
        mqtt_client.disconnect()

if __name__ == '__main__':
    run()
