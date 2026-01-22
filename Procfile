web: gunicorn core.wsgi --log-file -
worker: celery worker --app=core --loglevel=info
beat: celery beat --app=core --loglevel=info