import os
from typing import Any
from prefect import flow, task
from prefect_dask.task_runners import DaskTaskRunner
import docker


def docker_task(
    client: docker.DockerClient,
    submission_file_name: str,
    submission_function_name: str,
    submission_args: list[Any] | None = None,
):

    if submission_args is None:
        submission_args = []

    # Define volumes to mount
    results_dir = os.path.join(os.path.dirname(__file__), "results")

    volumes = {
        results_dir: {"bind": "/app/results/", "mode": "rw"},
    }

    # Execute docker image in a container
    print("Docker container started")
    container = client.containers.run(
        "submission:latest",
        command=[
            "python",
            "submission_wrapper.py",
            submission_file_name,
            submission_function_name,
            *submission_args,
        ],
        auto_remove=True,
        volumes=volumes,
    )
    print(container)


def create_docker_image():
    client = docker.from_env()

    file_path = os.path.join(os.path.dirname(__file__), "submission")

    print(file_path)

    # Create docker image from Dockerfile
    image, index = client.images.build(path=file_path, tag="submission:latest")
    print("Docker image created")

    return client


@task
def main_task(index: int):
    client = None
    try:
        client = create_docker_image()

        submission_file_name = "submission"
        submission_function_name = "submission_function"
        submission_args = [str(index)]

        docker_task(
            client,
            submission_file_name,
            submission_function_name,
            submission_args,
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            client.close()


@flow(
    task_runner=DaskTaskRunner(
        cluster_kwargs={
            "n_workers": 4,
            "threads_per_worker": 1,
            "memory_limit": "8GiB",
        }
    ),
    log_prints=False,
)
def main_flow():
    for i in range(5):
        main_task.submit(i)


def main():
    main_flow()


if __name__ == "__main__":
    main()
