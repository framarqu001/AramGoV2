# Use the official nginx-unprivileged image for better security
FROM nginxinc/nginx-unprivileged:1.25-alpine

# Maintainer information
LABEL maintainer="londonappdeveloper.com"

# Copy necessary configuration files
COPY default.conf.tpl /etc/nginx/templates/default.conf.tpl
COPY uwsgi_params /etc/nginx/uwsgi_params
COPY run.sh /docker-entrypoint.d/run.sh

# Environment variables for dynamic configuration
ENV LISTEN_PORT=8000
ENV APP_HOST=django
ENV APP_PORT=9000

# Ensure scripts and directories are set up with correct permissions
USER root

# Create necessary directories and set appropriate permissions
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    chmod +x /docker-entrypoint.d/run.sh && \
    chown -R nginx:nginx /vol/static /etc/nginx/templates /etc/nginx/uwsgi_params

# Expose a volume for static files
VOLUME /vol/static

# Revert back to non-root user for security
USER nginx

# Command to run when the container starts
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
