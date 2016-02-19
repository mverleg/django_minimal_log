
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from ipware.ip import get_ip
from .models import MinimalLogEntry, MinimalLogKey


@csrf_exempt
def add_log_entry(request):
	if request.method == 'POST':
		note = ''
		if not request.POST:
			return HttpResponse('POST data did not arrive; was there a redirect?', status=400)
		if not 'status' in request.POST:
			status = request.POST['status']
			note += ' used status "info" since status was not provided;'
		elif not len(request.POST['status']):
			status = request.POST['status']
			note += ' used status "info" since status was empty;'
		elif request.POST['status'] in all_statuses:
			status = request.POST['status']
		else:
			return HttpResponse('status "{0:s}" is not valid (choose one of {1:s})'.format(request.POST['status'],
				', '.join(s for s in all_statuses)), status=400)
		if 'message' in request.POST and len(request.POST['message']) >= 3:
			message = request.POST['message']
		elif 'description' in request.POST and len(request.POST['description']) >= 3:
			message = request.POST['description']
			note += ' note that "description" has been replaced by "message";'
		else:
			return HttpResponse('POST data did not contain a message or message too short', status=400)
		if not 'key' in request.POST:
			return HttpResponse('POST data did not contain a key', status=401)
		try:
			key = MinimalLogKey.objects.get(value=request.POST['key'])
		except MinimalLogKey.DoesNotExist:
			return HttpResponse('the key "{0:s}" is not valid'.format(request.POST['key']), status=401)
		if not key.active:
			return HttpResponse('the key "{0:s}" has been revoked'.format(request.POST['key']), status=401)
		entry = MinimalLogEntry(description=message, status=status, from_ip=get_ip(request), key=key)
		entry.save()
		extra_params = set(request.POST.keys()) - {'status', 'description', 'message', 'key'}
		if extra_params:
			note += ' you provided extra param(s) {0:s} which are redundant'.format(', '.join(s for s in extra_params))
		return HttpResponse('{0:s} added{1:s}'.format(entry.status,
			('; {0:s}\n'.format(note.strip()) if note else '\n')))
	keys = []
	if request.user.is_staff:
		keys = MinimalLogKey.objects.filter(active=True)
	return render(request, 'minimal_log/add_entry.html', {
		'MINIMAL_LOG_TEMPLATE': settings.MINIMAL_LOG_TEMPLATE,
		'statuses': MinimalLogEntry.STATUS_OPTIONS,
		'keys': keys,
	})


def permission_denied(request, action):
	return render(request, 'minimal_log/permission_denied.html', {
		'MINIMAL_LOG_TEMPLATE': settings.MINIMAL_LOG_TEMPLATE,
		'LOGIN_URL': settings.LOGIN_URL,
		'action': action,
	})


def list_log(request):
	"""
		GET parameters (all optional):

		:param page [int]: page number
		:param show [str,str,*]: the types of messages to show
		:param resolved: show resolved messages [no argument]
	"""
	if not (request.user.has_perm('minimal_log_host.change_logentry')):
		return permission_denied(request, 'view')
	entries_list, unresolved_count, show_statuses, show_sources, show_resolved = filtered_entries(
		statuses=request.GET.get('show', ''),
		sources=request.GET.get('from', ''),
		resolved='resolved' in request.GET,
	)
	paginator = Paginator(entries_list, 20)
	page = request.GET.get('page')
	try:
		entries = paginator.page(page)
	except PageNotAnInteger:
		entries = paginator.page(1)
	except EmptyPage:
		entries = paginator.page(paginator.num_pages)
	return render(request, 'minimal_log/list.html', {
		'MINIMAL_LOG_TEMPLATE': settings.MINIMAL_LOG_TEMPLATE,
		'entries': entries,
		'show_sources': ','.join(str(src) for src in sorted(show_sources)),
		'show_statuses': ','.join(show_statuses),
		'show_resolved': show_resolved,
		'pagenr': entries.number,
		'unresolved_count': unresolved_count,
	})


def resolve_log_entry(request):
	if not request.method == 'POST':
		messages.error(request, 'Log entry was not resolved (the request did not have POST data).')
		return redirect(reverse('minimal_log_list'), permanent=False)
	if not (request.user.has_perm('minimal_log_host.change_logentry')):
		return permission_denied(request, 'resolve')
	try:
		entry = MinimalLogEntry.objects.get(pk=int(request.POST['entry']))
	except ValueError:
		return HttpResponse('key "{0:s}" is not an integer'.format(request.POST['entry']))
	except KeyError:
		return HttpResponse('no entry provided')
	except MinimalLogEntry.DoesNotExist:
		return HttpResponse('entry with key "{0:s}" not found'.format(request.POST['entry']))
	action = request.POST.get('action', None)
	if action not in ('resolve', 'unresolve',):
		return HttpResponse('action should be "[un]resolve", not "{0:s}"'.format(action))
	if action == 'resolve':
		entry.resolved = now()
		entry.solver = request.user
		messages.success(request, 'Log entry #{0:d} was resolved.'.format(entry.pk))
	else:
		entry.resolved = None
		entry.solver = None
		messages.success(request, 'Log entry #{0:d} was marked as not resolved.'.format(entry.pk))
	entry.save()
	if request.POST.get('next', None):
		return redirect(to=request.POST['next'], permanent=False)
	return redirect(to=reverse('minimal_log_list'), permanent=False)


def resolve_all_log_entries(request):
	if not request.method == 'POST':
		messages.error(request, 'Log entries were not resolved (the request did not have POST data).')
		return redirect(reverse('minimal_log_list'), permanent=False)
	if not (request.user.has_perm('minimal_log_host.change_logentry')):
		return permission_denied(request, 'resolve')
	entries_list, unresolved_count, show_statuses, show_sources, show_resolved = filtered_entries(
		statuses=request.GET.get('show', ''),
		sources=request.GET.get('from', ''),
		resolved=False,
		sorted=False,
	)
	if not 'confirm' in request.POST and unresolved_count > 3:
		return render(request, 'minimal_log/confirm_resolve.html', {
			'MINIMAL_LOG_TEMPLATE': settings.MINIMAL_LOG_TEMPLATE,
			'count': unresolved_count,
			'next': request.POST.get('next', None),
		})
	entries_list.update(resolved=now(), solver=request.user)
	messages.success(request, '{0:d} log entries were resolved.'.format(unresolved_count))
	if request.POST.get('next', None):
		return redirect(to=request.POST['next'], permanent=False)
	return redirect(to=reverse('minimal_log_list'), permanent=False)


all_statuses = {item[0] for item in MinimalLogEntry.STATUS_OPTIONS}


def filtered_entries(statuses='', resolved=False, sources='', sorted=True):
	show_statuses = [item for item in statuses.split(',') if item in all_statuses]
	entries_list = MinimalLogEntry.objects.all()
	if show_statuses:
		entries_list = entries_list.filter(status__in=show_statuses)
	try:
		show_sources = set(int(source) for source in sources.split(','))
	except ValueError:
		show_sources = set()
	if show_sources:
		entries_list = entries_list.filter(key__pk__in=show_sources)
	unresolved_count = entries_list.filter(resolved__isnull=True).count()
	if not resolved:
		entries_list = entries_list.filter(resolved__isnull=True)
	if sorted:
		entries_list = entries_list.order_by('-added')
	return entries_list, unresolved_count, show_statuses, show_sources, resolved


