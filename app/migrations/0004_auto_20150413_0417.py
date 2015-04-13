# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_friends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friends',
            name='user_id',
            field=models.ForeignKey(related_name='Friends_user_id', primary_key=True, db_column='user_id', to='app.User'),
        ),
        migrations.AlterUniqueTogether(
            name='checkin',
            unique_together=set([('survey_id', 'bill_id', 'restaurant_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='friends',
            unique_together=set([('user_id', 'friend_id')]),
        ),
    ]
