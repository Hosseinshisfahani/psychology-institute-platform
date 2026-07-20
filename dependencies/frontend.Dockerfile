FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY dependencies/nginx-frontend.conf /etc/nginx/conf.d/default.conf

COPY frontend/build /usr/share/nginx/html

EXPOSE 80
