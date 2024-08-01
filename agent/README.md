# CoAP Agent for IoT Data Logging

## Overview

This CoAP agent handles the collection and transmission of log data to a CoAP server. It supports the following functionalities:
1. **Token Authentication**: Obtains and manages tokens for secure communication with the CoAP server.
2. **Log Collection**: Reads specified log files and system metrics.
3. **Data Transmission**: Sends collected data to the CoAP server.

## Configuration

### agente.conf

This file contains the agent configuration settings. Ensure to modify it according to your environment. 

- **[paths]**: Specify the paths to the log files. Ensure you have the appropriate read and write permissions for the log files.
- **[coap]**: Set the CoAP server IP address (default is localhost), port, and URI path parts (must match the server configuration).
- **[auth]**: Provide the credentials for the CoAP server. The default credentials are `username:password`, which should be changed.

## Installation

### System Dependencies

Ensure you have Python 3 installed. You can do this with the following commands:

**For Debian/Ubuntu:**
```sh
sudo apt-get update 
sudo apt-get install python3 python3-pip inotify-tools
```
### Python Dependencies
* aiocoap
* configparser
* psutil
* logging

1. Clone the repository:
```sh
git clone https://github.com/yourusername/coap-agent.git
cd agent/
```
2. Install the required Python packages:
```sh
pip3 install -r requirements.txt
```
## Usage
1. Ensure the coap_agent.conf file is properly configured.
2. Start the CoAP agent:
```sh
python3 coap_agent.py
```