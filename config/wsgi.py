"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# touched on 2025-05-27T15:28:48.236340Z
# touched on 2025-05-27T15:28:53.860532Z
# touched on 2025-05-27T15:29:02.326165Z