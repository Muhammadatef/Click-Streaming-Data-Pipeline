import os
import logging as log
import argparse
import random
import requests
import json
import time
from uuid import uuid4

# State management functions
def reset_state(state_file):
    """ Reset the state by clearing the state file content. """
    open(state_file, 'w').close()

def save_state(state_file, last_read_line):
    """ Save the current state to a file. """
    with open(state_file, 'w') as file:
        file.write(str(last_read_line))

def load_state(state_file):
    """ Load the last read state from a file. """
    if os.path.exists(state_file):
        with open(state_file, 'r') as file:
            return int(file.read().strip() or 0)
    return 0

# Setup function
def setup():
    """ Setup necessary parameters """
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", type=str, help="Provide a hostname ", nargs='?', default='http://localhost:60000')
    parser.add_argument("filename", type=str, help="Provide a data filename ", nargs='?', default='../data/events.json')
    parser.add_argument("--reset", action='store_true', help="Reset the reading state to start from the beginning")
    args = parser.parse_args()
    
    # Logging Configuration
    log.basicConfig(level=log.INFO, format='%(asctime)s [%(levelname)s] [%(name)8s] %(message)s')
    
    # Check if reset flag is set
    state_file = 'read_state.txt'
    if args.reset:
        reset_state(state_file)
    
    return args, state_file

# Function to send events
def send_events(hostname, events):
    """ Send events to a REST API """
    try:
        response = requests.post(f'{hostname}/collect', json=events)
        response.raise_for_status()
        if response.status_code != 200:
            log.error("Failed to send event: %s", events)
    except Exception as e:
        log.error(e)

# Function to generate and send random JSON objects
def generate_random_json_objects(hostname, filename, state_file):
    last_read_line = load_state(state_file)
    with open(filename, mode="r", encoding="utf8") as file_obj:
        lines = file_obj.readlines()
        rnd = 987
        count = 0
        data = []
        package_id = str(uuid4())  # Generate unique package identifier
        
        for index, line in enumerate(lines[last_read_line:], start=last_read_line):
            try:
                json_object = json.loads(line)
                json_object['package_id'] = package_id
                data.append(json_object)
                count += 1
                
                if count == rnd:
                    send_events(hostname, data)
                    data = []
                    count = 0
                    rnd = 987
                    package_id = str(uuid4())  # New package identifier
                    time.sleep(1)  # Delay
                    
                    save_state(state_file, index + 1) # Save the current index to the state file
                    time.sleep(5)

            except json.JSONDecodeError as e:
                log.error(f"Error parsing JSON: {e}")
            except Exception as e:
                log.error(f"Unexpected error: {e}")

# Main execution
if __name__ == "__main__":
    args, state_file = setup()
    generate_random_json_objects(args.hostname, args.filename, state_file)
