# vim: ai ts=4 sts=4 et sw=4
from django.db import models

class Blacklist(models.Model):
    id = models.IntegerField(primary_key=True)
    to_address = models.TextField(unique=True, blank=True)
    to_domain = models.TextField(blank=True)
    from_address = models.TextField(unique=True, blank=True)
    class Meta:
        db_table = u'blacklist'
        get_latest_by = "id"
        ordering = ['-id']

    @models.permalink
    def get_absolute_url(self):
        return ('baruwa.lists.views.delete_from_list', (), {'list_kind':2,'item_it':self.id})

class Whitelist(models.Model):
    id = models.IntegerField(primary_key=True)
    to_address = models.TextField(unique=True, blank=True)
    to_domain = models.TextField(blank=True)
    from_address = models.TextField(unique=True, blank=True)
    class Meta:
        db_table = u'whitelist'
        get_latest_by = "id"
        ordering = ['-id']

