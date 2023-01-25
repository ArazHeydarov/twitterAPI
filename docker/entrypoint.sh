#!/usr/bin/env sh
if [ "$1" = "django" ]; then
  echo "Django starting"
  gunicorn
elif [ "$1" = "celery" ]; then
  echo "Celery starting"
  celery -A twitterAPI worker -l info --pool=eventlet --concurrency=10
fi
