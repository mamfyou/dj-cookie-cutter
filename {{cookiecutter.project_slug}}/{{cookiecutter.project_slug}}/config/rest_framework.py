REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': '{{cookiecutter.project_slug}}.pagination.MainPagination',
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'EXCEPTION_HANDLER': '{{cookiecutter.project_slug}}.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_RATES': {
        'anon': f'250/minute',
        'user': f'250/minute'
    }

}
