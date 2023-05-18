# Packages a build result into nginx container
FROM nginx:latest as prod
WORKDIR /usr/share/nginx/html
# Remove Nginx assets
RUN rm -rf ./*
COPY /build /usr/share/nginx/html
RUN rm /etc/nginx/conf.d/*
ADD nginx.conf /etc/nginx/conf.d/

# Expose port 8000. TODO determine best practice as it works without this
EXPOSE 8000
