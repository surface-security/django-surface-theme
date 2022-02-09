from django import forms
from django.conf import settings


class DatePickerInput(forms.DateInput):
    template_name = 'widgets/datepicker.html'
    prefix = 'datepicker'

    def get_context(self, name, value, attrs):
        picker_id = f'{self.prefix}_{name}'
        if attrs is None:
            attrs = dict()
        attrs['data-target'] = f'#{picker_id}'
        attrs['class'] = f'form-control {self.prefix}-input'
        attrs['maxlength'] = '200'
        context = super().get_context(name, value, attrs)
        context['widget'][f'{self.prefix}_id'] = picker_id
        return context

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        return forms.Media(
            css={'all': ('components/tempusdominus-bootstrap-4/build/css/tempusdominus-bootstrap-4.min.css',)},
            js=('components/tempusdominus-bootstrap-4/build/js/tempusdominus-bootstrap-4.min.js',),
        )


class DateTimePickerInput(DatePickerInput):
    format_key = 'DATETIME_INPUT_FORMATS'
    template_name = 'widgets/datetimepicker.html'
    prefix = 'datetimepicker'
