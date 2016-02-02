
"""
Minimal log server, as Django app
"""

from django.core.exceptions import ImproperlyConfigured


try:
	from ipware.ip import get_ip
except:
	raise ImproperlyConfigured('For minimal_log_host you need to install "django-ipware" (you can use pip).')


