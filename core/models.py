from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Friend(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    friends = models.ManyToManyField(User)
       
class Group(models.Model):
    groupID = models.AutoField(primary_key=True)
    groupName = models.CharField(max_length=30)
    userList = models.ManyToManyField(User)

class Transactions(models.Model):
    groupID = models.IntegerField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField()
    paid_by = models.ForeignKey(User)
    owed_by = models.ManyToManyField(User)
