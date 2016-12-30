# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0009_auto_20161227_0610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personadoptpractice',
            name='adopt_practice',
            field=models.CharField(max_length=1, null=True, choices=[(b'1', b'Yes'), (b'2', b'No'), (b'3', b'Not Applicable')]),
        ),
    ]