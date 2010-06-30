from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Deletes records older than 60 days from the maillog table"

    def handle_noargs(self, **options):
        from django.db import connection
        #import datetime
        #from baruwa.messages.models import Message
        #interval = datetime.timedelta(days=60)
        #last_date = datetime.datetime.now() - interval
        #Message.objects.filter(timestamp__lt=last_date).delete()

        c = connection.cursor()
        c.execute('INSERT LOW_PRIORITY INTO archive SELECT * FROM messages WHERE timestamp < DATE_SUB(CURDATE(), INTERVAL 60 DAY)')
        c.execute('DELETE LOW_PRIORITY FROM messages WHERE timestamp < DATE_SUB(CURDATE(), INTERVAL 60 DAY)')
        c.execute('OPTIMIZE TABLE messages')
        c.execute('OPTIMIZE TABLE archive')
