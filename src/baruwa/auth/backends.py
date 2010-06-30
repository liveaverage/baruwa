from django.contrib.auth.models import User
from baruwa.accounts.models import UserProfile

class MailBackend:
    "Authenticates users using pop3 imap and smtp auth"

    def mail_auth(self, protocol, username, password, server,port=None):
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

        if self.mail_auth(host[3],login_user,password,host[1],host[2]):
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User(username=username)
                user.set_unusable_password()
                user.is_staff = False
                user.is_superuser = False
                try:
                    from django.forms.fields import email_re
                except ImportError:
                    from django.core.validators import email_re
                if email_re.match(username):
                    user.email = username
                user.save()
            try:
                profile = user.get_profile()
            except UserProfile.DoesNotExist:
                profile = UserProfile(user=user, account_type=3)
                profile.save()
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None