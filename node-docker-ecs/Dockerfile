# Use an official Node runtime as a parent image
FROM node:14-alpine

# Set the working directory to /app
WORKDIR /app

# Copy both package.json and package-lock.json to the working directory
COPY package*.json ./

# Install any needed packages specified in package.json
RUN yarn install --frozen-lockfile --non-interactive

# Copying the rest of the code to the working directory
COPY . .

# Make docker-entrypoint.sh executable
RUN chmod +x docker-entrypoint.sh
RUN cp docker-entrypoint.sh /usr/local/bin

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run index.js when the container launches
CMD ["/bin/sh", "/app/docker-entrypoint.sh"]
