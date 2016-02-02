
from time import time
from urllib.parse import urlencode
from django.conf import settings
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from os.path import join, dirname
from re import sub


signer = Signer()


def minimal_javascript_log(request):
	"""
	Create the url that javascript logs can be sent to. There's no way to prevent the client from sending fake log
	files, since any credentials must be in the code. But the damage can be limited by requiring csrf/signed value
	(so only the actual client) and timestamp (so they can only send logs for a limited time), rather than giving
	them direct access to the logging server.
	"""
	url = reverse('minimal_log_receive_js_log')
	if settings.APPEND_SLASH and not url.endswith('/'):
		url += '/'
	params = urlencode({
		'csrfmiddlewaretoken': get_token(request),
		'request_time': signer.sign('{0:.0f}'.format(time()))
	})
	with open(join(dirname(__file__), 'js_handler.html')) as fh:
		code = fh.read().strip()
		code = sub(r'{{\s*MINIMAL_LOG_JS_URL\s*}}',    url,    code)
		code = sub(r'{{\s*MINIMAL_LOG_JS_PARAMS\s*}}', params, code)
	return {
		'MINIMAL_LOG_JS_URL': mark_safe(url),
		'MINIMAL_LOG_JS_PARAMS': mark_safe(params),
		'MINIMAL_LOG_JAVASCRIPT_HANDLING_CODE': mark_safe(code),
	}


