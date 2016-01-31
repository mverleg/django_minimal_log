
Django Minimal Log
---------------------------------

A very minimal logging server and client for Django. The client can also be replaced by anything that can do send POST requests.

It has a minimal feature set:

- Register as a Django logging handler.
- Log events, which can have a message, a source and a level.
- Show logged messages, filtered by level.
- Resolve messages to remove them from the list (can be undone).
- Use secret keys as authentication to prevent unauthorized logs.
- Easily log from multiple sources and revoke keys for specific sources.

That's about it! If you want fancy graphs and more than 3 minutes of setup, maybe try Sentry.

License
---------------------------------

django_minimal_log is available under the revised BSD license, see LICENSE.txt. You can do anything as long as you include the license, don't use my name for promotion and are aware that there is no warranty.

Enhancements through pull requests are also most welcome.


