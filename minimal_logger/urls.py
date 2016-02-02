
from django.conf.urls import patterns, url
from minimal_logger.views_javascript import receive_log


urlpatterns = patterns('',
   url(r'^receive_js_log', receive_log, name ='minimal_log_receive_js_log'),
)


