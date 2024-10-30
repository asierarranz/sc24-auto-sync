import paramiko
import os
import time
import logging

# Set up logging
logging.basicConfig(
    filename="download_log.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the config file in the same directory as the script
config_path = os.path.join(script_dir, "config_download.txt")

# Function to load configuration from config_download.txt
def load_config(config_path=config_path):
    config = {}
    try:
        with open(config_path, 'r') as f:
            for line in f:
                key, value = line.strip().split('=')
                config[key] = value
        logging.info("Configuration loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        print(f"Error loading configuration: {e}")
        exit(1)  # Exit if configuration loading fails
    return config

# Load the configuration
config = load_config()

hostname = config['hostname']
username = config['username']
password = config['password']
remote_folder = config['remote_folder'].replace("\\", "/")  # Ensure forward slashes for remote path
local_folder = os.path.normpath(config['local_folder'])  # Normalize local path for Windows

# Ensure local folder exists
if not os.path.exists(local_folder):
    os.makedirs(local_folder)
    logging.info(f"Created local folder: {local_folder}")
    print(f"Created local folder: {local_folder}")

# Initialize a set to track downloaded files
downloaded_files = set(os.listdir(local_folder))

# Function to download files from the server
def download_photos():
    try:
        # Connect to the Linux server using SSH and SFTP
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        logging.info(f"Connected to server {hostname}")

        sftp = ssh.open_sftp()
        # List files in the remote folder
        for file_name in sftp.listdir(remote_folder):
            remote_path = f"{remote_folder}/{file_name}".replace("\\", "/")
            local_path = os.path.join(local_folder, file_name)

            # Download if the file is not already in the set of downloaded files
            if file_name not in downloaded_files:
                print(f"Downloading {file_name}...")
                sftp.get(remote_path, local_path)
                print(f"Downloaded: {file_name}")
                logging.info(f"Downloaded {file_name}")

                # Add the file to the set after downloading
                downloaded_files.add(file_name)
            else:
                print(f"Skipping {file_name}, already exists locally.")
                logging.info(f"Skipped {file_name}, already exists locally.")

        sftp.close()
        ssh.close()
    except Exception as e:
        logging.error(f"Error in download process: {e}")
        print(f"Error in download process: {e}")

# Periodically check for new files and download them as necessary
def sync_periodically(interval=10):
    try:
        while True:
            print("Checking for new files to download...")
            download_photos()
            print(f"Waiting {interval} seconds before the next check.")
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Download sync stopped by user.")
        print("Download sync stopped.")

# Start the periodic sync
sync_periodically()
