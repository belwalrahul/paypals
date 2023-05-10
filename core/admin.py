from django.contrib import admin
from .models import Friend, Group, Transactions, FriendRequests

# Register your models here.
admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Transactions)
admin.site.register(FriendRequests)