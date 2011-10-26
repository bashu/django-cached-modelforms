# -*- coding:utf-8 -*-
from django.db import models


class SimpleModel(models.Model):
    name = models.CharField(max_length=8)

class ModelWithForeignKey(models.Model):
    name = models.CharField(max_length=8)
    fk_field = models.ForeignKey(SimpleModel)

class ModelWithM2m(models.Model):
    name = models.CharField(max_length=8)
    m2m_field = models.ManyToManyField(SimpleModel)