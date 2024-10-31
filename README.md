# SC24 Auto Sync and Photo Gallery

`sc24-auto-sync` is a suite of tools designed for SC24 to streamline the management of generative AI images. It includes automated file synchronization scripts and a web-based photo gallery for selecting images that will be displayed on a VideoWall. 

## Requirements

### General Requirements
- **Python 3.x**: Required for running scripts and the web application.
- **Server with SSH Access**: Acts as a central repository for images, accessible by the generation machine and VideoWall machine.

### Python Dependencies

#### For Serverless Sync
- **`paramiko`**: SSH and SFTP functionality for secure file transfers.
- **`watchdog`**: Monitors a local folder for new files, facilitating automated uploads of generated images (`sync_upload.py`).

#### For Photo Gallery Manager
- **`Flask`**: Hosts the `/photo_gallery` web gallery for easy image selection.
- **`shutil`**: Manages file copying for selected images, sending them to the `videowall` folder.

**Note:** The server setup for SC24 already includes SSH access, so additional configuration for server access is unnecessary.

## Components and Workflow

### 1. Image Generation and Upload

   - **ComfyUI**: Generates images on the image-generation machine.
   - **Automatic Upload**: `sync_upload.py` runs on the ComfyUI machine, monitors the output folder for new images, and uploads them to the server’s main image folder.

### 2. Photo Gallery for Image Selection

   - The `/photo_gallery` web app, hosted on the server, displays all images stored in the main image folder.
   - Each image has a “Send to VideoWall” button, allowing users to select images for display. This button copies the selected image to a designated `videowall` folder within the main directory, which any VideoWall display system can read to show selected images in a fancy format.

### 3. Syncing to the VideoWall

   - `sync_download.py` runs on the VideoWall machine and only downloads images from the `videowall` folder on the server.
   - This setup ensures only the selected images are synchronized to the VideoWall machine for display.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sc24_auto_sync.git
cd sc24_auto_sync
```

### 2. Install Dependencies

Use the `requirements.txt` file to install all necessary libraries:

```bash
pip install -r requirements.txt
```

### 3. Configuration

#### Sync Scripts Configuration

- **Uploads** are sent to the main image folder, while **downloads** only sync from the `videowall` folder.

- **`config_upload.txt`** (used by `sync_upload.py`):
  ```bash
  hostname=SERVER_IP
  username=YOUR_USERNAME
  password=YOUR_PASSWORD
  remote_folder=/root/sc24_images
  local_folder=C:/path/to/local/upload_folder/ComfyUI
  ```

- **`config_download.txt`** (used by `sync_download.py`):
  ```bash
  hostname=SERVER_IP
  username=YOUR_USERNAME
  password=YOUR_PASSWORD
  remote_folder=/root/sc24_images/videowall
  local_folder=C:/path/to/local/download_folder/for_videowall
  ```

#### Photo Gallery Configuration

The main image folder path is `/root/sc24_images`, with a subfolder `/root/sc24_images/videowall` to store approved images. Make sure this structure exists on the server before starting.

## Usage

### Running `sync_upload.py`

The `sync_upload.py` script runs on the ComfyUI generation machine and monitors the specified local folder for new images, automatically uploading them to the main image folder on the server.

```bash
python sync_upload.py
```

### Running `sync_download.py`

The `sync_download.py` script periodically checks the `videowall` folder on the server, downloading any new images to the VideoWall machine.

```bash
python sync_download.py
```

### Running the Photo Gallery App

The gallery is hosted on the server and accessible via the server’s IP address in a browser. To run it in the background (e.g., using `screen`):

1. Start a new `screen` session:

   ```bash
   screen -S photo_gallery
   ```

2. Run the Flask app:

   ```bash
   flask run --host=0.0.0.0 --port=8000
   ```

3. Detach from the screen session with `Ctrl + A, D`. The app will keep running in the background.

## Logging

Each script generates logs for monitoring sync activities:

- **`upload_log.txt`**: Logs file uploads from `sync_upload.py`.
- **`download_log.txt`**: Logs file downloads from `sync_download.py`.

## Troubleshooting

1. **Configuration Loading Errors**: Ensure configuration files are correctly formatted and placed in the script directories.
2. **File Path Issues**: Verify the paths in each configuration file. The script will attempt to create any specified `local_folder` that doesn’t already exist.
3. **Connection Errors**: Ensure the server IP, username, and password are accurate and SSH access is configured on the server.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

### Author
[Asier Arranz](https://github.com/asierarranz)

