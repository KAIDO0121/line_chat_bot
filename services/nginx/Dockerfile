FROM nginx:alpine
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./certificate.crt /etc/ssl/certificate.crt
COPY ./private.key /etc/ssl/private.key

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]