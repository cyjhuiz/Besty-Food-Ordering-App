FROM node:14
WORKDIR /usr/src/app
COPY package*.json ./

RUN npm install
COPY . .

EXPOSE 5006
CMD [ "node", "./index.js" ]