# syntax=docker/dockerfile:1
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json /app/
RUN yarn install
COPY frontend /app
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
RUN yarn build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
# Simple nginx config with try_files
RUN printf 'server {\n  listen 80;\n  server_name _;\n  root /usr/share/nginx/html;\n  include /etc/nginx/mime.types;\n  location / {\n    try_files $uri /index.html;\n  }\n}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
