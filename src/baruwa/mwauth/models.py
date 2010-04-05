from django.db import models

# Create your models here.
class UserFilters(models.Model):
    username = models.CharField(max_length=60)
    filter = models.TextField()
    verify_key = models.CharField(max_length=96)
    active = models.CharField(max_length=3)
    class Meta:
        db_table = u'user_filters'

class Users(models.Model):
    username = models.CharField(max_length=60, primary_key=True)
    password = models.CharField(max_length=32)
    fullname = models.CharField(max_length=50)
    type = models.CharField(max_length=3)
    quarantine_report = models.IntegerField(null=True, blank=True)
    spamscore = models.IntegerField(null=True, blank=True)
    highspamscore = models.IntegerField(null=True, blank=True)
    noscan = models.IntegerField(null=True, blank=True)
    quarantine_rcpt = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'users'
