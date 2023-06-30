"""
WSGI config for efastmister project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from EFastMisterApp.views import iniciar_programador

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efastmister.settings')

application = get_wsgi_application()

# ? INICIAR PROGRAMADOR PARA LA GENERACIÓN DE JUGADORES Y CHEQUEO DE PUJAS
iniciar_programador()
