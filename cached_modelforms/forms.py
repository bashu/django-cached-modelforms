# -*- coding:utf-8 -*-
'''
The realisation of ModelForm that uses ModelChoiceField and
ModelMultipleChoiceField from fields.py
'''

from django.db.models import ForeignKey, ManyToManyField
from django.forms.models import BaseModelForm, ModelFormOptions, fields_for_model
from django.forms.widgets import media_property
from django.forms.forms import get_declared_fields
from django.core.exceptions import FieldError

from fields import ModelChoiceField, ModelMultipleChoiceField


def make_formfield_callback(another_func, choices):
    '''
    Decorator that creates ``formfield_callback`` function (that makes
    ModelForm to use desired form field for certain model fields).
    
    If there is another ``formfield_callback`` defined, decorator
    will apply it too (for any field exept for ``ForeignKey`` and
    ``ManyToManyField``).
    '''
    def formfield_callback(f, **kwargs):
        if f.name in choices:
            kwargs['choices'] = choices[f.name]
            if isinstance(f, ForeignKey):
                return ModelChoiceField(**kwargs)
            elif isinstance(f, ManyToManyField):
                return ModelMultipleChoiceField(**kwargs)
        if another_func is not None:
            return another_func(f)(**kwargs)
        else:
            return f.formfield(**kwargs)
    return formfield_callback

class CachedModelFormOptions(ModelFormOptions):
    '''
    ``ModelFormOptions`` version that also extracts ``choices`` param.
    '''
    def __init__(self, options=None):
        super(CachedModelFormOptions, self).__init__(options)
        self.choices = getattr(options, 'choices', None)

class CachedModelFormMetaclass(type):
    '''
    ModelFormMetaclass version that applies ``make_formfield_callback``
    decorator and passess ``opts.choices`` to it if neccessary.
    
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
        new_class = super(CachedModelFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class

        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        opts = new_class._meta = CachedModelFormOptions(getattr(new_class, 'Meta', None))
        if opts.choices:
            formfield_callback = make_formfield_callback(formfield_callback, opts.choices)
        if opts.model:
            # If a model is defined, extract form fields from it.
            fields = fields_for_model(opts.model, opts.fields,
                                      opts.exclude, opts.widgets, formfield_callback)
            # make sure opts.fields doesn't specify an invalid field
            none_model_fields = [k for k, v in fields.iteritems() if not v]
            missing_fields = set(none_model_fields) - \
                             set(declared_fields.keys())
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

class ModelForm(BaseModelForm):
    '''
    ``ModelForm`` that uses ``ModelChoiceField`` and
    ``ModelMultipleChoiceField`` from fields.py.
    
    Choices are passed in ``Meta`` like this::
        
        class Meta:
            choices = {'field_name_1': choices1,
                       'field_name_2': choices2, ...}
    '''
    __metaclass__ = CachedModelFormMetaclass
