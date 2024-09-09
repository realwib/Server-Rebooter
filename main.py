import os
import requests
import json
import subprocess
from datetime import datetime
import time
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

# API key and base URL
API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.vultr.com/v2'

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# Define phone numbers for WhatsApp notifications
TO_PHONE_NUMBERS = [
    'whatsapp:+910000000000',
]

# Headers for authentication
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json',
}

# Function to send WhatsApp message (using Twilio API)
def send_whatsapp_message(to_number, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )
    print(f"Sent WhatsApp message to {to_number}:\n{message.sid}")

# Helper function to get all instances
def get_all_instances():
    url = f'{BASE_URL}/instances'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        instances = response.json().get('instances', [])
        return instances
    else:
        print(f'Failed to retrieve instance list: {response.status_code} - {response.text}')
        return []

# Function to restart the server using instance ID
def restart_server(instance_id):
    url = f"{BASE_URL}/instances/{instance_id}/reboot"
    response = requests.post(url, headers=headers)
    if response.status_code == 204:
        print(f"Server {instance_id} is restarting.")
    else:
        print(f"Failed to restart server {instance_id}: {response.status_code} - {response.text}")

# Function to check server status using instance ID
def check_server_status(instance_id):
    try:
        command = [
            "curl",
            "-H", f"Authorization: Bearer {API_KEY}",
            "-H", "Content-Type: application/json",
            f"https://api.vultr.com/v2/instances/{instance_id}"
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        response = json.loads(result.stdout)
        status = response.get('instance', {}).get('status', 'Unknown')
        return status
    except subprocess.CalledProcessError as e:
        print(f"Error checking server status: {e}")
        return 'Failed'
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return 'Failed'

# Function to format output for terminal
def format_terminal_output(batch_name, server_statuses):
    output = f"--{batch_name}--\n\n"
    for status in server_statuses:
        output += f"{batch_name} - {status['timestamp']}\n"
        output += f"Restarting server: `{status['server']}`\n"
        output += f"Status: {status['status']}\n\n"
    output += f"End of {batch_name}.\n"
    return output

# Function to format output for log file
def format_log_output(batch_name, server_statuses):
    log_content = f"--{batch_name}--\n\n"
    for status in server_statuses:
        log_content += f"{status['timestamp']}: Restarting `{status['server']}`\n"
        log_content += f"Status: {status['status']}\n\n"
    log_content += f"End of {batch_name}.\n"
    return log_content

# Function to format output for WhatsApp
def format_whatsapp_output(batch_name, server_statuses):
    whatsapp_message = f"{batch_name} 🕒\n\n"
    for status in server_statuses:
        status_emoji = {
            'active': '✅',
            'Restart Completed & Active': '✅',
            'Status Not Active': '⚠️',
            'Failed': '❌'
        }.get(status['status'], '❓')
        whatsapp_message += f"{status['timestamp']}: Restarting `{status['server']}`\n"
        whatsapp_message += f"{status_emoji} *{status['status']}*\n\n"
    whatsapp_message += f"End of {batch_name}.\n"
    return whatsapp_message

# Function to process a batch
def process_batch(batch_name):
    try:
        with open(f'{batch_name}.json') as f:
            servers_to_restart = json.load(f)
    except Exception as e:
        print(f"Error loading {batch_name}: {e}")
        return

    instances = get_all_instances()
    instance_map = {instance['label']: instance['id'] for instance in instances}

    server_statuses = []

    for server in servers_to_restart:
        instance_id = instance_map.get(server)
        if instance_id:
            print(f"Restarting server: {server} ({instance_id})")
            restart_server(instance_id)  # Restart the server

            # Initial delay of 1 minute after issuing restart
            time.sleep(60)

            # Check status after the delay
            status = check_server_status(instance_id)
            if status in ['suspended', 'shutting_down', 'pending', 'stopped', 'failed']:
                print(f"Status after 1st check: {status}. Checking again in 2 minutes...")
                time.sleep(120)  # Wait 2 more minutes before the second check
                status = check_server_status(instance_id)

            # Log the final status
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            server_statuses.append({'timestamp': timestamp, 'server': server, 'status': status})
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            server_statuses.append({'timestamp': timestamp, 'server': server, 'status': 'Instance ID not found'})

    # Format outputs
    terminal_output = format_terminal_output(batch_name, server_statuses)
    log_output = format_log_output(batch_name, server_statuses)
    whatsapp_output = format_whatsapp_output(batch_name, server_statuses)

    # Print to terminal
    print(terminal_output)

    # Save to log file
    with open(f"logs/{batch_name}_log.txt", "w") as log_file:
        log_file.write(log_output)

    # Send WhatsApp message
    for number in TO_PHONE_NUMBERS:
        send_whatsapp_message(number, whatsapp_output)

# Main function
def main():
    batch_names = ['batch1','batch2']  # List batch files as needed

    for batch_name in batch_names:
        print(f"Processing {batch_name}...")
        process_batch(batch_name)

if __name__ == "__main__":
    main()
