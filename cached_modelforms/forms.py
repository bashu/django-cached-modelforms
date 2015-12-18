# -*- coding:utf-8 -*-
'''
The realisation of ``ModelForm`` that uses
``CachedModelChoiceField`` and ``CachedModelMultipleChoiceField`` from
fields.py

'''

from __future__ import unicode_literals

from django.utils.text import capfirst
from django.forms.util import ErrorList
from django.core.exceptions import FieldError
from django.forms.widgets import media_property
from django.db.models import ForeignKey, ManyToManyField
from django.forms.forms import BaseForm, get_declared_fields
from django.forms.models import BaseModelForm, ModelFormOptions, fields_for_model

from six import with_metaclass

from .fields import CachedModelChoiceField, CachedModelMultipleChoiceField


def make_formfield_callback(another_func, objects):
    '''
    Decorator that creates ``formfield_callback`` function (that makes
    ``ModelForm`` to use desired form field for certain model fields).

    If there is another ``formfield_callback`` defined, decorator
    will apply it too (for any field exept for ``ForeignKey`` and
    ``ManyToManyField``).
    '''
    def formfield_callback(f, **kwargs):
        if f.name in objects:
            kwargs['objects'] = ()
            kwargs.update({'required': not f.blank,
                           'label': capfirst(f.verbose_name),
                           'help_text': f.help_text})
            if isinstance(f, ForeignKey):
                return CachedModelChoiceField(**kwargs)
            elif isinstance(f, ManyToManyField):
                return CachedModelMultipleChoiceField(**kwargs)
        if another_func is not None:
            return another_func(f, **kwargs)
        else:
            return f.formfield(**kwargs)
    return formfield_callback


class CachedModelFormOptions(ModelFormOptions):
    '''
    ``ModelFormOptions`` version that also extracts ``objects`` param.
    '''
    def __init__(self, options=None):
        super(CachedModelFormOptions, self).__init__(options)
        self.objects = getattr(options, 'objects', None)
        self.m2m_initials = getattr(options, 'm2m_initials', None)


class CachedModelFormMetaclass(type):
    '''
    ``ModelFormMetaclass`` version that applies ``make_formfield_callback``
    decorator and passess ``opts.objects`` to it if neccessary.

    I had to do a lot of copy-pasting from ``ModelFormMetaclass``
    source, it's impossible (at least for me) to alter it desired way
    using ``super``.
    '''
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.pop('formfield_callback', None)
        try:
            parents = [b for b in bases if issubclass(b, ModelForm)]
        except NameError:
            # We are defining ModelForm itself.
            parents = None
        declared_fields = get_declared_fields(bases, attrs, False)
        new_class = super(CachedModelFormMetaclass, cls).__new__(
            cls, name, bases, attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = CachedModelFormOptions(getattr(new_class, 'Meta', None))
        if opts.objects:
            formfield_callback = make_formfield_callback(formfield_callback, opts.objects)
        if opts.model:
            # If a model is defined, extract form fields from it.
            fields = fields_for_model(opts.model, opts.fields,
                                      opts.exclude, opts.widgets, formfield_callback)
            # make sure opts.fields doesn't specify an invalid field
            none_model_fields = [k for k, v in list(fields.items()) if not v]
            missing_fields = set(none_model_fields) - set(declared_fields.keys())
            if missing_fields:
                message = 'Unknown field(s) (%s) specified for %s'
                message = message % (', '.join(missing_fields),
                                     opts.model.__name__)
                raise FieldError(message)
            # Override default model fields with any custom declared ones
            # (plus, include all the other declared fields).
            fields.update(declared_fields)
        else:
            fields = declared_fields
        new_class.declared_fields = declared_fields
        new_class.base_fields = fields
        return new_class


def model_to_dict(instance, fields=None, exclude=None, m2m_initials=None):
    """
    Returns a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, only the named
    fields will be included in the returned dict.

    ``exclude`` is an optional list of field names. If provided, the named
    fields will be excluded from the returned dict, even if they are listed in
    the ``fields`` argument.
    """
    # avoid a circular import
    from django.db.models.fields.related import ManyToManyField
    if m2m_initials is None:
        m2m_initials = {}
    opts = instance._meta
    data = {}
    for f in opts.fields + opts.many_to_many:
        if not f.editable:
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name not in exclude:
            continue
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primry key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[f.name] = []
            elif f.name in m2m_initials:
                data[f.name] = m2m_initials[f.name](instance)
            else:
                # MultipleChoiceWidget needs a list of pks, not object instances.
                data[f.name] = [obj.pk for obj in f.value_from_object(instance)]
        else:
            data[f.name] = f.value_from_object(instance)
    return data


class CachedBaseModelForm(BaseModelForm):

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        opts = self._meta
        if instance is None:
            if opts.model is None:
                raise ValueError('ModelForm has no model class specified.')
            # if we didn't get an instance, instantiate a new one
            self.instance = opts.model()
            object_data = {}
        else:
            self.instance = instance
            object_data = model_to_dict(instance, opts.fields, opts.exclude, opts.m2m_initials)
        # if initial was provided, it should override the values from instance
        if initial is not None:
            object_data.update(initial)
        # self._validate_unique will be set to True by BaseModelForm.clean().
        # It is False by default so overriding self.clean() and failing to call
        # super will stop validate_unique from being called.
        self._validate_unique = False
        BaseForm.__init__(
            self, data, files, auto_id, prefix, object_data, error_class, label_suffix, empty_permitted)
        if opts.objects:
            for field_name, get_objects in list(opts.objects.items()):
                field = self.fields.get(field_name)
                if isinstance(field, (CachedModelChoiceField, CachedModelMultipleChoiceField)):
                    field.objects = get_objects()


class ModelForm(with_metaclass(CachedModelFormMetaclass, CachedBaseModelForm)):
    '''
    ``ModelForm`` that uses ``CachedModelChoiceField`` and
    ``CachedModelMultipleChoiceField`` from fields.py.

    Objects are passed in ``Meta`` like this::

        class Meta:
            objects = {'field_name_1': objects1,
                       'field_name_2': objects2, ...}
    '''
    pass
