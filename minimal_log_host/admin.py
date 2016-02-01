
from django.contrib import admin
from django.forms import ModelForm
from .models import MinimalLogKey, MinimalLogEntry


class LogKeyAdminForm(ModelForm):
	"""
	Voodoo to make sure 'adder' is always the user who added or changed the object.
	"""
	def save(self, commit=True, **kwargs):
		instance = super(LogKeyAdminForm, self).save(commit=False, **kwargs)
		instance.adder = self.current_user
		instance.save()
		return instance


class LogKeyAdmin(admin.ModelAdmin):
	readonly_fields = ('added', 'adder', 'last_used',)
	list_display = ('description', 'key_end', 'added', 'adder', 'active', 'last_used',)
	list_display_links = ('description', 'key_end')

	form = LogKeyAdminForm

	def get_form(self, request, obj=None, **kwargs):
		"""
		More voodoo to set 'adder'.
		"""
		form = super(LogKeyAdmin, self).get_form(request, obj, **kwargs)
		form.current_user = request.user
		return form


class LogEntryAdmin(admin.ModelAdmin):
	readonly_fields = ('added', 'from_ip',)
	list_display = ('status', 'description', 'added', 'resolved',)


admin.site.register(MinimalLogKey, LogKeyAdmin)
admin.site.register(MinimalLogEntry, LogEntryAdmin)


