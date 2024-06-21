import os
from typing import Any, Dict, Sequence, TypeVar, cast
from dask.distributed import Client
from dask.delayed import delayed
import docker.models
import docker.models.containers
import docker
from docker.models.images import Image
from docker.models.containers import Container
from docker.errors import ImageNotFound


# @task
# def main_task(image: str, memory_limit: str, data_filepath: str):
#     client = None
#     try:
#         client = initialize_docker_client()
#         # image = create_docker_image(client, prefect_logger)

#         submission_file_name = "submission.submission_wrapper"
#         submission_function_name = "detect_time_shifts"
#         submission_args = [data_filepath]

#         docker_task(
#             client,
#             image,
#             memory_limit,
#             submission_file_name,
#             submission_function_name,
#             submission_args,
#         )
#     except Exception as e:
#         raise e
#     finally:
#         if client:
#             client.close()


# def main_flow(memory_limit: str):
#     tag: str = "submission:latest"

#     check_if_docker_daemon_is_running()

#     client = None
#     try:
#         client = initialize_docker_client()
#         image = create_docker_image(tag, client, overwrite=True)
#     except Exception as e:
#         raise e
#     finally:
#         if client:
#             client.close()

#     data_files = os.listdir("data")
#     print(data_files)

#     if not data_files:
#         raise FileNotFoundError("No data files found")

#     files = data_files[:5]

#     for filepath in files:
#         main_task.submit(tag, memory_limit, filepath)


# def main():

#     memory_limit = "8"

#     flow(
#         task_runner=DaskTaskRunner(
#             cluster_kwargs={
#                 "n_workers": 2,
#                 "threads_per_worker": 1,
#                 "memory_limit": f"{memory_limit}GiB",
#             }
#         ),
#         log_prints=True,
#     )(main_flow)(memory_limit)


# def main_func(memory_limit: str):
#     tag: str = "submission:latest"

#     check_if_docker_daemon_is_running()

#     client = None
#     try:
#         client = initialize_docker_client()
#         image = create_docker_image(tag, client, overwrite=True)
#     except Exception as e:
#         raise e
#     finally:
#         if client:
#             client.close()

#     data_files = os.listdir("data")
#     print(data_files)

#     if not data_files:
#         raise FileNotFoundError("No data files found")

#     files = data_files[:5]

#     for filepath in files:
#         sub_func.submit(tag, memory_limit, filepath)


# Functions for main code


class DockerContainerContextManager:

    def __init__(
        self,
        client: docker.DockerClient,
        image: Image | str,
        command: str | list[str],
        volumes: dict[str, dict[str, str]] | list[str],
        mem_limit: str | None = None,
    ) -> None:
        self.client = client
        self.container: Container | None = None
        self.image = image
        self.command = command
        self.volumes = volumes
        self.mem_limit = f"{mem_limit}g" if mem_limit else None

    def __enter__(self):
        container = self.client.containers.run(
            image=self.image,
            command=self.command,
            volumes=self.volumes,
            detach=True,
            stdout=True,
            stderr=True,
            mem_limit=self.mem_limit,
        )

        self.container = cast(Container, container)
        return self.container

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.container:
            if self.container.status == "running":
                self.container.stop()
            self.container.remove()


def docker_task(
    client: docker.DockerClient,
    image: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: Sequence[Any],
    data_dir: str,
    results_dir: str,
):

    if submission_args is None:
        submission_args = []

    # Define volumes to mount
    # results_dir = os.path.join(os.path.dirname(__file__), "results")
    # data_dir = os.path.join(os.path.dirname(__file__), "data")

    volumes = {
        results_dir: {"bind": "/app/results/", "mode": "rw"},
        data_dir: {"bind": "/app/data/", "mode": "ro"},
    }

    command: list[str] = [
        "python",
        "submission_wrapper.py",
        submission_file_name,
        submission_function_name,
        *submission_args,
    ]

    with DockerContainerContextManager(
        client, image, command, volumes, memory_limit
    ) as container:
        print("Docker container starting...")
        print(f"Image: {image}")
        print(f"Submission file name: {submission_file_name}")
        print(f"Submission function name: {submission_function_name}")
        print(f"Submission args: {submission_args}")

        # Wait for container to finish
        for line in container.logs(stream=True):
            line = cast(str, line)
            print(line.strip())

        container.wait()


