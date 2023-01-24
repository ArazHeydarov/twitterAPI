wsgi_app = "twitterAPI.wsgi:application"
loglevel = "info"
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn.log"
capture_output = True
name = "twitterProject"
bind = "0.0.0.0:8000"
timeout = 120
workers = 3
pidfile = "logs/gunicorn.pid"
reload = False
