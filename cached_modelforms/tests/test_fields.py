# -*- coding:utf-8 -*-
'''
Tests for ``ModelChoiceField`` and ``ModelMultipleChoiceField``.

Note that Django auth framework is required here, because its ``User`` model
is used for testing.
'''

from django.test import TestCase
from django import forms
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

from cached_modelforms import ModelChoiceField, ModelMultipleChoiceField

class TestFields(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(u'danny', u'danny@danny.com', u'123456')
        self.user2 = User.objects.create_user(u'penny', u'penny@penny.com', u'123456')
        self.user3 = User.objects.create_user(u'lenny', u'lenny@lenny.com', u'123456')

        self.cached_list = [self.user1, self.user2, self.user3]

        class FormSingle(forms.Form):
            user = ModelChoiceField(choices=self.cached_list, required=False)

        class FormMultiple(forms.Form):
            user = ModelMultipleChoiceField(choices=self.cached_list, required=False)

        self.FormSingle = FormSingle
        self.FormMultiple = FormMultiple

    def test_modelchoicefield_choices_arg(self):
        '''
        Test, how the field accepts different types of ``choices`` argument.
        '''
        as_list = ModelChoiceField(choices=self.cached_list)
        as_iterable = ModelChoiceField(choices=iter(self.cached_list))
        list_of_tuples = [(x.pk, x) for x in self.cached_list]
        as_list_of_tuples = ModelChoiceField(choices=list_of_tuples)
        as_dict = ModelChoiceField(choices=dict(list_of_tuples))

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
        as_list = ModelMultipleChoiceField(choices=self.cached_list)
        as_iterable = ModelMultipleChoiceField(choices=iter(self.cached_list))
        list_of_tuples = [(x.pk, x) for x in self.cached_list]
        as_list_of_tuples = ModelMultipleChoiceField(choices=list_of_tuples)
        as_dict = ModelMultipleChoiceField(choices=dict(list_of_tuples))

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
        form = self.FormSingle({'user': unicode(self.user1.pk)})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['user'], self.user1)

        # no value
        form = self.FormSingle({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['user'], None)

        # invalid value
        form = self.FormSingle({'user': u'-1'})
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors['user'])

    def test_modelmultiplechoicefield_behavior(self):
        '''
        Test, how the field handles data in form.
        '''
        # some value
        form = self.FormMultiple({'user': [unicode(self.user1.pk), unicode(self.user2.pk)]})
        self.assertTrue(form.is_valid())
        self.assertEqual(set(form.cleaned_data['user']), set([self.user1, self.user2]))

        # no value
        form = self.FormMultiple({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['user'], [])

        # invalid value
        form = self.FormMultiple({'user': [unicode(self.user1.pk), u'-1']})
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors['user'])

        # invalid list
        form = self.FormMultiple({'user': u'-1'})
        self.assertFalse(form.is_valid())
        self.assertTrue(form._errors['user'])