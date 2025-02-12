# PV-Validation-Hub

The Photovoltaic(PV) Validation Hub project is designed to be a one-stop-shop for industry and academic researchers to develop, test and evaluate their PV algorithms. To meet this dual-purpose assignment(e.g. Industry looking for the best algorithms and researchers looking to evaluate and refine their algorithms against otherwise difficult-to-obtain data), the validation hub will provide layered results to help industry and the researchers using the system.

Through publicly available leaderboards for different analytical tasks, industry can evaluate the efficacy, resolution time, and error-rates of different tasks to find the best algorithms for their specific use-cases.

Meanwhile, researchers will be able to benefit from receiving personal, high-fidelity results tailored to help them refine and further perfect their algorithms.

Finally, both industry and academia will be able to enjoy the assurance of accurate results through protection and anonymization of the used data-sets. By only providing results, industry and academia can be assured of the validity of an algorithm, as it would prevent the possibility of tailoring an algorithm to match the data.

## Developer quick-start

To begin development on the validation hub, download and install the [Docker client](https://www.docker.com). Alternatively, if you installed docker only for the command line tools, then you will need to also make sure to install ```docker-compose``` and to update both to the latest versions. You will need to generate a secret key for Django before you proceed. From the repository root, run the following:

~~~
cp .env.example .env
nano .env
// replace the placeholder text in the djangosk variable with your secret key
docker-compose up
~~~

Following those steps, you should now be able to access your local development version at ```localhost:3000```!

You can also manually install all the services locally for faster developmental iterations at your own discretion.

### Additional Prep

There are some additional steps to complete now that you have the validation hub up and running on your system. In the ```s3Emulator/preload``` directory, you will find several script files that will preload the database with all the basic elements needs to use an analysis as well as to create a test user and an example submission. If you set up a local build instead of the docker network, you will have to modify the scripts and configurations on your own.

- First, you will need to create a super-user. Open a shell in the api using either ```docker exec <container-id> bash``` or by using the terminal button next to the api container in docker desktop. Then run ```python3 manage.py createsuperuser``` and follow each of the steps. Since this is for local use, choose very simple and easy values to remember.
- Next, open ```localhost:8005/admin``` on your browser. You can sign in with the credentials you just created. This will let you see everything you will do next to populate the database.
- Now, you will need to open a shell in the s3 emulator container, and run the following commands.
~~~
cd preload
./loaddb.sh
~~~
- After the entire script has finished running, you will see "preload complete" print onto the terminal. This will now have the entire validation hub prepped for local development and use. 

## Jira link:

[Sprint Board](https://pv-validation-hub.atlassian.net/jira/software/projects/PVH/boards/1/)


## Documentation

Updating the ERD can be done using `djangoviz`. This should NOT be committed to production.

The steps to use it are simple:

When running a local container, update the following in `valhub/valhub/settings.py:`
```
INSTALLED_APPS = [
    "other apps",
    "djangoviz"
]
```

Then exec into your docker container, and run `python3 manage.py djangoviz`, the follow the link returned in the shell. You can share the link or take a screenshot to add the updated ERD into the docs directory.

- [PV validation hub requirements whitepaper](https://docs.google.com/document/d/e/2PACX-1vSQwL7_T0gTMJj7Z6nM5KYm0mzFAz0r_11hpzvCmlGyg5LPeKnyrKIZrwqQ7g5eS80ynmZWKnRA3-n0/pub)
- [Technical Requirements Document](https://docs.google.com/document/d/e/2PACX-1vSOjb0lh8LQ-jnrHf5CqAModR2NoGTU-GMHYOfJuUSEK4g71MIm9E3cPEuYqfuKPiP9VdUe2C5DCJD-/pub)
- [Practicum pitch slides](https://tinyurl.com/HubSlides)
- [Entity Relationship Diagram(Updated Oct 28, 2022)](https://drive.google.com/file/d/1jumoYNzJxIbATfRnDzyop6E5a0Zui_cq/view?usp=sharing)

## Figma Board

[Figma](https://www.figma.com/files/project/65110512/Team-project?fuid=1050154100208382320)

### Resources

K6 Load Tester: [Loadforge](https://loadforge.com/?utm_source=googleads&utm_medium=cpc&utm_campaign=usa&utm_content=112112401679&utm_term=k6.io&gclid=CjwKCAjw3qGYBhBSEiwAcnTRLshx2HB--zEgjFhdP2Po0qe0J7t4JnmGi6WwWywLLGZykIKy8nQBjxoCiMUQAvD_BwE)

## Useful tutorials for new devs:

### Docker-compose: 

[Video] (https://youtu.be/HG6yIjZapSA)

Note: docker-compose will automatically use environment variables specified in the ```.env``` file located at the project root. Variables specified in the shell take precedence over the env file. Copy and rename the ```.env.example``` file to ```.env``` and fill-in the desired values. ```.env``` files should never be committed, and should always be part of the ```.gitignore``` file, for safe development.

[Environment] (https://docs.docker.com/compose/environment-variables/)

## Important Developer Notes

### Managing Leaderboard Display Fields
For dynamic analysis error fields and dynamic display options on the front end, we have an informal yet critical connection from the Analysis object and the submission object.

The Analysis Model has a display error JSONfield, while the submission object has a Result JSONfield.

The Display errors field will set the field display name and tracking key on the leaderboard.

The keys in Display errors and Result must match in order for the result values to display on the front end.

Analysis:
```
...
Display errors: {"mae": "MAE", "test": "FOO!"}
...
```

Submission:
```
...
Result: {"mae": 44, "test": 9001}
...
```

In this example, we will get two columns: "MAE" and "FOO!"
"MAE" will have the value 44 display for its submission, while "FOO!" will have the number 9001 display.

This setup enables us to have multiple different analytical tasks, with customizable names and display metrics.

We can store as many different result fields as we want into Result, and can add or remove the display keys from the Analysis to show which one's we want.
