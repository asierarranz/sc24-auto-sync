import paramiko
import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
logging.basicConfig(
    filename="upload_log.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the config file in the same directory as the script
config_path = os.path.join(script_dir, "config_upload.txt")

# Function to load configuration from config_upload.txt
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
remote_folder = config['remote_folder'].replace("\\", "/")  # Ensure forward slashes
local_folder = config['local_folder']

# Class to handle file uploads when new files are detected
class UploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        
        # Log and print file detection
        logging.info(f"Detected new file: {file_name}")
        print(f"Detected new file: {file_name}")

        try:
            # Connect to the Linux server using SSH and SFTP
            print("Connecting to server...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=username, password=password)
            logging.info(f"Connected to server {hostname}")

            # Upload the file using SFTP
            sftp = ssh.open_sftp()
            # Construct the remote path with forward slashes only
            remote_path = f"{remote_folder}/{file_name}".replace("\\", "/")
            
            # Start uploading and log progress
            print(f"Uploading {file_name} to {remote_folder}...")
            sftp.put(file_path, remote_path, callback=self.upload_progress(file_name))
            
            print(f"Upload complete: {file_name}")
            logging.info(f"Upload complete for {file_name}")
            sftp.close()
            ssh.close()
        except Exception as e:
            logging.error(f"Error uploading {file_name}: {e}")
            print(f"Error uploading {file_name}: {e}")

    # Callback function to show upload progress
    def upload_progress(self, file_name):
        def inner_progress(transferred, total):
            percent = (transferred / total) * 100
            print(f"Uploading {file_name}: {percent:.2f}% complete", end='\r')
        return inner_progress

# Function to monitor the photo folder
def monitor_folder():
    event_handler = UploadHandler()
    observer = Observer()
    observer.schedule(event_handler, local_folder, recursive=False)
    observer.start()
    try:
        logging.info("Started monitoring folder for new files.")
        print("Monitoring folder for new files. Press CTRL+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopped monitoring folder.")
        print("Stopped monitoring folder.")
    observer.join()

# Start monitoring the folder
monitor_folder()
