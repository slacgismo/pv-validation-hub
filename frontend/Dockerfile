FROM node:16-alpine as builder
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
COPY ./.env.example .env
RUN npm run build
RUN npm install -g serve
EXPOSE 3000
CMD ["npx", "serve", "-s", "build"]