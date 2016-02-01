
from sys import stderr
from django.conf import settings
from django.contrib.sites.models import Site
from os.path import basename
from requests import post
from logging import Handler, NOTSET


class MinimalLogHandler(Handler):
	"""
	Sends log messages to minimal_log interface.
	"""
	def __init__(self, logging_url, auth_key=None, source_name=None, level=NOTSET):
		super(MinimalLogHandler, self).__init__(level=level)
		self.logging_url = logging_url
		if not auth_key:
			auth_key = settings.YU4LOG_AUTH_KEY
		self.auth_key = auth_key
		if source_name is None:
			source_name = getattr(settings, 'BASE_DIR', None)
			if source_name is None:
				source_name = 'unknown-django-project'
			else:
				source_name = basename(source_name)
		self.source_name = source_name
		self.level_map = {
			'CRITICAL': 'error',
			'ERROR': 'error',
			'WARNING': 'warn',
			'INFO': 'info',
			'DEBUG': 'info',
			'NOTSET': 'error',
		}

	def try_get_domain(self):
		try:
			domain = Site.objects.get_current().domain
		except:
			pass
		else:
			if not 'example' in domain:
				return domain
		dr = getattr(settings, 'BASE_DIR', None)
		if dr:
			return basename(dr)
		return 'unknown-django-project'

	def emit(self, record):
		description = '{0:s} {1:s}: {2:s}'.format(self.try_get_domain(), record.request.path, record.getMessage())
		data = dict(
			source=self.source_name,
			key=self.auth_key,
			description=description,
			status=self.level_map[record.levelname],
		)
		res = post(url=self.logging_url, data=data)
		if res.status_code != 200:
			stderr.write('!! LOGGING ERROR: got {0:}: {1:} when sending log to {2:s} (error was "{3:}")'
				.format(res.status_code, res.content, self.logging_url, record.getMessage()))


