# pv-validation-hub


## Jira link:

[Sprint Board](https://pv-validation-hub.atlassian.net/jira/software/projects/PVH/boards/1/)


## Documentation

- [PV validation hub requirements whitepaper](https://docs.google.com/document/d/e/2PACX-1vSQwL7_T0gTMJj7Z6nM5KYm0mzFAz0r_11hpzvCmlGyg5LPeKnyrKIZrwqQ7g5eS80ynmZWKnRA3-n0/pub)
- [Technical Requirements Document](https://docs.google.com/document/d/e/2PACX-1vSOjb0lh8LQ-jnrHf5CqAModR2NoGTU-GMHYOfJuUSEK4g71MIm9E3cPEuYqfuKPiP9VdUe2C5DCJD-/pub)
- [Practicum pitch slides](https://tinyurl.com/HubSlides)

## Figma Board

[Figma](https://www.figma.com/files/project/65110512/Team-project?fuid=1050154100208382320)

### Resources

K6 Load Tester: [Loadforge](https://loadforge.com/?utm_source=googleads&utm_medium=cpc&utm_campaign=usa&utm_content=112112401679&utm_term=k6.io&gclid=CjwKCAjw3qGYBhBSEiwAcnTRLshx2HB--zEgjFhdP2Po0qe0J7t4JnmGi6WwWywLLGZykIKy8nQBjxoCiMUQAvD_BwE)

## Useful tutorials for new devs:

### Docker-compose: 

[Video] (https://youtu.be/HG6yIjZapSA)

Note: docker-compose will automatically use environment variables specified in the ```.env``` file located at the project root. Variables specified in the shell take precedence over the env file. Copy and rename the ```.env.example``` file to ```.env``` and fill-in the desired values. ```.env``` files should never be committed, and should always be part of the ```.gitignore``` file, for safe development.

[Environment] (https://docs.docker.com/compose/environment-variables/)