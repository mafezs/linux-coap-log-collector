# CoAP Sensor 1

## Overview

This CoAP sensor simulates sensor data generation and sends it to a CoAP server. It supports the following functionalities:
1. **Data Generation**: Simulates temperature and humidity sensor data.
2. **Data Logging**: Saves generated data to a JSON file and logs events.
3. **Data Transmission**: Sends the generated data to a specified CoAP listener (Sensor2).

## Configuration

### sensor_1.conf

This file contains the sensor configuration settings. Ensure to modify it according to your environment.

## Installation

### System Dependencies

Ensure you have Python 3 installed. You can do this with the following commands:

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
cd linux-coap-log-collector/simulators/sensor_1/
```
2. Install the required Python packages:
```sh
pip3 install -r requirements.txt
```
## Usage
1. Ensure the sensor_1.conf file is properly configured.
2. Start the CoAP sensor:
```sh
python3 sensor_1.py
```
