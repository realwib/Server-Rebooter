# Server Restarter & Monitor

## Overview

The **Server Restart Monitor** is a Python script designed to automate the process of restarting servers using the Vultr API. After issuing a restart command, the script monitors the server status and provides real-time updates through WhatsApp notifications using the Twilio API.

This tool is useful for system administrators and DevOps engineers who need to automate server management tasks and stay informed about server statuses without manual intervention.

## Features

- **Automated Server Restarts:** Restart servers listed in batch files.
- **Status Monitoring:** Check the server status after restart and retry if needed.
- **Real-time Notifications:** Send status updates via WhatsApp using Twilio.
- **Logging:** Save detailed logs of operations for auditing and troubleshooting.

## Requirements

1. **Python 3.7 or higher**
2. **Vultr API Key:** For interacting with the Vultr API.
3. **Twilio Account:** For sending WhatsApp notifications.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/realwib/Server-Restarter.git
cd Server-Restarter
```

### 2. Install Dependencies

Install the required Python packages using `pip`. Ensure you are in the project directory.

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Configure a `.env` file in the root directory of the project with the following content:

```plaintext
API_KEY=your_vultr_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

Replace the placeholder values with your actual API keys and Twilio credentials.

### 4. Create Batch Files

Create JSON files (e.g., `batch1.json`) in the root directory with the list of server labels you want to restart. Here’s an example format for the batch file:

**`batch1.json`**
```json
[
    "server1_label",
    "server2_label",
    "server3_label"
]
```

Replace `"server1_label"`, `"server2_label"`, etc., with the actual labels of your servers.

### 5. Running the Script

Execute the script by running the following command:

```bash
python3 main.py
```

The script will process each batch file listed in the `batch_names` list, restart the servers, check their status, log the results, and send notifications.

## How It Works

1. **Load Environment Variables:** The script reads API keys and credentials from the `.env` file using the `python-dotenv` library.
2. **Retrieve Instances:** It fetches a list of instances from the Vultr API.
3. **Restart Servers:** For each server in the batch file, it sends a restart command to Vultr.
4. **Monitor Status:** It waits for 1 minute and checks the server status. If the status is not 'active', it checks again after an additional 2 minutes.
5. **Send Notifications:** The script sends WhatsApp notifications with the status of each server using the Twilio API.
6. **Log Results:** The results are logged to a file for review.

## Automating the Script with Cron

To automate the script execution at regular intervals, you can use `cron` on Unix-based systems. Here’s how to set up a cron job:

### 1. Open the Crontab Editor

Run the following command to edit the crontab file:

```bash
crontab -e
```

### 2. Add a Cron Job

Add a line to schedule the script. For example, to run the script daily at 2:00 AM, add:

```bash
0 2 * * * /usr/bin/python3 /path/to/your/project/main.py
```

Replace `/path/to/your/project/main.py` with the actual path to your script.

### 3. Save and Exit

Save the file and exit the editor. The cron job will now run the script at the specified time.

## Example Output

After running the script, you can expect output in the terminal, log files, and WhatsApp messages similar to the following:

**Terminal Output:**
```
Processing batch1...
Restarting server: server1_label (instance_id)
Server server1_label is restarting.
Status after 1st check: active. Restart completed & Active
```

**Log File:**
```
--batch1--

2024-09-09 10:00:00: Restarting `server1_label`
Status: Restart Completed & Active

End of batch1.
```

**WhatsApp Message:**
```
batch1 🕒

2024-09-09 10:00:00: Restarting `server1_label`
✅ *Restart Completed & Active*

End of batch1.
```

## Troubleshooting

- **Check API Key and Twilio Credentials:** Ensure they are correct in the `.env` file.
- **Verify Batch File Format:** Ensure JSON files are correctly formatted.
- **Review Logs:** Check log files in the `logs/` directory for detailed error messages.
