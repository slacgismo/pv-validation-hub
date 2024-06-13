import os
from prefect import flow, task
from prefect_dask.task_runners import DaskTaskRunner
import docker


def docker_task(client: docker.DockerClient, index: int = -1):

    # Define volumes to mount
    results_dir = os.path.join(os.path.dirname(__file__), "results")

    volumes = {
        results_dir: {"bind": "/app/results/", "mode": "rw"},
    }

    # Execute docker image in a container
    print("Docker container started")
    container = client.containers.run(
        "submission:latest",
        command=["python", "submission.py", f"{index}"],
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

    client = create_docker_image()
    docker_task(client=client, index=index)
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
    for i in range(30):
        main_task.submit(i)


def main():
    main_flow()


if __name__ == "__main__":
    main()
