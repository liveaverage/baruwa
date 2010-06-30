# Baruwa only setting
#

MS_CONFIG = '/etc/MailScanner/MailScanner.conf'
QUARANTINE_DAYS_TO_KEEP = 60
QUARANTINE_REPORT_HOSTURL = 'http://baruwa-alpha.local'
MAIL_AUTH_HOSTS = (
    #['topdog.za.net','tdss.co.za','25','smtp',True],
)
SA_RULES_DIRS = ['/usr/share/spamassassin','/etc/mail/spamassassin']
