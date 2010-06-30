from django.db import models
from django.contrib.auth.models import User

class SavedFilter(models.Model):
    """SavedFilter"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    field = models.CharField(max_length=25)
    op_field = models.IntegerField()
    value = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    
    class Meta:
        db_table = 'report_filters'

    def __unicode__(self):
        return u"Saved Filter id: " + self.id


