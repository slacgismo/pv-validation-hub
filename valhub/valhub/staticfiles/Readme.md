# Static Root

This directory exists to be used with the STATIC_ROOT and STATIC_URL defined in settings.py.

The command ```python3 manage.py collectstatic``` is used to populate this directory with django's default stylesheets and static files.

This should only affect the admin view of the api when signing in. 
