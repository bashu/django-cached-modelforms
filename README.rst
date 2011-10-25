=========================
Django Cached Modelforms
=========================

The application provides ModelForm, ModelChoiceField, ModelMultipleChoiceField implementations that can accept lists of objects, not just querysets. This can prevent these fields from hitting DB every time they are created.