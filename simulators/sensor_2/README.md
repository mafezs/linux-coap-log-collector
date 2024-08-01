# CoAP Sensor 2

## Overview

This CoAP sensor simulates environmental data adjustments based on incoming sensor data (Sensor1). It provides functionality for:
1. **Receiving Sensor Data**: Accepts POST requests with temperature and humidity data.
2. **Adjusting Internal Conditions**: Adjusts internal temperature and humidity based on the received data.
3. **Logging**: Records operations and adjustments in a log file.

## Configuration

### sensor_2.conf

This file contains configuration settings for the sensor. Ensure to modify it according to your environment.
Make sure to update these settings to match your environment and server configuration.

## Installation

### Dependencies

1. Ensure you have Python 3 installed. You can do this with the following commands:

**For Debian/Ubuntu:**

```sh
sudo apt-get update 
sudo apt-get install python3 python3-pip
```
### Python Dependencies
* aiocoap
* configparser
1. Clone the repository:
```sh
git clone https://github.com/mafezs/linux-coap-log-collector.git
cd linux-coap-log-collector/simulators/sensor_2/
```
2. Install the required Python packages:
```sh
pip3 install -r requirements.txt
```
## Usage
1. Ensure the sensor.conf file is properly configured.
2. Start the CoAP sensor:
```sh
python3 sensor_2.py
```
This will start the sensor, which will begin listening for incoming CoAP POST requests and log adjustments to the specified log file in the configuration file.
