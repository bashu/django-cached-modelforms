# -*- coding:utf-8 -*-
from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.forms import Textarea
from django.db.models import CharField

from cached_modelforms import (ModelForm, CachedModelChoiceField,
                               CachedModelMultipleChoiceField)
from cached_modelforms.tests.utils import SettingsTestCase
from cached_modelforms.tests.models import (SimpleModel, ModelWithForeignKey,
                                            ModelWithM2m)


def formfield_callback(f, **kwargs):
    '''
    Sample ``formfield_callback`` function that changes the widget for any
    ``CharField`` in model.
    '''
    result = f.formfield(**kwargs)
    if isinstance(f, CharField):
        result.widget = Textarea(attrs={'cols': '999', 'rows': '888'})
    return result

class TestForms(SettingsTestCase):
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=('cached_modelforms.tests',))

        self.obj1 = SimpleModel.objects.create(name=u'name1')
        self.obj2 = SimpleModel.objects.create(name=u'name2')
        self.obj3 = SimpleModel.objects.create(name=u'name3')

        self.get_objects = lambda: [self.obj1, self.obj2, self.obj3]

        class ModelFormSingle(ModelForm):
            class Meta:
                model = ModelWithForeignKey
                objects = {'fk_field': self.get_objects}

        class ModelFormSingleWithoutObjects(ModelForm):
            class Meta:
                model = ModelWithForeignKey

        class ModelFormSingleWithFormfieldCallback(ModelForm):
            formfield_callback = formfield_callback

            class Meta:
                model = ModelWithForeignKey
                objects = {'fk_field': self.get_objects}

        class ModelFormMultiple(ModelForm):
            class Meta:
                model = ModelWithM2m
                objects = {'m2m_field': self.get_objects}

        class ModelFormMultipleWithoutObjects(ModelForm):
            class Meta:
                model = ModelWithM2m

        class ModelFormMultipleWithFormfieldCallback(ModelForm):
            formfield_callback = formfield_callback

            class Meta:
                model = ModelWithM2m
                objects = {'m2m_field': self.get_objects}

        class ModelFormMultipleWithInitials(ModelForm):
            class Meta:
                model = ModelWithM2m
                objects = {'m2m_field': self.get_objects}
                m2m_initials = {'m2m_field': (
                    lambda instance: [self.obj1.pk, self.obj2.pk]
                )}

        self.ModelFormSingle = ModelFormSingle
        self.ModelFormSingleWithoutObjects = ModelFormSingleWithoutObjects
        self.ModelFormSingleWithFormfieldCallback = ModelFormSingleWithFormfieldCallback
        self.ModelFormMultiple = ModelFormMultiple
        self.ModelFormMultipleWithoutObjects = ModelFormMultipleWithoutObjects
        self.ModelFormMultipleWithFormfieldCallback = ModelFormMultipleWithFormfieldCallback
        self.ModelFormMultipleWithInitials = ModelFormMultipleWithInitials

    def test_modelform_single(self):
        '''
        Test, that ``Meta.objects`` transforms to
        ``CachedModelChoiceField.objects``.
        '''
        form = self.ModelFormSingle({'fk_field': unicode(self.obj1.pk),
                                     'name': u'Name1'})
        self.assertTrue(
            isinstance(form.fields['fk_field'], CachedModelChoiceField)
        )

        # saving
        new_obj = form.save()
        self.assertEqual(new_obj.fk_field, self.obj1)

        # loading back
        form = self.ModelFormSingle(instance=new_obj)
        self.assertEqual(form.initial['fk_field'], self.obj1.pk)

    def test_modelform_single_without_objects(self):
        '''
        If there is no ``objects`` for field, nothing happens, usual
        ``ModelChoiceField`` is used.
        '''
        form = self.ModelFormSingleWithoutObjects({
            'fk_field': unicode(self.obj1.pk),
            'name': u'Name1'
        })
        self.assertTrue(isinstance(form.fields['fk_field'], ModelChoiceField))

    def test_modelform_single_with_formfield_callback(self):
        '''
        ``formfield_callback`` function will be decorated, not overwritten
        '''
        form = self.ModelFormSingleWithFormfieldCallback({
            'fk_field': unicode(self.obj1.pk),
            'name': u'Name1'
        })
        self.assertTrue(
            isinstance(form.fields['fk_field'], CachedModelChoiceField)
        )
        self.assertEqual(form.fields['name'].widget.attrs['cols'], '999')

    def test_modelform_multiple(self):
        '''
        Test, that ``Meta.objects`` transforms to
        ``CachedModelMultipleChoiceField.objects``.
        '''
        form = self.ModelFormMultiple({
            'm2m_field': [unicode(self.obj1.pk), unicode(self.obj2.pk)],
            'name': u'Name1'
        })
        self.assertTrue(
            isinstance(
                form.fields['m2m_field'],
                CachedModelMultipleChoiceField
            )
        )

        # saving
        new_obj = form.save()
        self.assertEqual(
            set(new_obj.m2m_field.all()),
            set([self.obj1, self.obj2])
        )

        # loading back
        form = self.ModelFormSingle(instance=new_obj)
        self.assertEqual(
            set(form.initial['m2m_field']),
            set([self.obj1.pk, self.obj2.pk])
        )

    def test_modelform_multiple_without_objects(self):
        '''
        If there is no ``objects`` for field, nothing happens, usual
        ``ModelMultipleChoiceField`` is used.
        '''
        form = self.ModelFormMultipleWithoutObjects({
            'm2m_field': [unicode(self.obj1.pk), unicode(self.obj2.pk)],
            'name': u'Name1'
        })
        self.assertTrue(
            isinstance(form.fields['m2m_field'], ModelMultipleChoiceField)
        )

    def test_modelform_multiple_with_formfield_callback(self):
        '''
        ``formfield_callback`` function will be decorated, not overwritten
        '''
        form = self.ModelFormMultipleWithFormfieldCallback({
            'm2m_field': [unicode(self.obj1.pk), unicode(self.obj2.pk)],
            'name': u'Name1'})
        self.assertTrue(
            isinstance(
                form.fields['m2m_field'],
                CachedModelMultipleChoiceField
            )
        )
        self.assertEqual(form.fields['name'].widget.attrs['cols'], '999')

    def test_modelform_multiple_with_initials(self):
        '''
        You can set initial for ``CachedModelMultipleChoiceField`` in
        ``Meta.m2m_initials``. There will be no DB request.
        '''
        form = self.ModelFormMultipleWithInitials({
            'm2m_field': [unicode(self.obj3.pk)],
            'name': u'Name1'})
        new_obj = form.save()
        form = self.ModelFormMultipleWithInitials(instance=new_obj)
        self.assertEqual(
            set(form.initial['m2m_field']),
            set([self.obj1.pk, self.obj2.pk])
        )
