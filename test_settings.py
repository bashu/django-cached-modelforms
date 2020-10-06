
SECRET_KEY = 'DUMMY_SECRET_KEY'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

PROJECT_APPS = [
    'cached_modelforms',
]

INSTALLED_APPS = [
    'django.contrib.contenttypes',
] + PROJECT_APPS
