Deploying the RPICT3T1 shield and puch values to a MQTT broker

## Environment installation on RPI

Install pip for python3
```bash
sudo apt-get install python3-pip
```

Install paho-mqtt
```bash
sudo pip3 install paho-mqtt
```

Install serial (I have been unable to make it work when installing it using pip)
``` bash
sudo apt-get install python3-serial
```

# The product
- RPICT3T1 (bought on lechacal.com)
- 3 current transformers (sct-013-000)

## Read values
On a raspberry pi with serial line properly activated
```bash
stty -F /dev/ttyAMA0 raw speed 38400
cat /dev/ttyAMA0
```

## Configure the shield
The config is in the file rpict.conf

lechacal.com provides a python tool to interact with the shield's configuration :
```bash
wget lechacal.com/RPICT/tools/lcl-rpict-config.py.zip
unzip lcl-rpict-config.py.zip
```

To push a configuration :
```bash
./lcl-rpict-config.py -a -w rpict.conf
```
Note : option -a is the shields auto reboot


# Push to MQTT
The module mqtt.py does the job
To run periodically (every minute in the example below) using cron, launch cron editor
```bash
crontab -e
```
and add line : 
```
* * * * * /home/pi/.../mqtt.py
```

