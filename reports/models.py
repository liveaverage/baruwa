from django.db import models

class SavedFilters(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(unique=True)
    col = models.TextField(unique=True)
    operator = models.TextField(unique=True)
    value = models.TextField(unique=True)
    username = models.TextField(unique=True)
    class Meta:
        db_table = u'saved_filters'

