# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loop', '0004_auto_20160914_2154'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregatorShareOutliers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('time_modified', models.DateTimeField(auto_now=True, null=True)),
                ('date', models.DateField()),
                ('amount', models.FloatField()),
                ('comment', models.CharField(max_length=200, null=True, blank=True)),
                ('aggregator', models.ForeignKey(to='loop.LoopUser')),
                ('mandi', models.ForeignKey(to='loop.Mandi')),
                ('user_created', models.ForeignKey(related_name='loop_aggregatorshareoutliers_created', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('user_modified', models.ForeignKey(related_name='loop_aggregatorshareoutliers_related_modified', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='gaddidar',
            name='discount_criteria',
            field=models.IntegerField(default=0, choices=[(0, b'Volume'), (1, b'Amount')]),
        ),
        migrations.AlterUniqueTogether(
            name='aggregatorshareoutliers',
            unique_together=set([('date', 'aggregator', 'mandi')]),
        ),
    ]
