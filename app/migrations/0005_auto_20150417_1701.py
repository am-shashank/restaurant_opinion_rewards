# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150413_0417'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupons',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('deal', models.CharField(max_length=100)),
                ('expires', models.DateTimeField()),
                ('image_path', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'Coupons',
            },
        ),
        migrations.AddField(
            model_name='refers',
            name='referee_telephone',
            field=models.ForeignKey(primary_key=True, db_column='telephone', default=16782304782, to='app.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='image_path',
            field=models.CharField(default=b'/static/images/wireframe/image.png', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='telephone',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='login',
            name='user_id',
            field=models.ForeignKey(primary_key=True, db_column='user_id', serialize=False, to='app.User'),
        ),
        migrations.AlterField(
            model_name='refers',
            name='referee_id',
            field=models.ForeignKey(related_name='Refers_referee_id', db_column='referee_id', to='app.User'),
        ),
        migrations.AlterField(
            model_name='refers',
            name='referer_id',
            field=models.ForeignKey(related_name='Refers_referer_id', db_column='referer_id', to='app.User'),
        ),
        migrations.AlterUniqueTogether(
            name='refers',
            unique_together=set([('restaurant_id', 'referee_telephone')]),
        ),
        migrations.AddField(
            model_name='coupons',
            name='restaurant_id',
            field=models.ForeignKey(to='app.Restaurant', db_column='restaurant_id'),
        ),
        migrations.AddField(
            model_name='coupons',
            name='user_id',
            field=models.ForeignKey(to='app.User', db_column='user_id'),
        ),
    ]
