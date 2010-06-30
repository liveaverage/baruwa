from django.db import models
from django.contrib.auth.models import User

class List(models.Model):
    """
    Spam Whitelist and Blacklist
    """
    id = models.IntegerField(primary_key=True)
    list_type = models.IntegerField(default=0)
    from_address = models.TextField(default='any')
    to_address = models.TextField(default='any')
    user = models.ForeignKey(User)
    
    class Meta:
        db_table = 'lists'

    def can_access(self, request):
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            addresses = request.session['user_filter']['addresses']
            if account_type == 2:
                dom = self.to_address
                if '@' in dom:
                    dom = dom.split('@')[1]
                if dom not in addresses:
                    return False
            if account_type == 3:
                if request.user.username != self.to_address:
                    if self.to_address not in addresses:
                        return False
        return True
