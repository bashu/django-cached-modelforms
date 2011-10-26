# -*- coding:utf-8 -*-
'''
Tests for ``ModelForm``.

Note that Django auth framework is required here, because its ``User``,
``Group``, ``Message`` and ``Permission`` models are used for testing.
'''

from django.test import TestCase
from django.contrib.auth.models import User, Message, Group, Permission
from django.forms.models import ModelChoiceField as OrigModelChoiceField
from django.forms.models import ModelMultipleChoiceField as OrigModelMultipleChoiceField
from django.forms import Textarea
from django.db.models import TextField, CharField

from cached_modelforms import ModelForm, ModelChoiceField, ModelMultipleChoiceField


def formfield_callback(f, **kwargs):
    result = f.formfield(**kwargs)
    if isinstance(f, (TextField, CharField)):
        result.widget = Textarea(attrs={'cols': '999', 'rows': '888'})
    return result

class TestForms(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(u'danny', u'danny@danny.com', u'123456')
        self.user2 = User.objects.create_user(u'penny', u'penny@penny.com', u'123456')
        self.user3 = User.objects.create_user(u'lenny', u'lenny@lenny.com', u'123456')

        self.cached_user_list = [self.user1, self.user2, self.user3]

        # Get any three permissions
        self.cached_perm_list = list(Permission.objects.all()[:3])

        class ModelFormSingle(ModelForm):
            class Meta:
                model = Message
                choices = {'user': self.cached_user_list}

        class ModelFormSingleWithoutChoices(ModelForm):
            class Meta:
                model = Message

        class ModelFormSingleWithFormfieldCallback(ModelForm):
            formfield_callback = formfield_callback

            class Meta:
                model = Message
                choices = {'user': self.cached_user_list}

        class ModelFormMultiple(ModelForm):
            class Meta:
                model = Group
                choices = {'permissions': self.cached_perm_list}

        class ModelFormMultipleWithoutChoices(ModelForm):
            class Meta:
                model = Group

        class ModelFormMultipleWithFormfieldCallback(ModelForm):
            formfield_callback = formfield_callback

            class Meta:
                model = Group
                choices = {'permissions': self.cached_perm_list}

        self.ModelFormSingle = ModelFormSingle
        self.ModelFormSingleWithoutChoices = ModelFormSingleWithoutChoices
        self.ModelFormSingleWithFormfieldCallback = ModelFormSingleWithFormfieldCallback
        self.ModelFormMultiple = ModelFormMultiple
        self.ModelFormMultipleWithoutChoices = ModelFormMultipleWithoutChoices
        self.ModelFormMultipleWithFormfieldCallback = ModelFormMultipleWithFormfieldCallback

    def test_modelform_single(self):
        form = self.ModelFormSingle({'user': unicode(self.user1.pk),
                                          'message': u'Hi, Danny!'})
        self.assertTrue(isinstance(form.fields['user'], ModelChoiceField))

        message = form.save()
        self.assertEqual(message.user, self.user1)

    def test_modelform_single_without_choices(self):
        form = self.ModelFormSingleWithoutChoices({'user': unicode(self.user1.pk),
                                                        'message': u'Hi, Danny!'})
        self.assertTrue(isinstance(form.fields['user'], OrigModelChoiceField))

    def test_modelform_single_with_formfield_callback(self):
        form = self.ModelFormSingleWithFormfieldCallback({'user': unicode(self.user1.pk),
                                                               'message': u'Hi, Danny!'})
        self.assertTrue(isinstance(form.fields['user'], ModelChoiceField))
        self.assertEqual(form.fields['message'].widget.attrs['cols'], '999')

    def test_modelform_multiple(self):
        form = self.ModelFormMultiple({'permissions': [unicode(self.cached_perm_list[0].pk),
                                                       unicode(self.cached_perm_list[1].pk)],
                                       'name': u'Somename'})
        self.assertTrue(isinstance(form.fields['permissions'], ModelMultipleChoiceField))

        group = form.save()
        self.assertEqual(set(group.permissions.all()), set([self.cached_perm_list[0],
                                                           self.cached_perm_list[1]]))

    def test_modelform_multiple_without_choices(self):
        form = self.ModelFormMultipleWithoutChoices({'permissions': [unicode(self.cached_perm_list[0].pk),
                                                                     unicode(self.cached_perm_list[1].pk)],
                                                     'name': u'Somename'})
        self.assertTrue(isinstance(form.fields['permissions'], OrigModelMultipleChoiceField))

    def test_modelform_multiple_with_formfield_callback(self):
        form = self.ModelFormMultipleWithFormfieldCallback({'permissions': [unicode(self.cached_perm_list[0].pk),
                                                                            unicode(self.cached_perm_list[1].pk)],
                                                            'name': u'Somename'})
        self.assertTrue(isinstance(form.fields['permissions'], ModelMultipleChoiceField))
        self.assertEqual(form.fields['name'].widget.attrs['cols'], '999')