import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efastmister.settings')
django.setup()

from EFastMisterApp.views import iniciar_programador

#if __name__ == '__main__':
#    iniciar_programador()