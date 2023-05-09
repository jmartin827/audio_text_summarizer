FROM node:20.1.0 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:latest as prod
WORKDIR /usr/share/nginx/html
# Remove Nginx assets
RUN rm -rf ./*
COPY --from=build /app/build /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/*
ADD nginx.conf /etc/nginx/conf.d/

# Expose port 8000. TODO determine best practice as it works without this
EXPOSE 8000
