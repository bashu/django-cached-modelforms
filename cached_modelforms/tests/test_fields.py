# -*- coding:utf-8 -*-
from django import forms
from django.utils.encoding import smart_unicode

from cached_modelforms.tests.utils import SettingsTestCase
from cached_modelforms.tests.models import SimpleModel
from cached_modelforms import ModelChoiceField, ModelMultipleChoiceField

class TestFields(SettingsTestCase):
    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=('cached_modelforms.tests',))

        self.obj1 = SimpleModel.objects.create(name=u'name1')
        self.obj2 = SimpleModel.objects.create(name=u'name2')
        self.obj3 = SimpleModel.objects.create(name=u'name3')

        self.cached_list = [self.obj1, self.obj2, self.obj3]

        class FormSingle(forms.Form):
            obj = ModelChoiceField(objects=self.cached_list, required=False)

        class FormMultiple(forms.Form):
            obj = ModelMultipleChoiceField(objects=self.cached_list, required=False)

        self.FormSingle = FormSingle
        self.FormMultiple = FormMultiple

    def test_modelchoicefield_choices_arg(self):
        '''
        Test, how the field accepts different types of ``choices`` argument.
        '''
        as_list = ModelChoiceField(objects=self.cached_list)
        as_iterable = ModelChoiceField(objects=iter(self.cached_list))
        list_of_tuples = [(x.pk, x) for x in self.cached_list]
        as_list_of_tuples = ModelChoiceField(objects=list_of_tuples)
        as_dict = ModelChoiceField(objects=dict(list_of_tuples))

        choices_without_empty_label = as_list.choices[:]
        if as_list.empty_label is not None:
            choices_without_empty_label.pop(0)

        # make sure all of the ``choices`` attrs are the same
        self.assertTrue(as_list.choices == as_iterable.choices == as_list_of_tuples.choices == as_dict.choices)

        # same for ``objects``
        self.assertTrue(as_list.objects == as_iterable.objects == as_list_of_tuples.objects == as_dict.objects)

        # ``objects`` should be a dict as ``{smart_unicode(pk1): obj1, ...}``
        self.assertEqual(set(as_list.objects.keys()), set([smart_unicode(x.pk) for x in self.cached_list]))
        self.assertEqual(set(as_list.objects.values()), set(self.cached_list))

        # ``choices`` should be a list as ``[(smart_unicode(pk1), smart_unicode(obj1)), ...]``
        self.assertEqual(choices_without_empty_label, [(smart_unicode(x.pk), smart_unicode(x)) for x in self.cached_list])

    def test_modelmultiplechoicefield_choices_arg(self):
        '''
        Test, how the field accepts different types of ``choices`` argument.
        '''
        as_list = ModelMultipleChoiceField(objects=self.cached_list)
        as_iterable = ModelMultipleChoiceField(objects=iter(self.cached_list))
        list_of_tuples = [(x.pk, x) for x in self.cached_list]
        as_list_of_tuples = ModelMultipleChoiceField(objects=list_of_tuples)
        as_dict = ModelMultipleChoiceField(objects=dict(list_of_tuples))

        # make sure all of the ``choices`` attrs are the same
        self.assertTrue(as_list.choices == as_iterable.choices == as_list_of_tuples.choices == as_dict.choices)

        # same for ``objects``
        self.assertTrue(as_list.objects == as_iterable.objects == as_list_of_tuples.objects == as_dict.objects)

        # ``objects`` should be a dict as ``{smart_unicode(pk1): obj1, ...}``
        self.assertEqual(set(as_list.objects.keys()), set([smart_unicode(x.pk) for x in self.cached_list]))
        self.assertEqual(set(as_list.objects.values()), set(self.cached_list))

        # ``choices`` should be a list as ``[(smart_unicode(pk1), smart_unicode(obj1)), ...]``
        self.assertEqual(as_list.choices, [(smart_unicode(x.pk), smart_unicode(x)) for x in self.cached_list])

    def test_modelchoicefield_behavior(self):
        '''
        Test, how the field handles data in form.
        '''
        # some value
        form = self.FormSingle({'obj': unicode(self.obj1.pk)})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['obj'], self.obj1)

        # no value
        form = self.FormSingle({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['obj'], None)

        # invalid value
        form = self.FormSingle({'obj': u'-1'})
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors['obj'])

    def test_modelmultiplechoicefield_behavior(self):
        '''
        Test, how the field handles data in form.
        '''
        # some value
        form = self.FormMultiple({'obj': [unicode(self.obj1.pk), unicode(self.obj2.pk)]})
        self.assertTrue(form.is_valid())
        self.assertEqual(set(form.cleaned_data['obj']), set([self.obj1, self.obj2]))

        # no value
        form = self.FormMultiple({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['obj'], [])

        # invalid value
        form = self.FormMultiple({'obj': [unicode(self.obj1.pk), u'-1']})
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors['obj'])

        # invalid list
        form = self.FormMultiple({'obj': u'-1'})
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors['obj'])