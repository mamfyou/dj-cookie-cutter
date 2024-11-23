import os
import sys

import django
from django.apps import apps
from django.conf import settings

project_name = '{{cookiecutter.project_slug}}'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'{project_name}.settings')

django.setup()

installed_apps = settings.INSTALLED_APPS

for app in installed_apps:
    app_config = apps.get_app_config(app.split(".")[-1])
    migrations_dir = os.path.join(app_config.path, "migrations")
    if os.path.exists(migrations_dir):
        for filename in os.listdir(migrations_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                os.remove(os.path.join(migrations_dir, filename))