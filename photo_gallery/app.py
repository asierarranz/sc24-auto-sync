from flask import Flask, render_template, send_from_directory, jsonify
import os
import shutil
from datetime import datetime

app = Flask(__name__)

# Paths to the image folders
IMAGE_FOLDER = "/root/sc24_images"
videowall_folder = os.path.join(IMAGE_FOLDER, "videowall")  # Using lowercase

# Ensure videowall folder exists
os.makedirs(videowall_folder, exist_ok=True)

@app.route('/')
def index():
    # Get list of images with status based on presence in videowall folder
    images = [
        {
            'filename': f,
            'modified_time': datetime.fromtimestamp(os.path.getmtime(os.path.join(IMAGE_FOLDER, f))).strftime("Created: %H:%M:%S (%Y/%m/%d)"),
            'in_videowall': os.path.exists(os.path.join(videowall_folder, f))  # Check if file exists in videowall
        }
        for f in sorted(
            [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))],
            key=lambda x: os.path.getmtime(os.path.join(IMAGE_FOLDER, x)),
            reverse=True
        )
    ]
    return render_template('index.html', images=images)

@app.route('/send_to_videowall/<filename>', methods=['POST'])
def send_to_videowall(filename):
    src_path = os.path.join(IMAGE_FOLDER, filename)
    dest_path = os.path.join(videowall_folder, filename)
    
    try:
        if os.path.exists(dest_path):
            # If the image is already in videowall, remove it
            os.remove(dest_path)
            message = f"Image '{filename}' removed from videowall."
        else:
            # If the image is not in videowall, copy it there
            shutil.copy(src_path, dest_path)
            message = f"Image '{filename}' sent to videowall successfully!"
        
        return jsonify({"message": message, "in_videowall": os.path.exists(dest_path)})
    except Exception as e:
        return jsonify({"message": f"Failed to toggle image in videowall: {str(e)}"}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    # Serve images directly from the image folder
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
