import asyncio
import json
import random
import os
import configparser
from aiocoap import *
from aiocoap.numbers.codes import Code
from datetime import datetime

# CoAP Sensor 1 Implementation
#
# This CoAP sensor simulates sensor data generation and sends it to a CoAP server. 
# It supports the following functionalities:
# 1. Data Generation: Simulates temperature and humidity sensor data.
# 2. Data Logging: Saves generated data to a JSON file and logs events.
# 3. Data Transmission: Sends the generated data to a specified CoAP server.

# Load configuration from sensor_1.conf
config = configparser.ConfigParser()
config.read('sensor_1.conf')

# Define file path for configuration variables and log files
DATA_FILE = config['sensor']['DATA_FILE']
LOG_FILE = config['sensor']['LOG_FILE']
SENSOR_ID = config['sensor']['SENSOR_ID']
URI_IP = config['sensor']['URI_IP']
URI_PORT = config['sensor']['URI_PORT']
URI_PATH = config['sensor']['URI_PATH']

# Ensure the directory exists
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Generate simulated sensor data
def generate_sensor_data():
    return {
        "sensor_id": SENSOR_ID,
        "timestamp": datetime.now().isoformat(),
        "temperature": round(random.uniform(15.0, 25.0), 2),
        "humidity": round(random.uniform(30.0, 70.0), 2)
    }

# Save sensor data to a JSON file
def save_sensor_data(data):
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
            with open(DATA_FILE, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)

        with open(DATA_FILE, 'w') as f:
            json.dump(existing_data, f, indent=4)

    except Exception as e:
        log_message(f"Error saving sensor data: {e}")

# Log messages to a log file
def log_message(message):
    timestamp = datetime.now().isoformat()
    log_entry = {"timestamp": timestamp, "message": message}
    with open(LOG_FILE, 'a') as logfile:
        logfile.write(json.dumps(log_entry) + '\n')

# Send sensor data to the CoAP server
async def send_data():
    context = await Context.create_client_context()
    data = generate_sensor_data()

    payload = json.dumps({"sensor_data": data}).encode('utf-8')

    global URI_PATH
    if not URI_PATH.startswith('/'):
        URI_PATH = '/' + URI_PATH

    request_uri = f"coap://{URI_IP}:{URI_PORT}{URI_PATH}"
    request = Message(code=Code.POST, payload=payload)
    request.set_request_uri(request_uri)

    try:
        response = await context.request(request).response
        print(f"Received response: {response.code}")
        save_sensor_data(data)
        log_message(f"Data sent successfully: {data}")
    except Exception as e:
        log_message(f"Error sending data: {e}")

# Main function to continuously send data
async def main():
    while True:
        await send_data()
        await asyncio.sleep(15)  # Wait 15 seconds before sending data again

if __name__ == "__main__":
    asyncio.run(main())