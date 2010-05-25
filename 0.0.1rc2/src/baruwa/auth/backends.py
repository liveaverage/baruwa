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
# vim: ai ts=4 sts=4 et sw=4
from django.contrib.auth.models import User
from baruwa.accounts.models import User as UserObject, UserFilters
try:
    import hashlib as md5
except ImportError:
    import md5

class MailwatchBackend:
    "Authenticates users using the mailwatch database"

    def authenticate(self, username=None, password=None):
        m = md5.md5(password)
        hashv = m.hexdigest()
        try:
            login = UserObject.objects.get(username__exact=username,password__exact=hashv)
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


def mail_auth(protocol,username,password,server,port=None):
        "Authenticates to pop3,imap,smtp servers"

        if protocol == 'pop3':
            import poplib,re
            regex = re.compile(r"^.+\<\d+\.\d+\@.+\>$")
            try:
                if port == '995':
                    conn = poplib.POP3_SSL(server)
                elif port == '110' or port is None:
                    conn = poplib.POP3(server)
                else:
                    conn = poplib.POP3(server,port)
                if regex.match(conn.getwelcome()):
                    conn.apop(username,password)
                else:
                    dump = conn.user(username)
                    conn.pass_(password)
                conn.quit()
                return True
            except:
                return False
        elif protocol == 'imap':
            import imaplib
            try:
                if port == '993':
                    conn = imaplib.IMAP4_SSL(server)
                elif port == '143' or port is None:
                    conn = imaplib.IMAP4(server)
                else:
                    conn = imaplib.IMAP4(server,port)
                dump = conn.login(username,password)
                dump = conn.logout()
                return True
            except:
                return False
        elif protocol == 'smtp':
            import smtplib
            try:
                if port == '465':
                    conn = smtplib.SMTP_SSL(server)
                elif port == '25' or port is None:
                    conn = smtplib.SMTP(server)
                else:
                    conn = smtplib.SMTP(server,port)
                conn.ehlo()
                if conn.has_extn('STARTTLS') and port != '465':
                    conn.starttls()
                    conn.ehlo()
                conn.login(username,password)
                conn.quit()
                return True
            except:
                return False
        else:
            return False

class MailBackend:
    "Authenticates users using pop3 imap and smtp auth"

    def authenticate(self, username=None, password=None):
        from django.conf import settings

        server = ''
        protocols = ['pop3','imap','smtp']

        if not '@' in username:
            return None
       
        login_user,domain = username.split('@')
        hosts = getattr(settings, 'MAIL_AUTH_HOSTS', ['localhost','localhost','110','pop3',True])
        for host in hosts:
            if len(host) == 5:
                if host[0] == domain and (host[3] in protocols):
                    server = host[1]
                    break
        
        if server == '':
            return None

        if not host[4]:
            login_user = username

        if mail_auth(host[3],login_user,password,host[1],host[2]):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.set_unusable_password()
                user.is_staff = False
                user.is_superuser = False
                user.save()
            try:
                mwuser = UserObject.objects.get(username=username)
            except UserObject.DoesNotExist:
                mwuser = UserObject(username=username)
                mwuser.save()
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
