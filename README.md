# Linux CoAP Log Collector

This repository contains the components of a log collection system using the CoAP protocol for Linux-based environments. It includes a CoAP server with authentication and token-based communication, a Linux-based agent for log collection and system monitoring, and sensor simulators for testing purposes.

## Components

### Server
The CoAP server handles authentication and token issuance, and it collects data from authenticated clients.

- **Directory**: `server/`
- **Main Script**: `coap_server.py`
- **Configuration File**: `coap_server.conf`
- **Credentials File**: `credentials.txt`

### Agent
The agent is designed to run on lightweight Linux systems like Raspbian for IoT purposes, collecting logs and system information to send to the central server.

- **Directory**: `agent/`
- **Main Script**: `coap_agent.py`
- **Configuration File**: `coap_agent.conf`

### Sensor Simulators - Testing
These scripts simulate 2 sensors to test the functionality of the server and agent in virtual environments.

- **Directory**: `simulators/`
- **Scripts**: `sensor_1.py`, `sensor_2.py`

## Dependencies

The system is written in Python 3, so ensure you have Python 3 and `pip` installed. Common dependencies for all components are:

```shell
sudo apt-get update 
sudo apt-get install python3 python3-pip inotify-tools
pip3 install aiocoap psutil
pip3 install aiocoap
```
Each component (server, agent, sensors) has its own requirements.txt file, which can be installed with:

```sh
pip3 install -r requirements.txt
```
## Setup 
1. Clone the repository:
```sh
git clone https://github.com/mafezs/linux-coap-log-collector.git
cd linux-coap-log-collector
```
2. Server Setup:
* Navigate to the server/ directory.
* Configure the coap_server.conf file and credentials.txt according to your environment.
* Start the CoAP server with:
```sh
python3 coap_server.py
```
3. Agent Setup:
* Install the agent on a target device.
* Configure the coap_agent.conf file with the appropriate server address and other settings.
Start the agent with:
```sh
python3 coap_agent.py
```
4. Sensor Simulators Setup:
* Install the sensors on separate devices where the agents are also installed.
* Configure the sensor_1.conf and sensor_2.conf files as needed.
* Start each sensor simulator with:
```sh
python3 sensor_1.py
python3 sensor_2.py
```
## Usage
### Server
The server handles authentication and data logging. Ensure it is running and properly configured before starting the agents and sensors.
### Agent
The agent collects logs and system information and sends them to the CoAP server. Make sure the configuration file points to the correct server address.
### Sensors
The sensor simulators generate and send simulated sensor data to the CoAP server. Use these simulators to test the system's functionality.
