from django.contrib.auth.models import User
from mwauth.models import Users,UserFilters
import md5

class MailwatchBackend:
    def authenticate(self, username=None, password=None):
        m = md5.new(password)
        hashv = m.hexdigest()
        try:
            login = Users.objects.get(username__exact=username,password__exact=hashv)
        except Users.DoesNotExist:
            return None
        except:
            return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                #user.set_unusable_password()
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
