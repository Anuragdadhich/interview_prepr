web: gunicorn --config gunicorn.conf.py core.wsgi:application
worker: celery worker --app=core --loglevel=info
beat: celery beat --app=core --loglevel=info