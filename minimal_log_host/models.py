
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.timesince import timesince
from django.utils.timezone import now
from .utils import generate_key


class MinimalLogKey(models.Model):

	description = models.CharField(max_length=128,  help_text='Describe the service uses this key. It\'s best to generate a new key ' +
		'for each service so that you can easily revoke individual ones.', validators=[MinLengthValidator(3)])
	value = models.CharField(max_length=64, default=generate_key, unique=True,
		help_text='Secret key used as authentication token (keep it secret!).')
	active = models.BooleanField(default=True, help_text='Turn this off to disable the key.')
	added = models.DateTimeField(auto_now_add=True)
	adder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	def __str__(self):
		return (self.description or '[no description]') + ' ...{0:s}'.format(self.key_end())

	def __unicode__(self):
		return self.__str__()

	def key_end(self):
		return self.value[-4:]

	def last_used(self):
		entries = MinimalLogEntry.objects.filter(key=self).order_by('-added')
		if entries:
			return timesince(entries[0].added) + ' ago'
		return None

	class Meta:
		verbose_name = 'key'


class MinimalLogEntry(models.Model):
	STATUS_OPTIONS = (('good', 'success'), ('info', 'info'), ('warn', 'warning'), ('error', 'error'))

	description = models.TextField(help_text='Describe the problem, change, situation or event.')
	status = models.CharField(max_length=8, choices=STATUS_OPTIONS, help_text='What kind of situation is this?')
	added = models.DateTimeField(auto_now_add=True)
	from_ip = models.CharField(max_length=16, null=True)
	key = models.ForeignKey(MinimalLogKey, help_text='Key used to authenticate this log entry.', null=True, on_delete=models.SET_NULL)
	resolved = models.DateTimeField(default=None, null=True, blank=True)
	solver = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return '{0:s} {1:s}'.format((self.get_status_display() or '').upper(),
			self.description[:60] + ('...' if len(self.description) > 60 else ''))

	def __unicode__(self):
		return self.__str__()

	def key_end(self):
		return self.key.key_end()

	def resolve(self, request):
		if self.resolved is not None:
			raise AssertionError('log entry %s is already resolved' % self.pk)
		self.resolved = now()
		self.solver = request.user
		self.save()

	def unresolve(self, request):
		if self.resolved is None:
			raise AssertionError('log entry %s is not resolved' % self.pk)
		assert request.user.is_authenticated()
		self.resolved = None
		self.solver = None
		self.save()

	class Meta:
		verbose_name = 'entry'
		verbose_name_plural = 'entries'


