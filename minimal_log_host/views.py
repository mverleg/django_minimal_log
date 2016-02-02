from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from ipware.ip import get_ip
from .models import MinimalLogEntry, MinimalLogKey

statuses = {item[0] for item in MinimalLogEntry.STATUS_OPTIONS}


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
		elif request.POST['status'] in statuses:
			status = request.POST['status']
		else:
			return HttpResponse('status "{0:s}" is not valid (choose one of {1:s})'.format(request.POST['status'],
				', '.join(s for s in statuses)), status=400)
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
		return HttpResponse('{0:s} added'.format(entry.status) +
			('; {0:s}\n'.format(note.strip()) if note else '\n'))
	keys = []
	if request.user.is_staff:
		keys = MinimalLogKey.objects.filter(active=True)
	return render(request, 'minimal_log/add_entry.html', {
		'MINIMAL_LOG_TEMPLATE': settings.MINIMAL_LOG_TEMPLATE,
		'statuses': MinimalLogEntry.STATUS_OPTIONS,
		'keys': keys,
	})


@staff_member_required
def list_log(request):
	"""
		GET parameters (all optional):

		:param page [int]: page number
		:param show [str,str,*]: the types of messages to show
		:param resolved: show resolved messages [no argument]
	"""
	show = [item for item in request.GET.get('show', '').split(',') if item in statuses]
	query = MinimalLogEntry.objects.all()
	if show:
		query = query.filter(status__in=show)
	show_query = query
	show_resolved = 'resolved' in request.GET
	if not show_resolved:
		query = query.filter(resolved__isnull=True)
	entries_list = query.order_by('-added')
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
		'show': ','.join(show),
		'show_resolved': show_resolved,
		'pagenr': entries.number,
		'unresolved_count': show_query.filter(resolved__isnull=True).count(),
	})


@staff_member_required
def resolve_log_entry(request):
	try:
		entry = MinimalLogEntry.objects.get(pk=int(request.POST['entry']))
	except ValueError:
		return HttpResponse('key "%s" is not an integer' % request.POST['entry'])
	except KeyError:
		return HttpResponse('no entry provided')
	except MinimalLogEntry.DoesNotExist:
		return HttpResponse('entry with key "%s" not found' % request.POST['entry'])
	action = request.POST.get('action', None)
	if action not in ('resolve', 'unresolve',):
		return HttpResponse('action should be "[un]resolve", not "%s"' % action)
	if action == 'resolve':
		entry.resolved = now()
		entry.solver = request.user
	else:
		entry.resolved = None
		entry.solver = None
	entry.save()
	url = reverse('minimal_log_list') + '?'
	show = [item for item in request.GET.get('show', '').split(',') if item in statuses]
	if show:
		url += 'show=' + ','.join(show) + '&'
	if 'resolved' in request.GET:
		url += 'resolved&'
	page = int(request.GET.get('page', 1))
	if page > 1:
		url += 'page=' + str(page)
	return redirect(to=url.rstrip('?'))


@staff_member_required
def resolve_all_log_entries(request):
	#todo: check change permission?
	show = [item for item in request.GET.get('show', '').split(',') if item in statuses]
	query = MinimalLogEntry.objects.filter(resolved__isnull=True)
	if show:
		query = query.filter(status__in=show)
	unresolved_entries_count = query.count()
	if not 'confirm' in request.GET and unresolved_entries_count > 3:
		return render(request, 'minimal_log/confirm_resolve.html', {
			'MINIMAL_LOG_TEMPLATE': settings.MINIMAL_LOG_TEMPLATE,
			'count': unresolved_entries_count
		})
	entries_list = query.order_by('-added')
	entries_list.update(resolved=now(), solver=request.user)
	url = reverse('minimal_log_list') + '?'
	if show:
		url += 'show=' + ','.join(show) + '&'
	if 'resolved' in request.GET:
		url += 'resolved&'
	return redirect(to=url.rstrip('?'))


