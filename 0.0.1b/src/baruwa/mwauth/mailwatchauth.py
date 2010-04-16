#
# Baruwa
# Copyright (C) 2010  Andrew Colin Kissa
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from django.contrib.auth.models import User
from baruwa.accounts.models import Users,UserFilters
try:
    import hashlib as md5
except ImportError:
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
                user.set_unusable_password()
                user.is_staff = False
                if login.type == 'A':
                    user.is_superuser = True
                else:
                    user.is_superuser = False
                user.save()
            return user
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
