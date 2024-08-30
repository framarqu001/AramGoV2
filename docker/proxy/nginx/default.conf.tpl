server {
    listen 80;
    server_name aram-go www.aram-go.com;

    location /.well-known/acme-challenge/ {
        root /vol/www/;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}