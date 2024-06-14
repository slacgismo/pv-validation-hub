import os
from sys import stdout
from typing import Any, cast
import docker.models
import docker.models.containers
from prefect import flow, task
from prefect_dask.task_runners import DaskTaskRunner
import docker
from docker.models.images import Image
from docker.models.containers import Container
from docker.errors import ImageNotFound


def docker_task(
    client: docker.DockerClient,
    image: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: list[Any] | None = None,
):

    if submission_args is None:
        submission_args = []

    # Define volumes to mount
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    data_dir = os.path.join(os.path.dirname(__file__), "data")

    volumes = {
        results_dir: {"bind": "/app/results/", "mode": "rw"},
        data_dir: {"bind": "/app/data/", "mode": "ro"},
    }

    # Execute docker image in a container
    container = None
    try:
        print("Docker container starting...")
        print(f"Image: {image}")
        print(f"Submission file name: {submission_file_name}")
        print(f"Submission function name: {submission_function_name}")
        print(f"Submission args: {submission_args}")
        container = cast(
            Container,
            client.containers.run(
                image,
                command=[
                    "python",
                    "submission_wrapper.py",
                    submission_file_name,
                    submission_function_name,
                    *submission_args,
                ],
                volumes=volumes,
                detach=True,
                stdout=True,
                stderr=True,
                mem_limit=f"{memory_limit}g",
            ),
        )

        print("Docker container started")
        print(container.id)

        # Wait for container to finish
        for line in container.logs(stream=True):
            line = cast(str, line)
            print(line.strip())

        container.wait()

    except Exception as e:
        print(f"Error: {e}")
        raise e
    finally:
        if container:
            if container.status == "running":
                print("Docker container stopping...")
                container.stop()
                print("Docker container stopped")
            print("Docker container removing...")
            container.remove()
            print("Docker container removed")


def initialize_docker_client():
    client = docker.from_env()
    return client


def create_docker_image(
    tag: str,
    client: docker.DockerClient,
    overwrite: bool = False,
):

    file_path = os.path.join(os.path.dirname(__file__), "environment")

    print(file_path)

    # Check if Dockerfile exists
    if not os.path.exists(os.path.join(file_path, "Dockerfile")):
        raise FileNotFoundError("Dockerfile not found")

    # Check if docker image already exists

    image = None

    if not overwrite:
        try:
            image = client.images.get(tag)
        except ImageNotFound:
            print("Docker image not found")
        except Exception as e:
            print(f"Error: {e}")
            raise e

    if image:
        print("Docker image already exists")
        print(image)
        return image
    else:
        print("Docker image does not exist")

        # Create docker image from Dockerfile
        image, build_logs = client.images.build(
            path=file_path, tag=tag, dockerfile="Dockerfile"
        )

        for log in build_logs:
            if "stream" in log:
                print(log["stream"].strip())

        print("Docker image created")

        return image


@task
def main_task(image: str, memory_limit: str, data_filepath: str):
    client = None
    try:
        client = initialize_docker_client()
        # image = create_docker_image(client, prefect_logger)

        submission_file_name = "submission.submission_wrapper"
        submission_function_name = "detect_time_shifts"
        submission_args = [data_filepath]

        docker_task(
            client,
            image,
            memory_limit,
            submission_file_name,
            submission_function_name,
            submission_args,
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            client.close()


def main_flow(memory_limit: str):
    tag: str = "submission:latest"

    client = None
    try:
        client = initialize_docker_client()
        image = create_docker_image(tag, client, overwrite=True)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            client.close()

    data_files = os.listdir("data")
    print(data_files)

    if not data_files:
        raise FileNotFoundError("No data files found")

    files = data_files

    for filepath in files:
        main_task.submit(tag, memory_limit, filepath)


def main():

    memory_limit = "8"

    flow(
        task_runner=DaskTaskRunner(
            cluster_kwargs={
                "n_workers": 3,
                "threads_per_worker": 1,
                "memory_limit": f"{memory_limit}GiB",
            }
        ),
        log_prints=True,
    )(main_flow)(memory_limit)


if __name__ == "__main__":
    main()
