from django.db import models
from datetime import datetime


# Create your models here.

class Card(models.Model):
    type = models.IntegerField(default=0)
    front = models.CharField(max_length=1000, default='')
    back = models.CharField(max_length=1000, default='')
    add_date = models.DateTimeField('date added', default=datetime.now)
    last_review_date = models.DateTimeField('last review date', default=datetime.now)
    review_count = models.IntegerField(default=0)

    def __str__(self):
        return self.front


class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)


class Deck(models.Model):
    name = models.CharField(max_length=100)
    cards = models.ManyToManyField(Card)
    user = models.ForeignKey(User)
