#!/usr/bin/env python3
import os
import time
import asyncio
import functools
import signal
import traceback
import configparser
import serial
from paho.mqtt.client import Client as PahoClient
from distutils.util import strtobool

from pymqtt_hass.items import Device

current_folder = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = 'config.ini'
PYMQTT_HASS_CONFIG_FILE = 'pymqtt_hass_config.json'

# dict protected with an asyncio Semaphore
dynamic_config_semaphore = asyncio.Semaphore(1)
dynamic_config = {
    'boost':False,
}


def ask_exit(signame, loop):
    print("got signal %s: exit" % signame)
    loop.stop()

class AsyncPowerMeter():
    def __init__(self, loop):
        self.loop = loop
        self.dynamic_config_changed_event = asyncio.Event()

    def get_config(self):
        ret = {}

        parser = configparser.ConfigParser()
        parser.read(os.path.join(current_folder, CONFIG_FILE))

        ret['MQTT_HOST'] = parser.get('MQTT', 'HOST')
        ret['MQTT_PORT'] = parser.getint('MQTT', 'PORT', fallback=1883)
        ret['MQTT_USERNAME'] = parser.get('MQTT', 'USERNAME')
        ret['MQTT_PASSWORD'] = parser.get('MQTT', 'PASSWORD')

        return ret

    def on_message(self, client, userdata, message):
        print('Message received {}:{}'.format(message.topic, message.payload))
        
        end_topic = message.topic.split('/')[-1]
        if end_topic == 'boost':
            try:
                boost = strtobool(message.payload.decode('ascii'))
            except Exception as e:
                print('Error reading the .../boost topic: {}'.format(e))
                # Default to no boost
                boost = False
            finally:
                if boost:
                    self.dynamic_config_changed_event.set()
                else:
                    self.dynamic_config_changed_event.clear()

    def mqtt_init(self):
        # Initialize MQTT client
        self.client = PahoClient()
        # Set the client options
        self.client.enable_logger()
        # Configure callbacks
        self.client.on_message = self.on_message

        self.client.username_pw_set(self.config['MQTT_USERNAME'], self.config['MQTT_PASSWORD'])
        # Connect the mqtt client
        self.client.connect(self.config['MQTT_HOST'], self.config['MQTT_PORT'])

        # Get the configured home-assistant device
        self.device = Device(self.client, os.path.join(current_folder, PYMQTT_HASS_CONFIG_FILE))
        # Send the hass's device discovery
        self.device.send_discovery()

        self.device_topic = self.device.get_device_topic()

        topic = '/'.join([
            self.device_topic,
            'boost',
        ])
        self.client.subscribe(topic, 0)

        self.client.loop_start()

    def config(self):
        # Read the static configuration
        self.config = self.get_config()

        # Configure the MQTT client and publish homeassistant discovery
        self.mqtt_init()

        # Following implementation comes from :
        # https://docs.python.org/3.7/library/asyncio-eventloop.html#set-signal-handlers-for-sigint-and-sigterm
        for signame in {'SIGINT', 'SIGTERM'}:
            self.loop.add_signal_handler(
                getattr(signal, signame),
                functools.partial(ask_exit, signame, self.loop))

    def serial_read(self):
        # Read values from the serial line
        print('read')

        ser = serial.Serial('/dev/ttyAMA0', 38400)
        line = ser.readline().decode('utf-8').strip()
        ser.close()

        line_values = line.split()

        # Convert all read values to float
        values = list(map(float, line_values))

        # Drop the node id and temperature if any
        values = values[1:4]

        return values
        
    def mqtt_publish(self, values):
        # Publish the total consumed power
        print('publish')

        topic = '/'.join([
            self.device_topic,
            'power',
            'total',
        ])
        self.client.publish(topic, sum(values))

        # Publish each value (one per phase) on appropriate topic
        for i, value in enumerate(values):
            topic = '/'.join([
                self.device_topic,
                'power',
                'phase_{}'.format(i+1),
            ])
            self.client.publish(topic, value)


    async def main(self):
        self.config()

        while True:
            values = self.serial_read()
            self.mqtt_publish(values)

            try:
                await asyncio.wait_for(self.dynamic_config_changed_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                # Expected behaviour when not in boost mode
                pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncPowerMeter(loop).main())
    loop.close()

