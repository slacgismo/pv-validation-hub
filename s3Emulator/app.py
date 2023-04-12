from flask import Flask, request
from boto3.session import Session

app = Flask(__name__)

# Define a simple S3-like API
@app.route("/<bucket_name>/<object_name>", methods=["PUT"])
def put_object(bucket_name, object_name):
    # Get the content of the object from the request
    object_content = request.data

    # Store the object in a local file system
    with open(f"{bucket_name}/{object_name}", "wb") as f:
        f.write(object_content)

    return "", 204

@app.route("/<bucket_name>/<object_name>", methods=["GET"])
def get_object(bucket_name, object_name):
    # Retrieve the object from the local file system
    try:
        with open(f"{bucket_name}/{object_name}", "rb") as f:
            object_content = f.read()
    except FileNotFoundError:
        return "Object not found", 404

    return object_content, 200

if __name__ == "__main__":
    app.run()