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
    image_path = models.CharField(max_length=100)
    class Meta:
        db_table = 'Restaurant'


class Restaurantneighborhoods(models.Model):
    neighborhood_name = models.CharField(max_length=80, primary_key=True)
    restaurant_id = models.ForeignKey(Restaurant, primary_key=True)

    class Meta:
        # managed = False
        db_table = 'RestaurantNeighborhoods'
        unique_together = (('restaurant_id', 'neighborhood_name'),)

class Bill(models.Model):
    id = models.IntegerField(primary_key=True)
    restaurant_id = models.ForeignKey('Restaurant', primary_key=True)
    amount = models.IntegerField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Bill'
        unique_together = (('id', 'restaurant_id'),)

class Item(models.Model):
    name = models.CharField(max_length=80,primary_key=True)
    price = models.FloatField(blank=True, null=True)
    restaurant_id = models.ForeignKey('Restaurant', primary_key=True)

    class Meta:
        # managed = False
        db_table = 'Item'
        unique_together = (('name', 'restaurant_id'),)

class HasBill(models.Model):
    item_name = models.ForeignKey('Item', related_name='HasBill_item_name', db_column='name', primary_key=True)
    restaurant_id = models.ForeignKey('Item', related_name='HasBill_restaurant_id', db_column='restaurant_id', primary_key=True)
    bill_id = models.ForeignKey(Bill, primary_key=True)

    class Meta:
        # managed = False
        db_table = 'Has_Bill'
        unique_together = (('item_name', 'bill_id', 'restaurant_id'),)

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    email = models.CharField(max_length=20, blank=True, null=True)
    credit = models.IntegerField(blank=True, null=True)
    telephone = models.IntegerField(blank=True, null=True)
    class Meta:
        # managed = False
        db_table = 'User'


class Login(models.Model):
    user_id = models.ForeignKey('User', db_column='user_id', primary_key=True)
    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Login'

class Refers(models.Model):
    referer_id = models.ForeignKey('User', related_name='Refers_referer_id', db_column='referer_id')
    referee_id = models.ForeignKey('User', related_name='Refers_referee_id', db_column='referee_id')
    restaurant_id = models.ForeignKey('Restaurant', db_column='id', primary_key=True)
    referee_telephone = models.ForeignKey('User', db_column='telephone', primary_key=True)
    class Meta:
        db_table = 'Refers'
        unique_together = (('restaurant_id', 'referee_telephone'),)

class Survey(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('User', blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Survey'

class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=100, blank=True, null=True)
    flag = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Question'

class Choice(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Choice'

class HasQuestion(models.Model):
    survey_id = models.ForeignKey('Survey', related_name='HasQuestion_survey_id', primary_key=True)
    question_id = models.ForeignKey('Question', related_name='HasQuestion_question_id', primary_key=True)

    class Meta:
        # managed = False
        db_table = 'Has_Question'
        unique_together = (('survey_id', 'question_id'),)

class HasChoice(models.Model):
    question_id = models.ForeignKey('Question', related_name='HasChoice_question_id', primary_key=True)
    choice_id = models.ForeignKey(Choice, related_name='HasChoice_choice_id', primary_key=True)

    class Meta:
        # managed = False
        db_table = 'Has_Choice'
        unique_together = (('question_id', 'choice_id'),)


class Response(models.Model):
    id = models.IntegerField(primary_key=True)
    choice = models.ForeignKey(Choice, blank=True, null=True)
    question = models.ForeignKey(Question)
    survey = models.ForeignKey('Survey')
    text = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        # managed = False
        db_table = 'Response'


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
        # managed = False
        db_table = 'Review'

class Checkin(models.Model):
    survey_id = models.ForeignKey('Survey', db_column='id', primary_key=True)
    bill_id = models.ForeignKey('Bill', related_name='Checkin_bill_id', primary_key=True)
    restaurant_id = models.ForeignKey('Bill', related_name='Checkin_restaurant_id', primary_key=True)

    class Meta:
        unique_together = (('survey_id', 'bill_id', 'restaurant_id'),)
        db_table = 'Checkin'

class Friends(models.Model):
    user_id = models.ForeignKey('User', db_column='user_id', related_name='Friends_user_id', primary_key=True)
    friend_id = models.ForeignKey('User', db_column='friend_id', related_name='Friends_friend_id', primary_key=True)

    class Meta:
        unique_together = (('user_id', 'friend_id'),)
        db_table = 'Friends'

class Coupons(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey('User', db_column='user_id')
    restaurant_id = models.ForeignKey('Restaurant', db_column='restaurant_id')
    deal = models.CharField(max_length=100)
    expires = models.DateTimeField()
    image_path = models.CharField(max_length=50)

    class Meta:
        db_table = 'Coupons'
