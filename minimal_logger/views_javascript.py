
from time import time
from django.conf import settings
from django.core.signing import Signer, BadSignature
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from ipware.ip import get_ip
from .python_log import send_log, try_get_domain, MinimalLogError


signer = Signer()
IP_LOG_COUNTER = {}


@require_POST
def receive_log(request, key_lifetime=5*60, per_ip_limit=7, silence_in_debug_mode=True):
	params = {'request_time', 'message', 'csrfmiddlewaretoken'}
	for key in request.POST.keys():
		if key not in params:
			return HttpResponse('unknown parameter "{0:s}"'.format(key), status=400)
	for param in params:
		if param not in request.POST:
			return HttpResponse('parameter "{0:s}" is required'.format(param), status=400)
	try:
		request_time = int(signer.unsign(request.POST['request_time']))
	except BadSignature:
		return HttpResponse('the time signature is not valid'.format(request.POST['key']), status=401)
	if request_time > time() + key_lifetime:
		return HttpResponse('this logging key has expired', status=401)
	ip = get_ip(request)
	message = 'javascript at {0:s} from {2:s}: \n{1:s}'.format(
		try_get_domain(), request.POST['message'][:2048], ip)
	ip_time_hash = '{0:s} {1:d}'.format(ip, int(time() / (60*60*12)))
	if ip_time_hash not in IP_LOG_COUNTER:
		IP_LOG_COUNTER[ip_time_hash] = 1
	IP_LOG_COUNTER[ip_time_hash] += 1
	if IP_LOG_COUNTER[ip_time_hash] > per_ip_limit:
		return HttpResponse('silently ignored due to flooding', status=200)
	if settings.DEBUG and silence_in_debug_mode:
		return HttpResponse('error report discarded because of debug mode', status=200)
	try:
		send_log(message, status='error')
	except MinimalLogError:
		return HttpResponse('there was a server problem while storing the report', status=400)
	else:
		return HttpResponse('ok', status=200)


