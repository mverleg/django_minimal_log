
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf.urls import url
from .views import add_log_entry, list_log, resolve_log_entry, resolve_all_log_entries


urlpatterns = [
   url(r'^add/$', add_log_entry, name='minimal_log_add_entry'),
   url(r'^list/$', list_log, name='minimal_log_list'),
   url(r'^resolve/$', resolve_log_entry, name='minimal_log_resolve'),
   url(r'^resolve/all/$', resolve_all_log_entries, name='minimal_log_resolve_all'),
   url(r'^$', lambda request: HttpResponseRedirect(reverse('minimal_log_list'))),
]


