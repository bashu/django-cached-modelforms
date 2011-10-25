# -*- coding:utf-8 -*-
from django.forms import Field, ChoiceField, MultipleChoiceField
from django.utils.encoding import smart_unicode
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError


class ModelChoiceField(ChoiceField):
    '''
    ModelChoiceField that accepts ``choices`` argument.

    ``choices`` can be:
      * a list (or any iterable) or objects, e.g. ``[obj1, obj2, ...]``
      * a list (or any iterable) of tuples: ``[(obj1.pk, obj1), (obj2.pk, obj2), ...]``
      * a dict: ``{obj1.pk: obj1, obj2.pk: obj2, ...}``

    It doesn't accept ``to_field_name`` argument.
    '''
    def __init__(self, choices=(), empty_label=u"---------", required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        if isinstance(choices, dict):
            self.objects = dict((smart_unicode(k), v) for k, v in choices.itervalues())
        else:
            choices = list(choices)
            if choices:
                if isinstance(choices[0], (list, tuple)):
                    self.objects = dict((smart_unicode(k), v) for k, v in choices)
                else:
                    self.objects = dict((smart_unicode(x.pk), x) for x in choices)
            else:
                self.objects = {}
        _choices = [(k, smart_unicode(v)) for k ,v in self.objects.itervalues()]
        if self.empty_label is not None:
            _choices.insert(0, (u'', self.empty_label))
        super(ModelChoiceField, self).__init__(choices=_choices,
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
    '''
    ModelMultipleChoiceField that accepts ``choices`` argument.

    ``choices`` can be:
      * a list (or any iterable) or objects, e.g. ``[obj1, obj2, ...]``
      * a list (or any iterable) of tuples: ``[(obj1.pk, obj1), (obj2.pk, obj2), ...]``
      * a dict: ``{obj1.pk: obj1, obj2.pk: obj2, ...}``

    It doesn't accept ``to_field_name`` argument.
    '''
    hidden_widget = MultipleChoiceField.hidden_widget
    widget = MultipleChoiceField.widget
    default_error_messages = MultipleChoiceField.default_error_messages

    def __init__(self, choices=(), required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        super(ModelMultipleChoiceField, self).__init__(choices, None, required,
                                                       widget, label, initial,
                                                       help_text, *args,
                                                       **kwargs)

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'])
        return [self.objects[x] for x in value]
