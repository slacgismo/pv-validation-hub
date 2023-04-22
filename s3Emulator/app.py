from flask import Flask, request
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define a simple S3-like API
@app.route("/<bucket_name>/<path:object_name>", methods=["PUT"])
def put_object(bucket_name, object_name):
    logger.info(f"PUT request received for bucket: {bucket_name}, object: {object_name}")

    # Get the content of the object from the request
    object_content = request.data

    # Create the local directory for the bucket if it doesn't exist
    bucket_dir = f"{bucket_name}/"
    if not os.path.exists(bucket_dir):
        os.makedirs(bucket_dir)

    # Store the object in the local file system
    with open(f"/{bucket_dir}/{object_name}", "wb") as f:
        f.write(object_content)

    return "", 204

@app.route("/<bucket_name>/<path:object_name>", methods=["GET"])
def get_object(bucket_name, object_name):
    logger.info(f"GET request received for bucket: {bucket_name}, object: {object_name}")

    # Retrieve the object from the local file system
    try:
        with open(f"/{bucket_name}/{object_name}", "rb") as f:
            object_content = f.read()
    except FileNotFoundError:
        return "Object not found", 404

    return object_content, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
