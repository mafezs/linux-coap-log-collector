# CoAP Server for IoT Data Logging

## Overview

This CoAP server handles authentication and data logging for IoT devices. It supports the following functionalities:
1. **Authentication**: Validates users based on hashed credentials and issues tokens.
2. **Data Logging**: Receives POST requests, logs data, and manages token-based access.

## Configuration

### coap_server.conf

This file contains the server configuration settings. Ensure to modify it according to your environment.

### credentials.txt

This file contains user credentials for authentication with the CoAP server. Each line represents a single user's credentials in the format `username:hashed_password`. 

**Default credentials**: `username:password` (the password should be changed and hashed before use).

## Installation

## Dependencies

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
1. Clone the repository:

```sh
Copy code
git clone https://github.com/mafezs/linux-coap-log-collector.git
cd linux-coap-log-collector/server/
```
2. Install the required Python packages:

```sh
pip3 install -r requirements.txt
```

## Usage
1. Ensure the coap_server.conf and credentials.txt files are properly configured.
2. Start the CoAP server:

```sh
python3 coap_server.py
```
