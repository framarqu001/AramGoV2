# Base image: Unprivileged Nginx
FROM nginxinc/nginx-unprivileged:1-alpine

# Maintainer label
LABEL maintainer="londonappdeveloper.com"

# Copy necessary configuration and script files
COPY nginx/default.conf.tpl /etc/nginx/default.conf.tpl
COPY nginx/uwsgi_params /etc/nginx/uwsgi_params
COPY nginx/* /etc/nginx/
COPY run.sh /run.sh

# Environment variables
ENV APP_HOST=django
ENV APP_PORT=9000

# Switch to root user to perform necessary operations
USER root

# Create directories, set permissions, and prepare Nginx for use
RUN mkdir -p /vol/static /vol/www && \
    chmod 755 /vol/static /vol/www && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh && \
    apk add --no-cache openssl bash  # Added package installation from the second Dockerfile

# Define volumes for static files and web content
VOLUME /vol/static
VOLUME /vol/www

# Switch back to the unprivileged user
USER nginx

# Set the default command to run the custom script
CMD ["/run.sh"]
