server {
    listen 80;
    server_name aram-go.com www.aram-go.com;

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen      443 ssl;
    server_name aram-go.com www.aram-go.com;

    ssl_certificate     /etc/letsencrypt/live/aram-go.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aram-go.com/privkey.pem;

    include     /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass           django:9000;  # Replace with your actual app host and port
        include              /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
    }
}
