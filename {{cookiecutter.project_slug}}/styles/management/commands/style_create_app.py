import os

from django.conf import settings
from django.core.management.base import BaseCommand

BASE_DIR = settings.BASE_DIR.__str__()


class Command(BaseCommand):
    def create_app(self, app_name):
        os.system(f"mkdir {BASE_DIR}/{app_name}")
        os.system(f"touch {BASE_DIR}/{app_name}/__init__.py")

        os.system(f"mkdir {BASE_DIR}/{app_name}/migrations")
        os.system(f"touch {BASE_DIR}/{app_name}/migrations/__init__.py")

        os.system(f"mkdir {BASE_DIR}/{app_name}/tests")
        os.system(f"touch {BASE_DIR}/{app_name}/tests/__init__.py")

        os.system(f"mkdir {BASE_DIR}/{app_name}/api")
        os.system(f"touch {BASE_DIR}/{app_name}/api/__init__.py")

        os.system(f"touch {BASE_DIR}/{app_name}/api/serializers.py")
        serializers_text = f"from rest_framework import serializers\n\n# Create your serializers here."
        os.system(f"echo '{serializers_text}' > {BASE_DIR}/{app_name}/api/serializers.py")

        os.system(f"touch {BASE_DIR}/{app_name}/api/api_views.py")
        api_views_text = f"from rest_framework import generics\n\n# Create your views here."
        os.system(f"echo '{api_views_text}' > {BASE_DIR}/{app_name}/api/api_views.py")

        os.system(f"touch {BASE_DIR}/{app_name}/api/urls.py")
        api_urls_text = f"from django.urls import path\n\nurlpatterns = [\n\n]"
        os.system(f"echo '{api_urls_text}' > {BASE_DIR}/{app_name}/api/urls.py")

        os.system(f"touch {BASE_DIR}/{app_name}/admin.py")
        admin_text = f"from django.contrib import admin\n\n# Register your models here."
        os.system(f"echo '{admin_text}' > {BASE_DIR}/{app_name}/admin.py")

        os.system(f"touch {BASE_DIR}/{app_name}/apps.py")
        apps_text = f"from django.apps import AppConfig\n\n\nclass {app_name.capitalize()}Config(AppConfig):\n    default_auto_field = \"django.db.models.BigAutoField\"\n    name = \"{app_name}\" \n    import {app_name}.signals"
        os.system(f"echo '{apps_text}' > {BASE_DIR}/{app_name}/apps.py")

        os.system(f"touch {BASE_DIR}/{app_name}/models.py")
        models_text = f"from django.db import models\n\n# Create your models here."
        os.system(f"echo '{models_text}' > {BASE_DIR}/{app_name}/models.py")

        os.system(f"touch {BASE_DIR}/{app_name}/signals.py")
        signals_text = f"from django.db.models.signals import post_save\nfrom django.dispatch import receiver\n\n\n# Create your signals here."
        os.system(f"echo '{signals_text}' > {BASE_DIR}/{app_name}/signals.py")

        os.system(f"touch {BASE_DIR}/{app_name}/exceptions.py")
        exceptions_text = f"from rest_framework.exceptions import APIException\n\n\nclass {app_name.capitalize()}Exception(APIException):\n    pass"
        os.system(f"echo '{exceptions_text}' > {BASE_DIR}/{app_name}/exceptions.py")

        os.system(f"touch {BASE_DIR}/{app_name}/permissions.py")
        permissions_text = f"from rest_framework.permissions import BasePermission\n\n\nclass {app_name.capitalize()}Permission(BasePermission):\n    pass"
        os.system(f"echo '{permissions_text}' > {BASE_DIR}/{app_name}/permissions.py")

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str)

    def handle(self, *args, **options):
        app_name = options['app_name']
        self.create_app(app_name)
        self.stdout.write(
            self.style.SUCCESS(f"Created Django app '{app_name}' with the specified structure.")
        )
