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
            v1, v2, v3 = map(float, line_values[1:4])
            mqtt_client.publish('/current/1', v1)   
            mqtt_client.publish('/current/2', v2)   
            mqtt_client.publish('/current/3', v3)   
    
    except:
        traceback.print_exc()
            
    finally:
        ser.close()
        mqtt_client.disconnect()

if __name__ == '__main__':
    run()
