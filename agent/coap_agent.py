import asyncio
import shutil
import os
import configparser
import psutil
import logging
from aiocoap import *
from aiocoap.numbers.codes import Code
from datetime import datetime, timedelta
import base64

# CoAP Agent for IoT Data Logging
#
# This CoAP agent handles the following tasks:
# 1. Authentication: Obtains and renews tokens for secure communication with the CoAP server.
# 2. System Monitoring: Collects system memory and disk usage.
# 3. Log Management: Reads, backs up, and clears log files.
# 4. Data Transmission: Sends collected data and logs to the CoAP server at regular intervals.
#
# Configuration and credentials are managed via external files:
# - agente.conf: Configuration settings for the agent.
# - coap_agent.log: Log file for the agent's operations.
#
# Dependencies:
# - aiocoap
# - configparser
# - psutil

# Configure logging
LOG_FILE = 'agent.log'
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Load configuration from coap_agent.conf
config = configparser.ConfigParser()
config.read('coap_agent.conf')

# Define file paths and other configuration variables
LOG_FILES = [file.strip() for file in config['paths']['LOG_FILES'].split(',')]
LOG_FILES.append(LOG_FILE)  # Include the agent.log file

COAP_URI_IP = config['coap']['URI_IP']
COAP_URI_PORT = int(config['coap']['URI_PORT'])
COAP_URI_PATH_PART1 = config['coap']['URI_PATH_PART1']
COAP_URI_PATH_PART2 = config['coap']['URI_PATH_PART2']

# Token and credentials
TOKEN = None
TOKEN_EXPIRY = datetime.now()
USERNAME = config['auth']['USERNAME']
PASSWORD = config['auth']['PASSWORD']

# Function to get a token from the server
async def obtain_token(context):
    """Obtain a token from the CoAP server for authentication."""
    global TOKEN, TOKEN_EXPIRY
    auth_header = f"Basic {base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()}"
    request = Message(code=Code.POST, uri=f'coap://{COAP_URI_IP}:{COAP_URI_PORT}/auth', payload=b'')
    request.opt.uri_query = [f'Authorization={auth_header}']
    try:
        response = await context.request(request).response
        TOKEN = response.payload.decode('utf-8')
        TOKEN_EXPIRY = datetime.now() + timedelta(seconds=3600)  # Token expiry time
        logging.debug(f"Obtained new token: {TOKEN}")
    except Exception as e:
        logging.error(f"Failed to obtain token: {e}")

# Function to read the entire content of a log file
def read_log_file(log_file):
    """Read the content of a specified log file."""
    try:
        with open(log_file, 'r') as logfile:
            return logfile.read()
    except Exception as e:
        logging.error(f"Error reading log: {e}")
        return f"Error reading log: {e}"

# Function to get system memory usage
def get_memory_usage():
    """Get the current memory usage of the system."""
    try:
        virtual_memory = psutil.virtual_memory()
        used_memory = (virtual_memory.total - virtual_memory.available) / virtual_memory.total * 100
        return f"Memory Usage: {used_memory:.2f}%"
    except Exception as e:
        logging.error(f"Error getting memory usage: {e}")
        return f"Error getting memory usage: {e}"

# Function to get disk usage
def get_disk_usage():
    """Get the current disk usage of the system."""
    try:
        disk_usage = os.popen('df /').read().splitlines()[1].split()
        total = int(disk_usage[1])
        used = int(disk_usage[2])
        used_disk = (used / total) * 100
        return f"Disk Usage: {used_disk:.2f}%"
    except Exception as e:
        logging.error(f"Error getting disk usage: {e}")
        return f"Error getting disk usage: {e}"

# Function to backup and clear log files
def backup_and_clear_logs():
    """Backup and clear specified log files."""
    for log_file in LOG_FILES:
        if os.path.exists(log_file):
            backup_file = log_file + '.bak'
            shutil.copy(log_file, backup_file)
            with open(log_file, 'w') as logfile:
                logfile.write('')
            logging.debug(f"Backed up and cleared log file: {log_file}")
        else:
            logging.warning(f"Log file not found: {log_file}")

# Function to send a CoAP request with the log content
async def send_request(context, log_content):
    """Send a CoAP request containing the log content to the server."""
    global TOKEN, TOKEN_EXPIRY

    # Check if the token is expired
    if TOKEN is None or datetime.now() >= TOKEN_EXPIRY:
        await obtain_token(context)

    # Build the payload as a plain text string
    payload = (
        f"Timestamp: {datetime.now().isoformat()}\n"
        f"{get_memory_usage()}\n"
        f"{get_disk_usage()}\n"
        f"Logs:\n{log_content}"
    ).encode('utf-8')

    request = Message(code=Code.POST, payload=payload)
    request_uri = f"coap://{COAP_URI_IP}:{COAP_URI_PORT}/{COAP_URI_PATH_PART1}/{COAP_URI_PATH_PART2}"
    request.set_request_uri(request_uri)
    request.opt.uri_query = [f'Token={TOKEN}']

    logging.debug(f"Sending request to: {request_uri}")
    try:
        await context.request(request).response
        logging.debug("Request sent successfully")
    except Exception as e:
        logging.error(f"Failed to send request: {e}")

# Main function
async def main():
    """Main function to run the CoAP agent."""
    global TOKEN, TOKEN_EXPIRY
    context = await Context.create_client_context()
    
    # Obtain initial token
    await obtain_token(context)

    while True:
        log_contents = []
        for log_file in LOG_FILES:
            log_contents.append(read_log_file(log_file))

        # Concatenate all log contents into a single string
        all_logs = "".join(log_contents)

        # Send the content via CoAP
        await send_request(context, all_logs)

        # Backup and clear the log files
        backup_and_clear_logs()

        # Wait for 15 seconds before the next iteration
        await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())