from flask import Flask, request
import os
import sys

app = Flask(__name__)

# Define a simple S3-like API
@app.route("/<bucket_name>/<path:object_name>", methods=["PUT"])
def put_object(bucket_name, object_name):
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

@app.route("/<bucket_name>/<path:object_name>", methods=["GET"])
def get_object(bucket_name, object_name):
    # Retrieve the object from the local file system
    try:
        print(f"file path to get: {os.path.join('/', bucket_name, object_name)}", file=sys.stderr)
        with open(os.path.join('/', bucket_name, object_name), "rb") as f:
            object_content = f.read()
    except FileNotFoundError:
        return "Object not found", 404

    return object_content, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
