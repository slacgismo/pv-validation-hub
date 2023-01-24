In order to run the valhub backend, you will need to have Docker installed. The DJANGO_SECRET_KEY is a secret you will need, passed via the ```djangosk``` build arg to the dockerfile. You can follow the steps in the dockerfile if you want to build and run natively for testing purposes. DO NOT save any keys into the repository. 

Long-term goal is to setup a toplevel docker-compose file to start the entire application from one build command for local development and integration testing.

To build the API, from the top-level of the repository, run ```docker build --no-cache --progress=plain --build-arg djangosk='your-secret-key' -t "image-name:Dockerfile" -f valhub/Dockerfile .``` The ```--progress=plain``` flag is not necessary, but useful for debugging. 

To run the API and make it accessible from localhost, run ```docker run --name container-name -p 5001:5001 your-image:Dockerfile```