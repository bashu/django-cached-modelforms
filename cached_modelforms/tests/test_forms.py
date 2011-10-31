# -*- coding:utf-8 -*-
from django.forms.models import ModelChoiceField as OrigModelChoiceField
from django.forms.models import ModelMultipleChoiceField as OrigModelMultipleChoiceField
from django.forms import Textarea
from django.db.models import CharField

from cached_modelforms import ModelForm, ModelChoiceField, ModelMultipleChoiceField
from cached_modelforms.tests.utils import SettingsTestCase
from cached_modelforms.tests.models import SimpleModel, ModelWithForeignKey, ModelWithM2m


def formfield_callback(f, **kwargs):
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

        self.cached_list = [self.obj1, self.obj2, self.obj3]

        class ModelFormSingle(ModelForm):
            class Meta:
                model = ModelWithForeignKey
                choices = {'fk_field': self.cached_list}

        class ModelFormSingleWithoutChoices(ModelForm):
            class Meta:
                model = ModelWithForeignKey

        class ModelFormSingleWithFormfieldCallback(ModelForm):
            formfield_callback = formfield_callback

            class Meta:
                model = ModelWithForeignKey
                choices = {'fk_field': self.cached_list}

        class ModelFormMultiple(ModelForm):
            class Meta:
                model = ModelWithM2m
                choices = {'m2m_field': self.cached_list}

        class ModelFormMultipleWithoutChoices(ModelForm):
            class Meta:
                model = ModelWithM2m

        class ModelFormMultipleWithFormfieldCallback(ModelForm):
            formfield_callback = formfield_callback

            class Meta:
                model = ModelWithM2m
                choices = {'m2m_field': self.cached_list}

        class ModelFormMultipleWithInitials(ModelForm):
            class Meta:
                model = ModelWithM2m
                choices = {'m2m_field': self.cached_list}
                m2m_initials = {'m2m_field': (lambda instance: [self.obj1.pk, self.obj2.pk])}

        self.ModelFormSingle = ModelFormSingle
        self.ModelFormSingleWithoutChoices = ModelFormSingleWithoutChoices
        self.ModelFormSingleWithFormfieldCallback = ModelFormSingleWithFormfieldCallback
        self.ModelFormMultiple = ModelFormMultiple
        self.ModelFormMultipleWithoutChoices = ModelFormMultipleWithoutChoices
        self.ModelFormMultipleWithFormfieldCallback = ModelFormMultipleWithFormfieldCallback
        self.ModelFormMultipleWithInitials = ModelFormMultipleWithInitials

    def test_modelform_single(self):
        form = self.ModelFormSingle({'fk_field': unicode(self.obj1.pk),
                                     'name': u'Name1'})
        self.assertTrue(isinstance(form.fields['fk_field'], ModelChoiceField))

        new_obj = form.save()
        self.assertEqual(new_obj.fk_field, self.obj1)

        form = self.ModelFormSingle(instance=new_obj)
        self.assertEqual(form.initial['fk_field'], self.obj1.pk)

    def test_modelform_single_without_choices(self):
        form = self.ModelFormSingleWithoutChoices({'fk_field': unicode(self.obj1.pk),
                                                   'name': u'Name1'})
        self.assertTrue(isinstance(form.fields['fk_field'], OrigModelChoiceField))

    def test_modelform_single_with_formfield_callback(self):
        form = self.ModelFormSingleWithFormfieldCallback({'fk_field': unicode(self.obj1.pk),
                                                          'name': u'Name1'})
        self.assertTrue(isinstance(form.fields['fk_field'], ModelChoiceField))
        self.assertEqual(form.fields['name'].widget.attrs['cols'], '999')

    def test_modelform_multiple(self):
        form = self.ModelFormMultiple({'m2m_field': [unicode(self.obj1.pk),
                                                     unicode(self.obj2.pk)],
                                       'name': u'Name1'})
        self.assertTrue(isinstance(form.fields['m2m_field'], ModelMultipleChoiceField))

        new_obj = form.save()
        self.assertEqual(set(new_obj.m2m_field.all()), set([self.obj1, self.obj2]))

        form = self.ModelFormSingle(instance=new_obj)
        self.assertEqual(set(form.initial['m2m_field']),  set([self.obj1.pk, self.obj2.pk]))

    def test_modelform_multiple_without_choices(self):
        form = self.ModelFormMultipleWithoutChoices({'m2m_field': [unicode(self.obj1.pk),
                                                                   unicode(self.obj2.pk)],
                                                     'name': u'Name1'})
        self.assertTrue(isinstance(form.fields['m2m_field'], OrigModelMultipleChoiceField))

    def test_modelform_multiple_with_formfield_callback(self):
        form = self.ModelFormMultipleWithFormfieldCallback({'m2m_field': [unicode(self.obj1.pk),
                                                                          unicode(self.obj2.pk)],
                                                            'name': u'Name1'})
        self.assertTrue(isinstance(form.fields['m2m_field'], ModelMultipleChoiceField))
        self.assertEqual(form.fields['name'].widget.attrs['cols'], '999')

    def test_modelform_multiple_with_initials(self):
        form = self.ModelFormMultipleWithInitials({'m2m_field': [unicode(self.obj3.pk)],
                                       'name': u'Name1'})
        new_obj = form.save()
        form = self.ModelFormMultipleWithInitials(instance=new_obj)
        self.assertEqual(set(form.initial['m2m_field']), set([self.obj1.pk, self.obj2.pk]))