
Django Minimal Log
---------------------------------

A very minimal logging server and client for Django. The client can also be replaced by anything that can do send POST requests.

It has a minimal feature set:

- Register as a Django logging handler.
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

Server
=================================

url(r'^log/', include(minimal_log_host.urls)),

BASE_TEMPLATE, {% block content %}


Clients - Django
=================================



Clients - Bash
=================================



License
---------------------------------

django_minimal_log is available under the revised BSD license, see LICENSE.txt. You can do anything as long as you include the license, don't use my name for promotion and are aware that there is no warranty.

Enhancements through pull requests are also most welcome.


