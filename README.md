# PV-Validation-Hub

The Photovoltaic(PV) Validation Hub project is designed to be a one-stop-shop for industry and academic researchers to develop, test and evaluate their PV algorithms. To meet this dual-purpose assignment(e.g. Industry looking for the best algorithms and researchers looking to evaluate and refine their algorithms against otherwise difficult-to-obtain data), the validation hub will provide layered results to help industry and the researchers using the system.

Through publicly available leaderboards for different analytical tasks, industry can evaluate the efficacy, resolution time, and error-rates of different tasks to find the best algorithms for their specific use-cases.

Meanwhile, researchers will be able to benefit from receiving personal, high-fidelity results tailored to help them refine and further perfect their algorithms.

Finally, both industry and academia will be able to enjoy the assurance of accurate results through protection and anonymization of the used data-sets. By only providing results, industry and academia can be assured of the validity of an algorithm, as it would prevent the possibility of tailoring an algorithm to match the data.

## Table of Contents

- [PV-Validation-Hub](#pv-validation-hub)
  - [Table of Contents](#table-of-contents)
  - [Quick Start Instructions](#quick-start-instructions)
    - [Update Submodule](#update-submodule)
    - [Pre-commit and Black formatting](#pre-commit-and-black-formatting)
    - [ENV File](#env-file)
    - [Docker compose](#docker-compose)
      - [Increasing memory limit](#increasing-memory-limit)
    - [Website links](#website-links)
    - [Uploading an analysis](#uploading-an-analysis)
    - [Debugging and Troubleshooting](#debugging-and-troubleshooting)
  - [Troubleshooting](#troubleshooting)
    - [Django API Fixes](#django-api-fixes)
      - [Admin not found](#admin-not-found)
      - [Migrate Django API](#migrate-django-api)
  - [Documentation](#documentation)
  - [Figma Board](#figma-board)
  - [Useful tutorials for new devs](#useful-tutorials-for-new-devs)
    - [Docker-compose](#docker-compose-1)

## Quick Start Instructions

To get a local version of the PV Validation Hub running you will need to have Docker installed on your host machine.

### Update Submodule

To have the front-end client build properly you will need to pull the latest changes from the repo. Since it exists as a submodule you can pull all the latest changes from main with the following git command

```bash
    git submodule update --init --recursive
```

### Pre-commit and Black formatting

Install the base python packages using `python pip install -r requirements.txt` in the base directory of the repository.

To make sure pre-commit is active for submitting changes to the Github repository you will need to install pre-commit using the following command.

```bash
    pre-commit install
```

Additional information is located here:

[pre-commit](https://pre-commit.com/)

### ENV File

Here is an example .env file which you should fill out with your own values

```env
    djangosk=django-insecure-y&pp1if&0y)pxtmqf_@o1br(&-6mrxv**f5%&73d@d51kscvg!
    POSTGRES_PASSWORD=valhub
    POSTGRES_USER=valhub
    admin_username=admin
    admin_password=admin
    admin_email=admin@admin.com
    DOCKER_HOST_VOLUME_DATA_DIR="<path-to-repository>/<repo-name>/workers/current_evaluation/data"
    DOCKER_HOST_VOLUME_RESULTS_DIR="<path-to-repository>/<repo-name>/workers/current_evaluation/results"
```

### Docker compose

To get all the environments up and running all you will need to do is to use `docker compose up` or `docker compose up --watch`.

Using this will download the images required for each service and spin then up in the correct order automatically.

There are many different bind mounts for each service which will create a symbolic link between the files on the host directory and the files attributed within the docker containers for debugging purposes. These various bind mounts can be seen within the `docker-compose.yml` file.

#### Increasing memory limit

If you find that there is not enough memory when running submissions you can change the memory limit within Docker Desktop. You can increase the memory allocation for Docker through the Settings > Resources > Memory Limit slider.

### Website links

The frontend port is 3000 and the Django API port is 8005. So you can access the frontend at [localhost:3000](http://localhost:3000) and the admin dashboard at [localhost:8005/admin](http://localhost:8005/admin)

### Uploading an analysis

To upload a new analysis to the PV Validation Hub you will need to create a shell inside the running EC2 docker container in the same way described on how to do so listed in the [Admin not found](#admin-not-found) section.

Once you have a valid shell inside the docker container you will notice that there is an `insert_analysis.py` and this will be your main entrypoint to uploading a new analysis.

You will also need all the files required for a valid analysis. All of this is described within the [README.md](/ec2/README.md) within the `ec2` folder within this repository.

### Debugging and Troubleshooting

When uploading a submission zip to the analysis task you created you can view the logs both in the docker desktop for the worker container but also within the `worker/logs` folder.

After the submission has been processed the logs are reset for the next submission and the logs are added to the submission S3 artifacts. In the repository for example a submission is located here `s3Emulator/pv-validation-hub-bucket/submission_files/submission_user_{###}/submission_{###}/logs`.

## Troubleshooting

### Django API Fixes

There may be two different issues that could come up when running docker compose.

#### Admin not found

If you are unable to login to the admin dashboard or into your profile on the frontend after including the `admin_username`, `admin_password`, and `admin_email` from within the .env file you will need to do so manually.

To fix this issue you will need to create a shell inside the docker container for the Django API. You can do this easily using the Docker Desktop program by clicking on the 3 dots on the side of the running container and opening a terminal. You can also do so by creating a shell using VS code with the Docker extension by right clicking on the running container within the extension sidebar and creating a shell.

Once you have an active shell inside the Django API docker container there is a `manage.py` script that allows you to manually edit and manage the Django API. The command that you will need will be the following:

```bash
    python manage.py createsuperuser
```

After running this inside the root directory of the docker container you will need to follow the prompts to provide a username and password for the admin account.

After doing so you will have made a valid admin user and you should be able to login to both the admin dashboard to change and check the state of the database but also to login the frontend to upload submission zip files to tasks.

#### Migrate Django API

When model changes occur that require the database to be modified in a major way you will be prompted to migrate the changes when running docker compose.

To do so you can follow the instructions on how to get an interactive shell inside the Django API docker container listed in the [Admin not found](#admin-not-found) section.

Once you have a valid shell inside the container you will need to run two different commands in the base directory to merge the new changes.

```bash
    python manage.py makemigrations
    python manage.py migrate
```

With these two commands in order the database should create the new changes and commit them with the rest of the existing data.

## Documentation

- [PV validation hub requirements whitepaper](https://docs.google.com/document/d/e/2PACX-1vSQwL7_T0gTMJj7Z6nM5KYm0mzFAz0r_11hpzvCmlGyg5LPeKnyrKIZrwqQ7g5eS80ynmZWKnRA3-n0/pub)
- [Technical Requirements Document](https://docs.google.com/document/d/e/2PACX-1vSOjb0lh8LQ-jnrHf5CqAModR2NoGTU-GMHYOfJuUSEK4g71MIm9E3cPEuYqfuKPiP9VdUe2C5DCJD-/pub)
- [Practicum pitch slides](https://tinyurl.com/HubSlides)
- [Entity Relationship Diagram(Updated Oct 28, 2022)](https://drive.google.com/file/d/1jumoYNzJxIbATfRnDzyop6E5a0Zui_cq/view?usp=sharing)

## Figma Board

[Figma](https://www.figma.com/files/project/65110512/Team-project?fuid=1050154100208382320)

## Useful tutorials for new devs

### Docker-compose

[Video] (<https://youtu.be/HG6yIjZapSA>)

Note: docker-compose will automatically use environment variables specified in the ```.env``` file located at the project root. Variables specified in the shell take precedence over the env file. Copy and rename the ```.env.example``` file to ```.env``` and fill-in the desired values. ```.env``` files should never be committed, and should always be part of the ```.gitignore``` file, for safe development.

[Environment] (<https://docs.docker.com/compose/environment-variables/>)
