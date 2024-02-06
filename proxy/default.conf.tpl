server {
    listen ${LISTEN_PORT};

    location /static/media/ {
        alias /vol/static/media/;
    }

    location /static {
        alias /vol/static/static/;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }
}