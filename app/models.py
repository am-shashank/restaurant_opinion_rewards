# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Bill(models.Model):
    id = models.IntegerField()
    restaurant = models.ForeignKey('Restaurant')
    amount = models.IntegerField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Bill'
        unique_together = (('id', 'restaurant_id'),)


class Choice(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Choice'


class HasBill(models.Model):
    item_name = models.ForeignKey('Item', db_column='item_name')
    restaurant = models.ForeignKey('Item')
    bill = models.ForeignKey(Bill)

    class Meta:
        managed = False
        db_table = 'Has_Bill'
        unique_together = (('item_name', 'bill_id', 'restaurant_id'),)


class HasChoice(models.Model):
    question = models.ForeignKey('Question')
    choice = models.ForeignKey(Choice)

    class Meta:
        managed = False
        db_table = 'Has_Choice'
        unique_together = (('question_id', 'choice_id'),)


class HasQuestion(models.Model):
    survey = models.ForeignKey('Survey')
    question = models.ForeignKey('Question')

    class Meta:
        managed = False
        db_table = 'Has_Question'
        unique_together = (('survey_id', 'question_id'),)


class Item(models.Model):
    name = models.CharField(max_length=80)
    price = models.FloatField(blank=True, null=True)
    restaurant = models.ForeignKey('Restaurant')

    class Meta:
        managed = False
        db_table = 'Item'
        unique_together = (('name', 'restaurant_id'),)


class Login(models.Model):
    user = models.ForeignKey('User', primary_key=True)
    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Login'


class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=100, blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Question'


class Refers(models.Model):
    referer = models.ForeignKey('User')
    referee = models.ForeignKey('User')

    class Meta:
        managed = False
        db_table = 'Refers'
        unique_together = (('referer_id', 'referee_id'),)


class Response(models.Model):
    id = models.IntegerField(primary_key=True)
    choice = models.ForeignKey(Choice, blank=True, null=True)
    question = models.ForeignKey(Question)
    survey = models.ForeignKey('Survey')
    text = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Response'


class Restaurant(models.Model):
    id = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=50, blank=True, null=True)
    full_address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    stars = models.FloatField(blank=True, null=True)
    review_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Restaurant'


class Restaurantneighborhoods(models.Model):
    neighborhood_name = models.CharField(max_length=80)
    restaurant = models.ForeignKey(Restaurant)

    class Meta:
        managed = False
        db_table = 'RestaurantNeighborhoods'
        unique_together = (('restaurant_id', 'neighborhood_name'),)


class Review(models.Model):
    id = models.IntegerField(primary_key=True)
    restaurant = models.ForeignKey(Restaurant, blank=True, null=True)
    stars = models.FloatField(blank=True, null=True)
    text = models.CharField(max_length=1000, blank=True, null=True)
    review_date = models.DateField(blank=True, null=True)
    votes_funny = models.IntegerField(blank=True, null=True)
    votes_useful = models.IntegerField(blank=True, null=True)
    votes_cool = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Review'


class Survey(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('User', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Survey'


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=20, blank=True, null=True)
    credit = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'User'
