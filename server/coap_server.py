import asyncio
import subprocess
import configparser
from aiocoap import *
from aiocoap.numbers.codes import Code
from aiocoap.resource import Resource, Site
from datetime import datetime, timedelta
import base64
import uuid
import hashlib

# CoAP Server Implementation
#
# This CoAP server handles authentication and data logging for IoT devices. 
# It supports the following functionalities:
# 1. Authentication: Validates users based on hashed credentials and issues tokens.
# 2. Data Logging: Receives POST requests, logs data, and manages token-based access.
#
# Configuration and credentials are managed via external files:
# - coap_server.conf: Configuration settings for the server.
# - credentials.txt: Contains hashed credentials for user authentication.
#
# Dependencies:
# - aiocoap
# - configparser

# Load configuration from coap_server.conf
config = configparser.ConfigParser()
config.read('coap_server.conf')

# Define configuration variables
SERVER_IP = config['coap']['SERVER_IP']
SERVER_PORT = int(config['coap']['SERVER_PORT'])
URI_PATH_PART1 = config['coap']['URI_PATH_PART1']
URI_PATH_PART2 = config['coap']['URI_PATH_PART2']
TOKEN_EXPIRY_SECONDS = 3600  # Token validity period

# Load hashed credentials from credentials.txt
def load_credentials():
    # Load user credentials from a file
    credentials = {}
    with open('credentials.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Ignore empty lines and comments
                parts = line.split(':')
                if len(parts) == 2:
                    username, hashed_password = parts
                    credentials[username] = hashed_password
                else:
                    print(f"Warning: Ignoring invalid credential line: {line}")
    return credentials

credentials = load_credentials()

# Token storage
tokens = {}

# Get MAC address from IP
def get_mac(ip):
    # Retrieve MAC address using ARP
    try:
        ipv4_part = ip.split(":")[-1]
        pid = subprocess.Popen(["arp", "-n", ipv4_part], stdout=subprocess.PIPE)
        s = pid.communicate()[0].decode('utf-8')
        lines = s.split('\n')

        for line in lines:
            if ipv4_part in line:
                parts = line.split()
                mac = parts[2] if len(parts) > 2 else None
                return mac if mac != "(incomplete)" else None
        return None
    except Exception as e:
        print(f"Error getting MAC address for IP {ip}: {e}")
        return None

# Hash password
def hash_password(password):
    # Hash password using SHA-256
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Validate credentials
def validate_credentials(auth_header):
    # Validate user credentials from authorization header
    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(":")
        hashed_password = hash_password(password)
        if username in credentials and credentials[username] == hashed_password:
            return username
        else:
            return None
    except Exception as e:
        print(f"Error validating credentials: {e}")
        return None

# Generate token
def generate_token(username):
    # Generate a new token for the user
    token = str(uuid.uuid4())
    tokens[token] = (username, datetime.now() + timedelta(seconds=TOKEN_EXPIRY_SECONDS))
    return token

# Validate token
def validate_token(token):
    # Check if the token is valid and not expired
    if token in tokens:
        username, expiry = tokens[token]
        if datetime.now() < expiry:
            return username
        else:
            del tokens[token]
            return None
    else:
        return None

class AuthResource(Resource):
    # Resource for handling authentication requests
    async def render_post(self, request):
        # Process POST request for authentication
        try:
            auth_header = None
            for option in request.opt.uri_query:
                if option.startswith("Authorization="):
                    auth_header = option.split("=", 1)[1]
                    break

            username = validate_credentials(auth_header)
            if username:
                token = generate_token(username)
                return Message(code=Code.CONTENT, payload=token.encode('utf-8'))
            else:
                return Message(code=Code.UNAUTHORIZED, payload=b"Unauthorized")
        except Exception as e:
            print(f"Error processing authentication request: {e}")
            return Message(code=Code.INTERNAL_SERVER_ERROR)

class PostResource(Resource):
    # Resource for handling data submission requests
    async def render_post(self, request):
        # Process POST request for data submission
        try:
            token = None
            auth_header = None
            for option in request.opt.uri_query:
                if option.startswith("Token="):
                    token = option.split("=", 1)[1]
                elif option.startswith("Authorization="):
                    auth_header = option.split("=", 1)[1]

            if token and validate_token(token):
                username = validate_token(token)
            elif auth_header:
                username = validate_credentials(auth_header)
                if username:
                    token = generate_token(username)
                else:
                    return Message(code=Code.UNAUTHORIZED, payload=b"Unauthorized")
            else:
                return Message(code=Code.UNAUTHORIZED, payload=b"Unauthorized")
            
            payload = request.payload.decode('utf-8')
            client_ip = request.remote.sockaddr[0]
            client_ip = client_ip.split(":")[-1] if "::" in client_ip else client_ip
            client_mac = get_mac(client_ip)

            print(f"Received POST request: {payload}")
            log_entry = f"Reception date: {datetime.now().isoformat()}\nClient IP: {client_ip}\nClient MAC: {client_mac}\nPayload:\n{payload}\n"

            with open('coap_logging.txt', 'a') as logfile:
                logfile.write(log_entry)
                logfile.write("\n---\n")

            response_payload = f"Token={token}".encode('utf-8')
            return Message(code=Code.CREATED, payload=response_payload)
        except Exception as e:
            print(f"Error processing POST request: {e}")
            return Message(code=Code.INTERNAL_SERVER_ERROR)

async def main():
    # Start the CoAP server
    root = Site()
    root.add_resource(('auth',), AuthResource())
    root.add_resource((URI_PATH_PART1, URI_PATH_PART2), PostResource())

    try:
        context = await Context.create_server_context(root, bind=(SERVER_IP, SERVER_PORT))
        print(f"CoAP server started at {SERVER_IP}:{SERVER_PORT}")
        await asyncio.Future()
    except OSError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
