server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        # Serve the content over HTTP
        uwsgi_pass           ${APP_HOST}:${APP_PORT};
        include              /etc/nginx/uwsgi_params;
        client_max_body_size 10M;

        error_page 404 /custom_404;
        location = /custom_404 {
            internal;
            uwsgi_pass ${APP_HOST}:${APP_PORT};
            include /etc/nginx/uwsgi_params;
        }
    }

    location /static {
        alias /vol/static;
    }

    location = /riot.txt {
        alias /vol/static/static/match_history/texts/riot.txt;
    }
}
