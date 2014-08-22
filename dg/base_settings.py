# Django settings for dg project.
import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
APPEND_SLASH = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/social_website/uploads/documents/%Y/%m/%d/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

STATIC_URL = '/media/'
STATICFILES_DIRS = (
   # Put strings here, like "/home/html/static" or "C:/www/django/static".
   # Always use forward slashes, even on Windows.
   # Don't forget to use absolute paths, not relative paths.
   os.path.join(PROJECT_PATH, 'media'),                 
)

LOGIN_URL = '/login/'
LOGOUT_URL = '/'
PERMISSION_DENIED_URL = '/denied/'

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'dg.urls'

# Google ID is required for fetching the user profile image
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = [ ('id', 'id'), ('picture', 'picture') ]

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'templates'),
    os.path.join(PROJECT_PATH, 'templates/output'),
    os.path.join(PROJECT_PATH, 'templates/static_site'),
    os.path.join(PROJECT_PATH, 'templates/farmerbook'),
    os.path.join(PROJECT_PATH, 'media/coco/app'),
    os.path.join(PROJECT_PATH, 'templates/social_website'),
    os.path.join(PROJECT_PATH, 'templates/deoanalytics'),
	os.path.join(PROJECT_PATH, 'media/'),
    os.path.join(PROJECT_PATH, 'templates/xl_import')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'django.contrib.messages.context_processors.messages',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    #'django.contrib.sites',
    'django.contrib.admindocs',
    'dashboard',
    'programs',
    'geographies',
    'people',
    'videos',
    'activities',
    #'debug_toolbar',
    'output',
    'django.contrib.humanize',
    'south',
    'farmerbook',
    #'video_practice_map',
    #'path',
    'fbconnect',
    'dimagi',
    'tastypie',
    'coco',
    'social_website',
    'social.apps.django_app.default',
    'communications',
    'human_resources',
    'feeds',
    'deoanalytics',
    'xl_import',
    'progressbarupload',
)
#File upload handlers
    
#following line makes sessionid cookie accessible to in-browser javascript
SESSION_COOKIE_HTTPONLY = False

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth',
    'social.backends.google.GoogleOAuth2',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] [%(name)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_PATH, 'media/social_website/uploads/log/logfile'),
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'social_website': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
        'dashboard': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
        },
    }
}