def submission_task(
    image_tag: str,
    memory_limit: str,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: Sequence[Any],
    data_dir: str,
    results_dir: str,
):

    with DockerClientContextManager() as client:
        docker_task(
            client=client,
            image=image_tag,
            memory_limit=memory_limit,
            submission_file_name=submission_file_name,
            submission_function_name=submission_function_name,
            submission_args=submission_args,
            data_dir=data_dir,
            results_dir=results_dir,
        )


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


class DockerClientContextManager:
    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = initialize_docker_client()
        return self.client

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.client:
            self.client.close()


def initialize_docker_client():
    base_url = os.environ.get("DOCKER_HOST")

    if not base_url:
        raise FileNotFoundError("DOCKER_HOST environment variable not set")

    # cert_path = os.environ.get("DOCKER_CERT_PATH")
    # if not cert_path:
    #     raise FileNotFoundError(
    #         "DOCKER_CERT_PATH environment variable not set"
    #     )

    # if not os.path.exists(cert_path):
    #     raise FileNotFoundError(f"Cert path {cert_path} not found")

    # ca_cert = cert_path + "/ca.pem"
    # client_cert = cert_path + "/ca-key.pem"
    # client_key = cert_path + "/key.pem"

    # if not os.path.exists(ca_cert):
    #     raise FileNotFoundError(f"CA cert {ca_cert} not found")
    # if not os.path.exists(client_cert):
    #     raise FileNotFoundError(f"Client cert {client_cert} not found")
    # if not os.path.exists(client_key):
    #     raise FileNotFoundError(f"Client key {client_key} not found")

    client = docker.DockerClient(
        base_url=base_url,
        version="auto",
        # tls={
        #     "ca_cert": ca_cert,
        #     "client_cert": (client_cert, client_key),
        #     "verify": True,
        # },
    )
    return client


def is_docker_daemon_running():
    is_running = False

    with DockerClientContextManager() as client:
        if client.ping():
            is_running = True

    return is_running


def create_docker_image_for_submission():
    tag = "submission:latest"

    is_docker_daemon_running()

    with DockerClientContextManager() as client:
        image = create_docker_image(tag, client, overwrite=True)

    return image, tag


def dask_main():
    results: list = []

    total_workers = 2
    total_threads = 1
    memory_per_worker = 8

    image, tag = create_docker_image_for_submission()

    data_files = os.listdir("data")
    print(data_files)

    if not data_files:
        raise FileNotFoundError("No data files found")

    files = data_files[:5]

    submission_file_name = "submission.submission_wrapper"
    submission_function_name = "detect_time_shifts"

    data_dir = "/Users/mvicto/Desktop/Projects/PVInsight/pv-validation-hub/pv-validation-hub/dockerize-workflow/data"
    results_dir = "/Users/mvicto/Desktop/Projects/PVInsight/pv-validation-hub/pv-validation-hub/dockerize-workflow/results"

    with Client(
        n_workers=total_workers,
        threads_per_worker=total_threads,
        memory_limit=f"{memory_per_worker}GiB",
        # **kwargs,
    ) as client:

        lazy_results = []
        for file in files:
            submission_args = (file,)
            lazy_result = delayed(submission_task, pure=True)(
                tag,
                memory_per_worker,
                submission_file_name,
                submission_function_name,
                submission_args,
                data_dir,
                results_dir,
            )
            lazy_results.append(lazy_result)

        futures = client.compute(lazy_results)

        results = client.gather(futures)  # type: ignore

    return results


if __name__ == "__main__":
    # main()
    dask_main()
    # check_if_docker_daemon_is_running()
