
from django.forms import ModelForm
from minimal_log_host.models import MinimalLogEntry


class MinimalLogForm(ModelForm):
	#todo: not used anymore?

	class Meta:
		fields = ('description', 'status', 'key', )
		model = MinimalLogEntry

	def __init__(self, *args, **kwargs):
		"""
		Ugly-as-sin hack to add bootstrap class to each widget. But it's better than installing crispy-forms for one form.
		"""
		super(MinimalLogForm, self).__init__(*args, **kwargs)
		for field in self.fields.values():
			field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'


