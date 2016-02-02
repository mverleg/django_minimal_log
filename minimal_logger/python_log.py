
from django.conf import settings
from os.path import basename
from requests import post


class MinimalLogError(Exception):
	pass


def try_get_domain():
	from django.contrib.sites.models import Site
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


def send_log(message, key=None, url=None, status='error', check_status=True):
	if key is None:
		assert hasattr(settings, 'MINIMAL_LOG_AUTH_KEY'), \
			'send_log did not get a key and could not find one in Django settings (MINIMAL_LOG_AUTH_KEY)'
		key = settings.MINIMAL_LOG_AUTH_KEY
	if url is None:
		assert hasattr(settings, 'MINIMAL_LOG_URL'), \
			'send_log did not get a url and could not find one in Django settings (MINIMAL_LOG_URL)'
		url = settings.MINIMAL_LOG_URL
	if check_status:
		assert status in ('good', 'info', 'warn', 'error',), 'not a valid status (provide check_status=False to overrule)'
	data = dict(
		key=key,
		message=message,
		status=status,
	)
	res = post(url=url, data=data)
	if res.status_code != 200:
		raise MinimalLogError('Got {0:}: {1:} when sending log to {2:s} (error was "{3:}")'
			.format(res.status_code, res.content, url, message))


