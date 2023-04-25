from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import sys

app = Flask(__name__)

CORS(app) 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a simple S3-like API
@app.route("/put_object/<bucket_name>/<path:object_name>", methods=["PUT"])
def put_object(bucket_name, object_name):
    logger.info(f"PUT request received for bucket: {bucket_name}, object: {object_name}")

    # Get the content of the object from the request
    object_content = request.data

    # Create the local directory for the bucket if it doesn't exist
    full_path = os.path.join('/', bucket_name, object_name)
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path))

    # Store the object in the local file system
    with open(full_path, "wb") as f:
        f.write(object_content)

    return "", 204


@app.route("/get_object/<bucket_name>/<path:object_name>", methods=["GET"])
def get_object(bucket_name, object_name):
    logger.info(f"GET request received for bucket: {bucket_name}, object: {object_name}")

    # Check if the requested path is a directory
    if os.path.isdir(f"/{bucket_name}/{object_name}"):
        return "Requested path is a directory, not a file", 400

    # Retrieve the object from the local file system
    try:
        print(f"file path to get: {os.path.join('/', bucket_name, object_name)}", file=sys.stderr)
        with open(os.path.join('/', bucket_name, object_name), "rb") as f:
            object_content = f.read()
    except FileNotFoundError:
        return "Object not found", 404

    return object_content, 200


<<<<<<< HEAD
@app.route("/<bucket_name>/<path:directory_path>/list", methods=["GET"])
def list_directory(bucket_name, directory_path):
    logger.info(f"GET request received for directory: {bucket_name}/{directory_path}")

    # List the directory content from the local file system
    try:
        directory_content = os.listdir(f"/{bucket_name}/{directory_path}")
    except FileNotFoundError:
        return "Directory not found", 404

    return jsonify(directory_content)
=======
@app.route("/list_bucket/<bucket_name>/<path:prefix>", methods=["GET"])
def get_bucket(bucket_name, prefix):
    # Retrieve the object from the local file system
    print(f"enter get_bucket()", file=sys.stderr)
    if not (os.path.exists(os.path.join('/', bucket_name)) and os.path.isdir(os.path.join('/', bucket_name))):
        return "Bucket not found", 404
    print(f"bucket {bucket_name} exists", file=sys.stderr)
    ret = {
        'Contents': []
    }

    for dir_path, dir_names, file_names in os.walk(os.path.join('/', bucket_name, prefix)):
        if dir_path == os.path.join('/', bucket_name, prefix):
            print(f"dir_path: {dir_path}\nfile_names: {file_names}", file=sys.stderr)
            for file_name in file_names:
                full_file_name = os.path.join(dir_path, file_name)
                key = '/'.join(full_file_name.split('/')[2:])
                ret['Contents'].append({'Key' : key})
    print(f"ret: {ret}", file=sys.stderr)
    return ret, 200

>>>>>>> 8b98f6160568108635a6d106a57b06a79b234976

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
