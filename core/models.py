from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Friend(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    friends = models.ManyToManyField(User,related_name='friends')
       
class Group(models.Model):
    groupID = models.AutoField(primary_key=True)
    groupName = models.CharField(max_length=30)
    userList = models.ManyToManyField(User,related_name='userList')

class Transactions(models.Model):
    groupID = models.IntegerField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(decimal_places=2,max_digits=15)
    paid_by = models.ForeignKey(User,on_delete=models.CASCADE)
    owed_by = models.ManyToManyField(User,related_name='owed_by')
    settled = models.BooleanField(default=False)
