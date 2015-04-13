# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('text', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
                'db_table': 'Choice',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('text', models.CharField(max_length=100, null=True, blank=True)),
                ('flag', models.IntegerField(null=True, blank=True)),
                ('category', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
                'db_table': 'Question',
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('text', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'db_table': 'Response',
            },
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.CharField(max_length=80, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('full_address', models.CharField(max_length=200, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('state', models.CharField(max_length=50, null=True, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('stars', models.FloatField(null=True, blank=True)),
                ('review_count', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Restaurant',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('stars', models.FloatField(null=True, blank=True)),
                ('text', models.CharField(max_length=1000, null=True, blank=True)),
                ('review_date', models.DateField(null=True, blank=True)),
                ('votes_funny', models.IntegerField(null=True, blank=True)),
                ('votes_useful', models.IntegerField(null=True, blank=True)),
                ('votes_cool', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Review',
            },
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'Survey',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('first_name', models.CharField(max_length=50, null=True, blank=True)),
                ('last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('dob', models.DateField(null=True, blank=True)),
                ('email', models.CharField(max_length=20, null=True, blank=True)),
                ('credit', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'User',
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.IntegerField(primary_key=True)),
                ('restaurant_id', models.ForeignKey(primary_key=True, serialize=False, to='app.Restaurant')),
                ('amount', models.IntegerField(null=True, blank=True)),
                ('image', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'Bill',
            },
        ),
        migrations.CreateModel(
            name='HasChoice',
            fields=[
                ('question_id', models.ForeignKey(related_name='HasChoice_question_id', primary_key=True, to='app.Question')),
                ('choice_id', models.ForeignKey(related_name='HasChoice_choice_id', primary_key=True, serialize=False, to='app.Choice')),
            ],
            options={
                'db_table': 'Has_Choice',
            },
        ),
        migrations.CreateModel(
            name='HasQuestion',
            fields=[
                ('survey_id', models.ForeignKey(related_name='HasQuestion_survey_id', primary_key=True, serialize=False, to='app.Survey')),
                ('question_id', models.ForeignKey(related_name='HasQuestion_question_id', primary_key=True, to='app.Question')),
            ],
            options={
                'db_table': 'Has_Question',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('name', models.CharField(max_length=80, primary_key=True)),
                ('price', models.FloatField(null=True, blank=True)),
                ('restaurant_id', models.ForeignKey(primary_key=True, serialize=False, to='app.Restaurant')),
            ],
            options={
                'db_table': 'Item',
            },
        ),
        migrations.CreateModel(
            name='Login',
            fields=[
                ('user', models.ForeignKey(primary_key=True, serialize=False, to='app.User')),
                ('facebook_id', models.CharField(max_length=20, null=True, blank=True)),
                ('password', models.CharField(max_length=20, null=True, blank=True)),
            ],
            options={
                'db_table': 'Login',
            },
        ),
        migrations.CreateModel(
            name='Refers',
            fields=[
                ('referer_id', models.ForeignKey(related_name='Refers_referer_id', primary_key=True, db_column='referer_id', to='app.User')),
                ('referee_id', models.ForeignKey(related_name='Refers_referee_id', primary_key=True, db_column='referee_id', to='app.User')),
                ('restaurant_id', models.ForeignKey(primary_key=True, db_column='id', serialize=False, to='app.Restaurant')),
            ],
            options={
                'db_table': 'Refers',
            },
        ),
        migrations.CreateModel(
            name='Restaurantneighborhoods',
            fields=[
                ('neighborhood_name', models.CharField(max_length=80, serialize=False, primary_key=True)),
                ('restaurant_id', models.ForeignKey(to='app.Restaurant', primary_key=True)),
            ],
            options={
                'db_table': 'RestaurantNeighborhoods',
            },
        ),
        migrations.AddField(
            model_name='survey',
            name='user',
            field=models.ForeignKey(blank=True, to='app.User', null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='restaurant',
            field=models.ForeignKey(blank=True, to='app.Restaurant', null=True),
        ),
        migrations.AddField(
            model_name='response',
            name='choice',
            field=models.ForeignKey(blank=True, to='app.Choice', null=True),
        ),
        migrations.AddField(
            model_name='response',
            name='question',
            field=models.ForeignKey(to='app.Question'),
        ),
        migrations.AddField(
            model_name='response',
            name='survey',
            field=models.ForeignKey(to='app.Survey'),
        ),
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('survey_id', models.ForeignKey(primary_key=True, db_column='id', serialize=False, to='app.Survey')),
                ('bill_id', models.ForeignKey(related_name='Checkin_bill_id', primary_key=True, to='app.Bill')),
                ('restaurant_id', models.ForeignKey(related_name='Checkin_restaurant_id', primary_key=True, to='app.Bill')),
            ],
            options={
                'db_table': 'Checkin',
            },
        ),
        migrations.CreateModel(
            name='HasBill',
            fields=[
                ('item_name', models.ForeignKey(related_name='HasBill_item_name', primary_key=True, db_column='name', serialize=False, to='app.Item')),
                ('restaurant_id', models.ForeignKey(related_name='HasBill_restaurant_id', primary_key=True, db_column='restaurant_id', to='app.Item')),
                ('bill_id', models.ForeignKey(to='app.Bill', primary_key=True)),
            ],
            options={
                'db_table': 'Has_Bill',
            },
        ),
        migrations.AlterUniqueTogether(
            name='restaurantneighborhoods',
            unique_together=set([('restaurant_id', 'neighborhood_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='refers',
            unique_together=set([('referer_id', 'referee_id', 'restaurant_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together=set([('name', 'restaurant_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='hasquestion',
            unique_together=set([('survey_id', 'question_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='haschoice',
            unique_together=set([('question_id', 'choice_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='bill',
            unique_together=set([('id', 'restaurant_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='hasbill',
            unique_together=set([('item_name', 'bill_id', 'restaurant_id')]),
        ),
    ]
