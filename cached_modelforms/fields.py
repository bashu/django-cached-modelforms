# -*- coding:utf-8 -*-
from django.forms import Field, ChoiceField, MultipleChoiceField
from django.utils.encoding import smart_unicode
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError


class ModelChoiceField(ChoiceField):
    def __init__(self, objects=(), empty_label=u"---------", required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        choices = [(smart_unicode(x.pk), smart_unicode(x)) for x in objects]
        self.objects = dict((smart_unicode(x.pk), x) for x in objects)
        if self.empty_label is not None:
            choices.insert(0, (u'', self.empty_label))
        super(ModelChoiceField, self).__init__(choices=choices,
                                               required=required,
                                               widget=widget, label=label,
                                               initial=initial,
                                               help_text=help_text,
                                               *args, **kwargs)

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        value = smart_unicode(value)
        if value not in self.objects:
            raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})
        return self.objects[value]

    def validate(self, value):
        return Field.validate(self, value)

class ModelMultipleChoiceField(ModelChoiceField):
    hidden_widget = MultipleChoiceField.hidden_widget
    widget = MultipleChoiceField.widget
    default_error_messages = MultipleChoiceField.default_error_messages

    def __init__(self, objects=(), required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        super(ModelMultipleChoiceField, self).__init__(objects, None, required,
                                                       widget, label, initial,
                                                       help_text, *args,
                                                       **kwargs)

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'])
        return [self.objects[x] for x in value]