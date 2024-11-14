#!/usr/bin/env python3
import os
import configparser
import serial
import asyncio
import aiomqtt

from pymqtt_hass.items import Device


current_folder = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = 'config.ini'
PYMQTT_HASS_CONFIG_FILE = 'pymqtt_hass_config.json'

def get_config():
    ret = {}
    config = configparser.ConfigParser()
    config.read(os.path.join(current_folder, CONFIG_FILE))

    ret['MQTT_HOST'] = config.get('MQTT', 'HOST')
    ret['MQTT_PORT'] = config.getint('MQTT', 'PORT', fallback=1883)
    ret['MQTT_USERNAME'] = config.get('MQTT', 'USERNAME')
    ret['MQTT_PASSWORD'] = config.get('MQTT', 'PASSWORD')

    ret['NORMAL_REFRESH_PERIOD'] = config.getint('SYSTEM', 'NORMAL_REFRESH_PERIOD')
    ret['BOOST_REFRESH_PERIOD'] = config.getint('SYSTEM', 'BOOST_REFRESH_PERIOD')

    return ret

class MQTTDevice:

    def __init__(self):
        self.config = get_config()
        self.client = None
        self.device = None
        self.device_topic = None

        self.boost_status = 0

    async def boost_toggle(self):

        boost_topic = '/'.join([
            self.device.get_device_topic(),
            'boost',
        ])
        while True:
            await self.client.subscribe(boost_topic)
            async with self.client.messages() as messages:
                async for message in messages:
                    if message.payload == b'ON' and self.boost_status == 0:
                        print("ON")
                        self.boost_status = 1
                    if message.payload == b'OFF' and self.boost_status == 1:
                        print("OFF")
                        self.boost_status = 0
                    # Signal boost value changed
                    self.event_boost_changed.set()


    async def periodic(self, time_s, boost):
        while True:
            if self.boost_status == boost:
                self.event_refresh.set()
                await asyncio.sleep(time_s)
            else:
                await self.event_boost_changed.wait()
                self.event_boost_changed.clear()


    async def publisher(self):
        while True:
            try:
                # Read values from the serial line
                ser = serial.Serial('/dev/ttyAMA0', 38400)
                line = ser.readline().decode('utf-8').strip()
                line_values = line.split()

                # Convert all read values to float
                values = list(map(float, line_values))

                # Drop the node id and temperature if any
                values = values[1:4]

                device_topic = self.device.get_device_topic()

                # Publish the total consumed power
                topic = '/'.join([
                    device_topic,
                    'power',
                    'total',
                ])
                await self.client.publish(topic, sum(values))

                # Publish each value (one per phase) on appropriate topic
                for i, value in enumerate(values):
                    topic = '/'.join([
                        device_topic,
                        'power',
                        'phase_{}'.format(i+1),
                    ])
                    await self.client.publish(topic, value)

            except:
                traceback.print_exc()
                    
            finally:
                ser.close()

            # Block until event_refresh in fired
            await self.event_refresh.wait()
            self.event_refresh.clear()

    async def send_discovery(self):
         for topic, payload in self.device.discovery_items():
             await self.client.publish(topic, payload)


    async def main(self):
        ''' main method
            Launches tasks

            publisher : collect and publish on MQTT, then wait for an event
            period: triggers the publish signal if given boost is the actual one, or wait for boost changed

            boost_toogle: subscribes on the boost topic, and changes config accordingly
        '''
        client_config = {
            'hostname': self.config['MQTT_HOST'],
            'port': self.config['MQTT_PORT'],
            'username': self.config['MQTT_USERNAME'],
            'password': self.config['MQTT_PASSWORD'],
        }

        loop = asyncio.get_running_loop() 

        async with aiomqtt.Client(**client_config) as client:
            self.client = client

            self.device = Device(self.client, os.path.join(current_folder, PYMQTT_HASS_CONFIG_FILE))

            await self.send_discovery()

            self.event_refresh = asyncio.Event(loop=loop) 
            self.event_boost_changed = asyncio.Event(loop=loop)

            publish_tk = loop.create_task(self.publisher())
            boost_toggle_tk = loop.create_task(self.boost_toggle())

            period_normal_tk = loop.create_task(
                self.periodic(self.config['NORMAL_REFRESH_PERIOD'], 0)
            )
            period_boost_tk = loop.create_task(
                self.periodic(self.config['BOOST_REFRESH_PERIOD'], 1)
            )

            await publish_tk
            await boost_toggle_tk
            await period_normal_tk
            await period_boost_tk

if __name__ == '__main__':
    asyncio.run(MQTTDevice().main())

