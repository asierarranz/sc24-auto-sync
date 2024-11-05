from flask import Flask, render_template, send_from_directory, jsonify
import os
import shutil
from datetime import datetime

app = Flask(__name__)

# Paths to main image folder and VideoWall folder
IMAGE_FOLDER = "/root/sc24_images"
VIDEOWALL_FOLDER = os.path.join(IMAGE_FOLDER, "videowall")

# Ensure VideoWall folder exists
os.makedirs(VIDEOWALL_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # List all images in the main image folder with VideoWall status
    images = []
    for filename in sorted(os.listdir(IMAGE_FOLDER), key=lambda x: os.path.getmtime(os.path.join(IMAGE_FOLDER, x)), reverse=True):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            # Check if the image is already in the VideoWall folder
            is_in_videowall = os.path.exists(os.path.join(VIDEOWALL_FOLDER, filename))
            images.append({
                'filename': filename,
                'modified_time': datetime.fromtimestamp(os.path.getmtime(os.path.join(IMAGE_FOLDER, filename))).strftime("Created: %H:%M:%S (%Y/%m/%d)"),
                'is_in_videowall': is_in_videowall
            })
    return render_template('index.html', images=images)

@app.route('/videowall')
def videowall():
    # Get list of images in VideoWall folder
    videowall_images = [
        f for f in os.listdir(VIDEOWALL_FOLDER)
        if f.endswith(('.png', '.jpg', '.jpeg'))
    ]
    return render_template('videowall.html', images=videowall_images)

@app.route('/send_to_videowall/<filename>', methods=['POST'])
def send_to_videowall(filename):
    src_path = os.path.join(IMAGE_FOLDER, filename)
    dest_path = os.path.join(VIDEOWALL_FOLDER, filename)
    if os.path.exists(dest_path):
        # If already in VideoWall, remove it (toggle off)
        os.remove(dest_path)
        message = f"Image '{filename}' removed from VideoWall."
    else:
        # If not in VideoWall, copy it (toggle on)
        shutil.copy(src_path, dest_path)
        message = f"Image '{filename}' sent to VideoWall."
    return jsonify({"message": message})

@app.route('/images/<filename>')
def serve_image(filename):
    # Serve images directly from the main image folder
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/videowall_images/<filename>')
def serve_videowall_image(filename):
    # Serve images directly from the VideoWall folder
    return send_from_directory(VIDEOWALL_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
