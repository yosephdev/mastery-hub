web: gunicorn skill_sharing_platform.wsgi --log-file -
release: python manage.py migrate
worker: celery -A skill_sharing_platform worker -l info



