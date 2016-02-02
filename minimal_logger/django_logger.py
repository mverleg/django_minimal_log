
from sys import stderr
from logging import Handler
from .python_log import send_log, MinimalLogError, try_get_domain


class MinimalLogHandler(Handler):
	"""
	Sends log messages to minimal_log interface.
	"""

	level_map = {
		'CRITICAL': 'error',
		'ERROR': 'error',
		'WARNING': 'warn',
		'INFO': 'info',
		'DEBUG': 'info',
		'NOTSET': 'error',
	}

	def emit(self, record):
		message = '{0:s} {1:s}: {2:s}'.format(try_get_domain(), record.request.path, record.getMessage())
		status = self.level_map[record.levelname]
		try:
			send_log(message=message, status=status)
		except MinimalLogError as err:
			stderr.write('!! LOGGING ERROR: {0:s}'.format(str(err)))


