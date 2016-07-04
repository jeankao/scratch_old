from base import *

LOCAL_SETTINGS_LOADED = True

DEBUG = True

INTERNAL_IPS = ('127.0.0.1', )

ADMINS = (
    ('admin', 'koma@mail.nksh.tp.edu.tw'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'scratch',
        'USER': 'scratch',
        'PASSWORD': '1234',
        'HOST': 'localhost',
    }
}