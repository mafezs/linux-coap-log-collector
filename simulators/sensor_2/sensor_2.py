import asyncio
import json
import random
import os
import configparser
from aiocoap import *
from aiocoap.resource import Resource, Site
from aiocoap.numbers.codes import Code
from datetime import datetime

# Description:
# This script implements a CoAP listener for Sensor 2, which receives sensor data from other devices (like Sensor 1) 
# and simulates internal adjustments of temperature and humidity based on the received external data.
# The server responds to POST requests with the data and performs periodic adjustments to internal temperature 
# and humidity. It also logs all relevant events and errors to a specified log file in the configuration file.


# Load configuration from sensor_2.conf
config = configparser.ConfigParser()
config.read('sensor_2.conf')

# Define file path for configuration variables and log files
LOG_FILE = config['sensor']['LOG_FILE']
URI_IP = config['sensor']['URI_IP']
URI_PORT = int(config['sensor']['URI_PORT'])  # Convert port to integer
SENSOR_ID = config['sensor']['SENSOR_ID']
URI_PATH_PART1 = config['sensor']['URI_PATH_PART1']
URI_PATH_PART2 = config['sensor']['URI_PATH_PART2']

print("Configuration values:")
print(f"LOG_FILE: {LOG_FILE}")
print(f"URI_IP: {URI_IP}")
print(f"URI_PORT: {URI_PORT}")
print(f"SENSOR_ID: {SENSOR_ID}")
print(f"URI_PATH_PART1: {URI_PATH_PART1}")
print(f"URI_PATH_PART2: {URI_PATH_PART2}")

# Define constants for internal temperature and humidity
INTERNAL_TEMP_MIN = 20.0
INTERNAL_TEMP_MAX = 22.0
INTERNAL_HUMIDITY_MIN = 30.0
INTERNAL_HUMIDITY_MAX = 50.0
ADJUSTMENT_INTERVAL = 15  # Interval in seconds

# Ensure the directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Function to log messages
def log_message(message):
    timestamp = datetime.now().isoformat()
    log_entry = {"timestamp": timestamp, "sensor_id": SENSOR_ID, "message": message}
    with open(LOG_FILE, 'a') as logfile:
        logfile.write(json.dumps(log_entry) + '\n')

# Function to simulate internal temperature adjustment
def adjust_internal_temperature(external_temp, internal_temp):
    if external_temp > INTERNAL_TEMP_MAX:
        adjustment = random.uniform(-1.0, -0.5)  # Cool down
    elif external_temp < INTERNAL_TEMP_MIN:
        adjustment = random.uniform(0.5, 1.0)  # Heat up
    else:
        adjustment = random.uniform(-0.2, 0.2)  # Slight adjustment

    new_temp = internal_temp + adjustment
    new_temp = max(INTERNAL_TEMP_MIN, min(INTERNAL_TEMP_MAX, new_temp))
    return round(new_temp, 2)

# Function to simulate internal humidity adjustment
def adjust_internal_humidity(external_humidity, internal_humidity):
    if external_humidity > INTERNAL_HUMIDITY_MAX:
        adjustment = random.uniform(-2.0, -1.0)  # Decrease humidity
    elif external_humidity < INTERNAL_HUMIDITY_MIN:
        adjustment = random.uniform(1.0, 2.0)  # Increase humidity
    else:
        adjustment = random.uniform(-0.5, 0.5)  # Slight adjustment

    new_humidity = internal_humidity + adjustment
    new_humidity = max(INTERNAL_HUMIDITY_MIN, min(INTERNAL_HUMIDITY_MAX, new_humidity))
    return round(new_humidity, 2)

# CoAP resource to handle incoming POST requests
class SensorDataResource(Resource):
    def __init__(self):
        super().__init__()
        self.internal_temp = round(random.uniform(INTERNAL_TEMP_MIN, INTERNAL_TEMP_MAX), 2)
        self.internal_humidity = round(random.uniform(INTERNAL_HUMIDITY_MIN, INTERNAL_HUMIDITY_MAX), 2)
        self.external_temp = None
        self.external_humidity = None
        self.start_periodic_adjustment()

    async def render_post(self, request):
        try:
            payload = json.loads(request.payload.decode('utf-8'))
            sensor_data = payload['sensor_data']
            self.external_temp = sensor_data['temperature']
            self.external_humidity = sensor_data['humidity']

            log_message(f"Received sensor data: {sensor_data}")
            return Message(code=Code.VALID, payload=b"Sensor data processed")
        except Exception as e:
            log_message(f"Error processing sensor data: {e}")
            return Message(code=Code.BAD_REQUEST, payload=b"Invalid sensor data")

    def start_periodic_adjustment(self):
        asyncio.create_task(self.periodic_adjustment())

    async def periodic_adjustment(self):
        while True:
            if self.external_temp is not None and self.external_humidity is not None:
                try:
                    new_internal_temp = adjust_internal_temperature(self.external_temp, self.internal_temp)
                    new_internal_humidity = adjust_internal_humidity(self.external_humidity, self.internal_humidity)

                    log_message(f"Adjusting temperature to {new_internal_temp}")
                    log_message(f"Adjusting humidity to {new_internal_humidity}")

                    self.internal_temp = new_internal_temp
                    self.internal_humidity = new_internal_humidity
                except Exception as e:
                    log_message(f"Error during adjustment: {e}")

            await asyncio.sleep(ADJUSTMENT_INTERVAL)

# Function to start the CoAP server
async def main():
    root = Site()
    root.add_resource([URI_PATH_PART1, URI_PATH_PART2], SensorDataResource())
    await Context.create_server_context(root, bind=(URI_IP, URI_PORT))

    print(f"CoAP server running on {URI_IP}:{URI_PORT}")
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
