# -*- coding:utf-8 -*-
'''
Fields.
'''

from django.forms import Field, ChoiceField, MultipleChoiceField
from django.utils.encoding import smart_unicode
from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError


class CachedModelChoiceField(ChoiceField):
    '''
    ``ModelChoiceField`` that accepts ``objects`` argument.

    ``objects`` can be:
      * a list (or any iterable) or objects, e.g. ``[obj1, obj2, ...]``
      * a list (or any iterable) of tuples: ``[(obj1.pk, obj1), (obj2.pk, obj2), ...]``
      * a dict: ``{obj1.pk: obj1, obj2.pk: obj2, ...}``

    It doesn't accept ``to_field_name`` argument.
    '''
    def __init__(self, objects=(), empty_label=u"---------", required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        if required and (initial is not None):
            self.empty_label = None
        else:
            self.empty_label = empty_label
        if callable(objects):
            objects = objects()
        self.objects = objects
        super(CachedModelChoiceField, self).__init__(
            choices=self.choices,
            required=required,
            widget=widget,
            label=label,
            initial=initial,
            help_text=help_text,
            *args,
            **kwargs
        )

    @property
    def objects(self):
        return self._objects.copy()

    @objects.setter
    def objects(self, value):
        if isinstance(value, dict):
            self._objects = dict(
                (smart_unicode(k), v) for k, v in value.iteritems()
            )
            self.choices = [(x, smart_unicode(self._objects[x]))
                            for x in sorted(self._objects.keys())]
        else:
            objects = list(value)
            if objects:
                if isinstance(objects[0], (list, tuple)):
                    self._objects = dict(
                        (smart_unicode(k), v) for k, v in objects
                    )
                    self.choices = [(smart_unicode(k), smart_unicode(v))
                                    for k, v in objects]
                else:
                    self._objects = dict(
                        (smart_unicode(x.pk), x) for x in objects
                    )
                    self.choices = [(smart_unicode(x.pk), smart_unicode(x))
                                    for x in objects]
            else:
                self._objects = {}
                self.choices = ()
        if self.empty_label is not None:
            self.choices.insert(0, (u'', self.empty_label))

    def to_python(self, value):
        if value in EMPTY_VALUES:
            return None
        value = smart_unicode(value)
        if value not in self.objects:
            raise ValidationError(
                self.error_messages['invalid_choice'] % {'value': value}
            )
        return self.objects[value]

    def validate(self, value):
        return Field.validate(self, value)

class CachedModelMultipleChoiceField(CachedModelChoiceField):
    '''
    ``ModelMultipleChoiceField`` that accepts ``objects`` argument.

    ``objects`` can be:
      * a list (or any iterable) or objects, e.g. ``[obj1, obj2, ...]``
      * a list (or any iterable) of tuples: ``[(obj1.pk, obj1), (obj2.pk, obj2), ...]``
      * a dict: ``{obj1.pk: obj1, obj2.pk: obj2, ...}``

    It doesn't accept ``to_field_name`` argument.
    '''
    hidden_widget = MultipleChoiceField.hidden_widget
    widget = MultipleChoiceField.widget
    default_error_messages = MultipleChoiceField.default_error_messages

    def __init__(self, objects=(), required=True,
                 widget=None, label=None, initial=None, help_text=None,
                 *args, **kwargs):
        super(CachedModelMultipleChoiceField, self).__init__(
            objects,
            None,
            required,
            widget,
            label,
            initial,
            help_text,
            *args,
            **kwargs
        )

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'])
        try:
            result = [self.objects[x] for x in value]
        except KeyError:
            raise ValidationError(
                self.error_messages['invalid_choice'] % {'value': value}
            )
        return result
