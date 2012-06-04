=========================
Django Cached Modelforms
=========================

The application provides ``ModelForm``, ``ModelChoiceField``, ``ModelMultipleChoiceField`` implementations that can accept lists of objects, not just querysets. This can prevent these fields from hitting DB every time they are created.

The problem
=========================

Imagine the following form::

    class MyForm(forms.Form):
        obj = ModelChoiceField(queryset=MyModel.objects.all())

Every time you render the form ``ModelChoiceField`` field will hit DB. What if you don't want it? Can't you just pass the list of objects (from cache) to the field? You can't. What to do? Use CachedModelChoiceField.

The solution
=========================

Form with ``CachedModelChoiceField``::

     from cached_modelforms import CachedModelChoiceField

     class MyForm(forms.Form):
        obj = CachedModelChoiceField(objects=lambda:[obj1, obj2, obj3])

This field will act like regular ``ModelChoiceField``, but you pass a callable that returns the list of objects, not queryset, to it. Calable is needed because we don't want to evaluate the list out only once.

A callable can return:

* a list of objects: ``[obj1, obj2, obj3, ...]``. ``obj`` should have ``pk`` property and be coercible to unicode.
* a list of tuples: ``[(pk1, obj1), (pk2, obj2), (pk3, obj3), ...]``.
* a dict: ``{pk1: obj1, pk2: obj2, pk3: obj3, ...}``. Note that ``dict`` is unsorted so the items will be ordered by ``pk`` lexicographically.

Same is for ``CachedModelMultipleChoiceField``.

Warnings
=========================
There is no special validation here. The field won't check that the object is an instance of a particular model, it won't even check that object is a model instance. And it's up to you to keep cache relevant. Usually it's not a problem.

Modelform
=========================
But what about modelforms? They still use original ``ModelChoiceField`` for ``ForeignKey`` fields. This app has its own ``ModelForm`` that uses ``CachedModelChoiceField`` and ``CachedModelMultipleChoiceField``. The usage is following::

    # models.py
    class Category(models.Model):
        title = CharField(max_length=64)

    class Tag(models.Model):
        title = CharField(max_length=64)

    class Product(models.Model):
        title = CharField(max_length=64)
        category = models.ForeignKey(Category)
        tags = models.ManyToManyField(Tag)


    # forms.py
    class ProductForm(cached_modelforms.ModelForm):
        class Meta:
            model = Product
            objects = {
                'category': lambda:[...], # your callable here
                'tags': lambda:[...], # and here
            }

That's all. If you don't specify ``objects`` for some field, regular ``Model[Multiple]ChoiceField`` will be used.

m2m_initials
=========================
If you use ``ManyToManyField`` in ``ModelForm`` and load an ``instance`` to it, it will make one extra DB request (JOINed!) – to get initials for this field. Can we cache it too? Yes. You need a function that accepts model instance and returns a list of ``pk``'s – initials for the field. Here's a modification of previous example::

    # models.py

    class Product(models.Model):
        title = CharField(max_length=64)
        category = models.ForeignKey(Category)
        tags = models.ManyToManyField(Tag)

        def tags_cached(self):
            cache_key = 'tags_for_%(product_pk)d' % {'product_pk': self.pk}
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            result = list(self.tags.all())
            cache.set(cache_key, result)
            return result

    # forms.py

    class ProductForm(cached_modelforms.ModelForm):
        class Meta:
            model = Product
            objects = {
                'category': lambda:[...], # your callable here
                'tags': lambda:[...], # and here
            }
            m2m_initials = {'tags': lambda instance: [x.pk for x in instance.tags_cached()]}

Compatibility
=========================
For sure is works fine with Django 1.2-1.4. Altering ``ModelForm`` has required some copy-pasting from Django source code. It couldn't be done with inheritance. I don't think there will be problems with futher versions of Django, but don't forget to run the tests if something seems wrong.
