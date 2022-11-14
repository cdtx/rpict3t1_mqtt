# Power sensor based on RPICT3T1 for home-assistant

RPICT3T1 is a shield for raspberry pi that uses current transformers to measure the electrical power carrier by a wire.
Its sold on lechacal.com

## The product
- Raspberry pi 2
- RPICT3T1\_v2.4 (bought on lechacal.com)
- 3 current transformers (sct-013-000)

## Environment installation on RPI

Install pip for python3
```bash
sudo apt-get install python3-pip
```

Install serial (I did not manage to make it work when installing it using pip)
``` bash
sudo apt-get install python3-serial
```

Clone the current project
```bash
git clone https://github.com/cdtx/rpict3t1_mqtt
```

# Configuration

The main script expects to read a file named config.ini in the same folder, containing the following keys :

``` ini
[MQTT]
# url or ip to the mqtt broker
HOST = 
# port to connect to the mqtt broker
PORT =
# mqtt broker username/password
USERNAME =
PASSWORD =
``` 


## Links

- [Shield home page](http://lechacal.com/wiki/index.php?title=RPICT3T1)
- [Shield configuration](http://lechacal.com/wiki/index.php?title=Attiny_Over_Serial_Configuration_A2)

