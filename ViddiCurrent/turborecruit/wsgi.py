"""
WSGI config for turborecruit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

#activate_this = 'C:/Users/developer/Envs/turbo/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read(),dict(__file__=activate_this))

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/Users/developer/Envs/turbo/Lib/site-packages')




# Add the app's directory to the PYTHONPATH
sys.path.append('C:/Apache24/htdocs/turborecruit')
sys.path.append('C:/Apache24/htdocs/turborecruit/turborecruit')

os.environ['DJANGO_SETTINGS_MODULE'] = 'turborecruit.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turborecruit.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
