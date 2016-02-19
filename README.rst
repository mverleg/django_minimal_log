
Django Minimal Log
---------------------------------

A very minimal logging server and client for Django. The client can also be replaced by anything that can do send POST requests.

It has a minimal feature set:

- Register as a Django logging handler.
- Register as a Javascript logging handler (in combination with Django).
- Log events, which can have a message, a source, a level and a time.
- Show logged messages, which you can filter by level.
- Resolve messages to remove them from the list (can be undone).
- Use secret keys as authentication to prevent unauthorized logs.
- Easily log from multiple sources and revoke keys for specific sources.
- Add log messages by hand from the server interface if needed.
- Logs some meta info, like who resolved an entry and which IP submitted it.

That's about it! If you want fancy graphs and more than 3 minutes of setup, maybe try Sentry.

Server and clients
---------------------------------

You need to have a running, reachable host that logs are sent to. Besides that, you can have any number of programs that report events to this host.

It is not advisable to have the host and clients running in the same project. In that case, if the client is having a problem it wants to report, chances are the host is having the same problem, and won't register the event.

For either one, you will need to have Django and you will need to install install minimal-log::

	pip install django-minimal-log

This will also install ``requests`` and ``django-ipware``.

Server
=================================

The logging server is a Django app. You can either add it to an existing project (not one of the ones you want to log) or create a new project.

After finding or creating a suitable project, make a few changes. (Make sure ``django-minimal-log`` is installed).

In ``settings.py``, add ``minimal_log_host`` to apps (position doesn't matter)::

	INSTALLED_APPS = (
		# other apps
		'minimal_log_host',
	)

You should also define the template that minimal-logs extends when displaying logs. It should contain a ``{% block content %}``::

    MINIMAL_LOG_TEMPLATE = 'my_base_template.html'

In ``urls.py``, choose a base url (``/log/`` in this example)::

	# import minimal_log_host.urls
	url(r'^log/', include(minimal_log_host.urls)),

Now you can go to your admin site and find two models: keys (for authentication) and entries (logged events). You should create a key through the admin for each project that you want to receive logs from.

That's all for the server! You'll need the keys you generated to configure clients.

You can also go to the url you chose, look around and add test entries. If you want to test logging from an external program, have a look at Bash below.

Clients - Django
=================================

Update your settings by adding some details about the logging server (update both values)::

	# this is the key you generated on your server's admin panel before
	MINIMAL_LOG_AUTH_KEY = 'DXKIrRzSmo81QTnmaWhMkg7U8ndqtux5'
	# make sure there will be no redirect, e.g. www and slash should be correct
	MINIMAL_LOG_URL = 'https://example.com/log/add/'

and add these values at the appropriate places in the ``LOGGING`` dictionary::

	LOGGING = {
		# other settings
		'handlers': {
			# other handlers
			'minimallog': {
				'level': 'WARNING',
				'class': 'minimal_logger.MinimalLogHandler',
				'formatter': 'verbose',
			}
		},
		'loggers': {
			# other loggers
			'django': {
				'handlers': ['minimallog',],  # other handlers
				'level': 'WARNING',
				'propagate': True,
			},
		}
	}

A working version of ``LOGGING`` might look like this::

	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'formatters': {
			'verbose': {'format': '%(levelname)s %(asctime)s %(module)s %(message)s'},
			'simple': {'format': '%(levelname)s %(message)s'},
		},
		'filters': {
			'require_debug_true': {
				'()': 'django.utils.log.RequireDebugTrue',
			},
		},
		'handlers': {
			'console': {
				'level': 'INFO',
				'filters': ['require_debug_true'],
				'class': 'logging.StreamHandler',
			},
			'minimallog': {
				'level': 'WARNING',
				'class': 'minimal_logger.MinimalLogHandler',
				'formatter': 'verbose',
			}
		},
		'loggers': {
			'django': {
				'handlers': ['console', 'minimallog',],
				'level': 'WARNING',
				'propagate': True,
			},
		}
	}

That's it!

Clients - Javascript (with Django)
=================================

You can also log javascript errors (only the ones that trigger ``window.onerror``). They will be sent to your site and then forwarded to the logging server after filtering.

Realize that there is no way to log javascript errors without giving a malicious visitor the ability to send fake logs. Any credentials you protect your logging server with will have to be sent to the client, where they can be extracted. ``django_minimal_log`` helps you with this by accepting only logs from recent requests (using signed timestamps) with csrf protection, by trimming entries that are too long and by blocking too many entries from a single IP address. But fake log entries always remain possible.

To log javascript errors, you will need to add this to settings (which is already done if you set up the Django client)::

	# this is the key you generated on your server's admin panel before
	MINIMAL_LOG_AUTH_KEY = 'DXKIrRzSmo81QTnmaWhMkg7U8ndqtux5'
	# make sure there will be no redirect, e.g. www and slash should be correct
	MINIMAL_LOG_URL = 'https://example.com/log/add/'

You will also need to add a template context processor::

	TEMPLATES = [
		{
			# more settings here
			'OPTIONS': {
				'context_processors': [
					# other context processors
					'minimal_logger.context.minimal_javascript_log',
				],
				'loaders': [
					# loaders here
				],
			},
		},
	]

In ``urls.py``, add::

	# import minimal_logger.urls
	url(r'^log/', include(minimal_logger.urls)),

And finally, add the logging code to ant template for which you want logging, by adding::

	{{ MINIMAL_LOG_JAVASCRIPT_HANDLING_CODE }}

Alternatively you can also have a look at ``minimal_logger/js_handler.html`` and copy-paste the (changed) code, it's pretty short. You will still need the context processor.

THe javascript for logging should appear above any other javascript code, or it will not catch errors in their initialization.

Clients - Bash / general
=================================

Sending a log is simply a POST request, so you can use Bash or just about anything else::

	function send_log ()
	{
		curl --silent --show-error --request POST 'https://example.com/log/add/' \
			--data-urlencode "description=$2" --data-urlencode "status=warn" \
			--data-urlencode 'key=DXKIrRzSmo81QTnmaWhMkg7U8ndqtux5';
	}

If you write a logger client for something else, you're certainly welcome to suggest it for addition into the main minimal_log package.

License
---------------------------------

django_minimal_log is available under the revised BSD license, see LICENSE.txt. You can do anything as long as you include the license, don't use my name for promotion and are aware that there is no warranty.

Enhancements through pull requests are also most welcome.


