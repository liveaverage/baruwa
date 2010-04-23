# Baruwa only setting
#

MS_CONFIG = '/etc/MailScanner/MailScanner.conf'
QUARANTINE_DAYS_TO_KEEP = 60
QUARANTINE_REPORT_HOSTURL = 'http://baruwa-alpha.sentechsa.net'
MAIL_AUTH_HOSTS = (
    ['sentechsa.net','cgp3.sentechsa.net','110','pop3',False],
    ['topdog.za.net','tdss.co.za','25','smtp',True],
)
SA_RULES_DIRS = ['/usr/share/spamassassin','/etc/mail/spamassassin']
