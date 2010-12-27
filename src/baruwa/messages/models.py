#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010  Andrew Colin Kissa <andrew@topdog.za.net>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# vim: ai ts=4 sts=4 et sw=4
#

from django.db import models
from django.db.models import Q

class MessageManager(models.Manager):
    "message manager"
    def for_user(self, request):
        "returns users messages"
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(MessageManager, self).get_query_set().filter(
                Q(from_domain__in=addresses) | Q(to_domain__in=addresses))
            if account_type == 3:
                return super(MessageManager, self).get_query_set().filter(
                Q(from_address__in=addresses) | Q(to_address__in=addresses))
        return super(MessageManager, self).get_query_set()

    def to_user(self, request):
        "returns messages to the users accounts"
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(MessageManager, self).get_query_set().filter(
                Q(to_domain__in=addresses))
            if account_type == 3:
                return super(MessageManager, self).get_query_set().filter(
                Q(to_address__in=addresses))
        return super(MessageManager, self).get_query_set()

    def from_user(self, request):
        "returns messages from users accounts"
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(MessageManager, self).get_query_set().filter(
                Q(from_domain__in=addresses))
            if account_type == 3:
                return super(MessageManager, self).get_query_set().filter(
                Q(from_address__in=addresses))
        return super(MessageManager, self).get_query_set()


class RecipientManager(models.Manager):
    "Recipients manager"
    def for_user(self, request):
        "returns users records"
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(RecipientManager, self).get_query_set().filter(
                Q(to_domain__in=addresses))
            if account_type == 3:
                return super(RecipientManager, self).get_query_set().filter(
                Q(to_address__in=addresses))
        return super(RecipientManager, self).get_query_set()


class QuarantineMessageManager(models.Manager):
    """
    QuarantineMessageManager
    """
    def for_user(self, request):
        "users quarantine"
        if not request.user.is_superuser:
            addresses = request.session['user_filter']['addresses']
            account_type = request.session['user_filter']['account_type']
            if account_type == 2:
                return super(QuarantineMessageManager, self).get_query_set().\
                filter(
                    Q(from_domain__in=addresses) | Q(to_domain__in=addresses)
                ).filter(isquarantined__exact=1)
            if account_type == 3:
                return super(QuarantineMessageManager, self).get_query_set().\
                filter(
                    Q(from_address__in=addresses) | Q(to_address__in=addresses)
                ).filter(isquarantined__exact=1)
        return super(QuarantineMessageManager, self).get_query_set().filter(
            isquarantined__exact=1
            )

class EmailReportMessageManager(models.Manager):
    "Used in processing the quarantine email reports"
    

    def for_user(self, user):
        "users messages"
        from baruwa.accounts.models import UserProfile, UserAddresses
        
        addresses = UserAddresses.objects.values('address').filter(
                user=user).exclude(enabled=0)
        account_type = UserProfile.objects.values('account_type').get(user=user)
        if user.is_superuser:
            return super(EmailReportMessageManager, self).get_query_set().\
            filter(
                isquarantined__exact=1
            )
        else:
            if account_type['account_type'] == 2:
                return super(EmailReportMessageManager, self).get_query_set()\
                .filter(
                    Q(from_domain__in=addresses) | Q(to_domain__in=addresses)
                ).filter(isquarantined__exact=1)
            else:
                return super(EmailReportMessageManager, self).get_query_set().\
                filter(
                    Q(from_address__in=addresses) | Q(to_address__in=addresses)
                     | Q(to_address=user.username) | 
                     Q(from_address=user.username)
                ).filter(isquarantined__exact=1)

    def to_user(self, user):
        "messages to user"
        from baruwa.accounts.models import UserProfile, UserAddresses
        
        addresses = UserAddresses.objects.values('address').filter(
            user=user
        ).exclude(enabled=0)
        account_type = UserProfile.objects.values('account_type').get(user=user)
        if user.is_superuser:
            return super(EmailReportMessageManager, self).get_query_set().\
            filter(isquarantined__exact=1)
        else:
            if account_type['account_type'] == 2:
                return super(EmailReportMessageManager, self).get_query_set()\
                .filter(
                    Q(to_domain__in=addresses)).filter(isquarantined__exact=1)
            else:
                return super(EmailReportMessageManager, self).get_query_set().\
                filter(Q(to_address__in=addresses) | 
                Q(to_address=user.username)).filter(isquarantined__exact=1)

    def from_user(self, user):
        "messages from user"
        from baruwa.accounts.models import UserProfile, UserAddresses
        
        addresses = UserAddresses.objects.values('address').filter(
            user=user
        ).exclude(enabled=0)
        account_type = UserProfile.objects.values('account_type').get(user=user)
        if user.is_superuser:
            return super(EmailReportMessageManager, self).get_query_set().\
            filter(isquarantined__exact=1)
        else:
            if account_type['account_type'] == 2:
                return super(EmailReportMessageManager, self).get_query_set().\
                filter(Q(from_domain__in=addresses)
                ).filter(isquarantined__exact=1)
            else:
                return super(EmailReportMessageManager, self).get_query_set().\
                filter(Q(from_address__in=addresses) | 
                Q(from_address=user.username)).filter(isquarantined__exact=1)

class ReportMessageManager(models.Manager):

    def all(self, user, enddate=None):
        "reporting messages"
        from baruwa.accounts.models import UserProfile, UserAddresses
        addresses = (UserAddresses.objects.values('address').
        filter(user=user).exclude(enabled=0).all()[:])
        account_type = (UserProfile.objects.values('account_type')
        .get(user=user))
        if user.is_superuser:
            query = super(ReportMessageManager, self).get_query_set()
            if enddate:
                query = query.filter(date__gt=enddate)
        else:
            if account_type['account_type'] == 2:
                query = super(ReportMessageManager, self).get_query_set()\
                .filter(Q(from_domain__in=addresses) | \
                Q(to_domain__in=addresses))
                if enddate:
                    query = query.filter(date__gt=enddate)
            else:
                query = super(ReportMessageManager, self).get_query_set()\
                .filter(Q(from_address__in=addresses) | \
                Q(to_address__in=addresses) | Q(to_address=user.username)\
                 | Q(from_address=user.username))
                if enddate:
                    query = query.filter(date__gt=enddate)
        return query

class TotalsMessageManager(models.Manager):
    "totals manager"
    def makevals(self, val):
        "map function to build a row"
        index = val[0]
        index += 1
        row = val[1]
        vpct = "%.1f" % ((1.0 * int(row[2])/int(row[1]))*100)
        spct = "%.1f" % ((1.0 * int(row[3])/int(row[1]))*100)
        obj = self.model(id=index, date=str(row[0]),
            mail_total=int(row[1]), virus_total=int(row[2]),
            virus_percent=vpct, spam_total=int(row[3]),
            spam_percent=spct, size_total=int(row[4]))
        obj.total = row[1]
        return obj

    def doms(self, domain, enddate=None):
        "domain message totals"
        from django.db import connection
        conn = connection.cursor()
        if enddate:
            query = """
                SELECT date, count(*) AS mail_total,
                SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END)
                AS virus_total, SUM(CASE WHEN (virusinfected=0)
                AND spam>0 THEN 1 ELSE 0 END) AS spam_total,
                SUM(size) AS size_total FROM messages WHERE 
                from_domain = %s OR to_domain = %s AND date > %s
                 GROUP BY date ORDER BY date DESC
                """
            conn.execute(query, [domain, domain, enddate])
        else:
            query = """
                SELECT date, count(*) AS mail_total,
                SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END)
                AS virus_total, SUM(CASE WHEN (virusinfected=0)
                AND spam>0 THEN 1 ELSE 0 END) AS spam_total,
                SUM(size) AS size_total FROM messages WHERE 
                from_domain = %s OR to_domain = %s GROUP BY 
                date ORDER BY date DESC
                """
            conn.execute(query, [domain, domain])
        result_list = map(self.makevals, enumerate(conn.fetchall()))
        return result_list
        
    def all(self, user, filters_list=None, addrs=None, act=3):
        "message totals"
        from django.db import connection
        from baruwa.utils.misc import raw_user_filter
        from baruwa.reports.utils import gen_dynamic_raw_query
        conn = connection.cursor()
        query = """
            SELECT date, count(*) AS mail_total,
            SUM(CASE WHEN virusinfected>0 THEN 1 ELSE 0 END)
            AS virus_total, SUM(CASE WHEN (virusinfected=0)
            AND spam>0 THEN 1 ELSE 0 END) AS spam_total,
            SUM(size) AS size_total FROM messages
            """
        if filters_list:
            sub = gen_dynamic_raw_query(filters_list)
            if user.is_superuser:
                conn.execute(query + " WHERE " + sub[0] +
                " GROUP BY date ORDER BY date DESC",sub[1])
            else:
                sql = raw_user_filter(user, addrs, act)
                conn.execute(query + " WHERE " + sql +" AND "+ sub[0] +
                " GROUP BY date ORDER BY date DESC", sub[1])
        else:
            if user.is_superuser:
                query = "%s GROUP BY date ORDER BY date DESC" % query
                conn.execute(query)
            else:
                sql = raw_user_filter(user, addrs, act)
                query = """%s WHERE %s GROUP BY date ORDER BY date
                DESC""" % (query, sql)
                conn.execute(query)

        result_list = map(self.makevals, enumerate(conn.fetchall()))
        return result_list

class SpamScoresManager(models.Manager):
    "spam scores manager"

    def all(self, user, filters_list=None, addrs=None, act=3):
        "spam scores"
        from django.db import connection
        from baruwa.utils.misc import raw_user_filter
        from baruwa.reports.utils import gen_dynamic_raw_query

        conn = connection.cursor()
        query = """
        SELECT round(sascore) AS score, count(*) AS count FROM messages
        """

        if filters_list:
            sub = gen_dynamic_raw_query(filters_list)
            if user.is_superuser:
                conn.execute(query + " WHERE " +  sub[0] +
                " AND whitelisted=0 AND scaned = 1 GROUP" +
                " BY score ORDER BY score", sub[1])
            else:
                sql = raw_user_filter(user, addrs, act)
                conn.execute(query + " WHERE " + sql + " AND "+ sub[0] +
                " AND whitelisted=0 AND scaned = 1 GROUP BY" +
                " score ORDER BY score", sub[1])
        else:
            if user.is_superuser:
                query = """%s WHERE whitelisted=0 AND scaned = 1 GROUP BY
                        score ORDER BY score""" % query
                conn.execute(query)
            else:
                sql = raw_user_filter(user, addrs, act)
                gql = """WHERE %s AND whitelisted=0 AND scaned = 1 GROUP
                    BY score ORDER BY score""" % sql
                query = "%s %s" % (query, gql)
                conn.execute(query)
        result_list = [self.model(id=i + 1, score=row[0], count=int(row[1])) 
                        for i, row in enumerate(conn.fetchall())]
        return result_list

class MessageStatsManager(models.Manager):
    "message stats manager"

    def get(self, user, addrs=None, act=3):
        "message stats"
        from django.db import connection
        import datetime
        from baruwa.utils.misc import raw_user_filter

        conn = connection.cursor()
        today = datetime.date.today()

        query = """
        SELECT COUNT(*) AS mail, SUM(CASE WHEN virusinfected=0 AND
        nameinfected=0 AND otherinfected=0 AND spam=0 AND
        highspam=0 THEN 1 ELSE 0 END) AS clean_mail, SUM(CASE WHEN
         virusinfected>0 THEN 1 ELSE 0 END) AS virii, SUM(CASE WHEN
          nameinfected>0 AND virusinfected=0 AND otherinfected=0
        AND spam=0 AND highspam=0 THEN 1 ELSE 0 END) AS infected,
        SUM(CASE WHEN otherinfected>0 AND nameinfected=0 AND
        virusinfected=0 AND spam=0 AND highspam=0 THEN 1 ELSE 0 END)
        AS otherinfected, SUM(CASE WHEN spam>0 AND virusinfected=0
        AND nameinfected=0 AND otherinfected=0 AND highspam=0 THEN
        1 ELSE 0 END) AS spam_mail, SUM(CASE WHEN highspam>0 AND
        virusinfected=0 AND nameinfected=0 AND otherinfected=0
        THEN 1 ELSE 0 END) AS high_spam, SUM(size) AS size FROM
        messages WHERE date = '%s'
        """ % today

        if user.is_superuser:
            conn.execute(query)
        else:
            sql = raw_user_filter(user, addrs, act)
            conn.execute(query + " AND " + sql)

        row = conn.fetchone()
        return self.model(total=row[0], clean_mail=row[1], virii=row[2],
        infected=row[3], otherinfected=row[4], spam_mail=row[5],
        high_spam=row[6], size=row[7])


class MessageStats(models.Model):
    "message stats"
    total = models.IntegerField()
    clean_mail = models.IntegerField()
    virii = models.IntegerField()
    infected = models.IntegerField()
    otherinfected = models.IntegerField()
    spam_mail = models.IntegerField()
    high_spam = models.IntegerField()
    size = models.IntegerField()

    objects = MessageStatsManager()

    class Meta:
        managed = False

class SpamScores(models.Model):
    "spam scores"
    score = models.FloatField()
    count = models.IntegerField()

    objects = SpamScoresManager()

    def obj_to_dict(self):
        " object to dict"
        vals = [(field.name, getattr(self, field.name)) 
                for field in self._meta.fields]
        return dict(vals)

    class Meta:
        managed = False


class MessageTotals(models.Model):
    "message totals"
    date = models.DateField()
    mail_total = models.IntegerField()
    virus_total = models.IntegerField()
    virus_percent = models.CharField(max_length=10)
    spam_total = models.IntegerField()
    spam_percent = models.CharField(max_length=10)
    size_total = models.IntegerField()

    objects = TotalsMessageManager()

    def obj_to_dict(self):
        "convert object to dict"
        vals = [(field.name, getattr(self, field.name)) 
                for field in self._meta.fields]
        return dict(vals)

    class Meta:
        managed = False

class Message(models.Model):
    """
    Message Model, represents messages in the
    Database.
    """

    id = models.CharField(max_length=255, primary_key=True)
    actions = models.CharField(max_length=255)
    clientip = models.IPAddressField()
    date = models.DateField()
    from_address = models.CharField(blank=True, db_index=True, max_length=255)
    from_domain = models.CharField(db_index=True, max_length=255)
    headers = models.TextField()
    hostname = models.TextField()
    highspam = models.IntegerField(default=0, db_index=True)
    rblspam = models.IntegerField(default=0)
    saspam = models.IntegerField(default=0)
    spam = models.IntegerField(default=0, db_index=True)
    nameinfected = models.IntegerField(default=0)
    otherinfected = models.IntegerField(default=0)
    isquarantined = models.IntegerField(default=0, db_index=True)
    sascore = models.FloatField()
    scaned = models.IntegerField(default=0)
    size = models.IntegerField()
    blacklisted = models.IntegerField(default=0, db_index=True)
    spamreport = models.TextField(blank=True)
    whitelisted = models.IntegerField(default=0, db_index=True)
    subject = models.TextField(blank=True)
    time = models.TimeField()
    timestamp = models.DateTimeField()
    to_address = models.CharField(db_index=True, max_length=255)
    to_domain = models.CharField(db_index=True, max_length=255)
    virusinfected = models.IntegerField(default=0)

    objects = models.Manager()
    messages = MessageManager()
    report = ReportMessageManager()
    quarantine = QuarantineMessageManager()
    quarantine_report = EmailReportMessageManager()

    class Meta:
        db_table = 'messages'
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']

    def __unicode__(self):
        return u"Message id: "+ self.id

    def can_access(self, request):
        """can_access"""
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            addresses = request.session['user_filter']['addresses']
            if account_type == 2:
                if (('@' not in self.to_address) and
                    ('@' not in self.from_address)
                    and (',' not in self.to_address)
                    and (',' not in self.from_address)):
                    return False
                else:
                    parts = self.to_address.split(',')
                    parts.extend(self.from_address.split(','))
                    for part in parts:
                        if '@' in part:
                            dom = part.split('@')[1]
                            if dom in addresses:
                                return True
                    return False
            if account_type == 3:
                addresses = request.session['user_filter']['addresses']
                if ((self.to_address not in addresses) and
                    (self.from_address not in addresses)):
                    return False
        return True

class Recipient(models.Model):
    "message recipients"
    message = models.ForeignKey(Message)
    to_address = models.CharField(db_index=True, max_length=255)
    to_domain = models.CharField(db_index=True, max_length=255)
    
    objects = models.Manager()
    messages = RecipientManager()
    
    class Meta:
        db_table = u'message_recipients'
    

class SaRules(models.Model):
    "spamassassin rules"
    rule = models.CharField(max_length=25, primary_key=True)
    rule_desc = models.CharField(max_length=200)

    class Meta:
        db_table = u'sa_rules'


class Release(models.Model):
    "quarantine release records"
    message_id = models.CharField(max_length=255, unique=True)
    #release_address = models.CharField(max_length=255)
    uuid = models.CharField(max_length=36)
    timestamp = models.DateTimeField()
    released = models.IntegerField(default=0)
    class Meta:
        db_table = u'quarantine_releases'


class Archive(models.Model):
    "archive records"
    id = models.CharField(max_length=255, primary_key=True)
    actions = models.CharField(max_length=255)
    clientip = models.IPAddressField()
    date = models.DateField()
    from_address = models.CharField(blank=True, db_index=True, max_length=255)
    from_domain = models.CharField(db_index=True, max_length=255)
    headers = models.TextField()
    hostname = models.TextField()
    highspam = models.IntegerField(default=0, db_index=True)
    rblspam = models.IntegerField(default=0)
    saspam = models.IntegerField(default=0)
    spam = models.IntegerField(default=0, db_index=True)
    nameinfected = models.IntegerField(default=0)
    otherinfected = models.IntegerField(default=0)
    isquarantined = models.IntegerField(default=0, db_index=True)
    sascore = models.FloatField()
    scaned = models.IntegerField(default=0)
    size = models.IntegerField(db_index=True)
    blacklisted = models.IntegerField(default=0, db_index=True)
    spamreport = models.TextField(blank=True)
    whitelisted = models.IntegerField(default=0, db_index=True)
    subject = models.TextField(blank=True)
    time = models.TimeField()
    timestamp = models.DateTimeField()
    to_address = models.CharField(db_index=True, max_length=255)
    to_domain = models.CharField(db_index=True, max_length=255)
    virusinfected = models.IntegerField(default=0)

    objects = models.Manager()
    messages = MessageManager()
    report = ReportMessageManager()
    quarantine = QuarantineMessageManager()
    quarantine_report = EmailReportMessageManager()
    class Meta:
        db_table = u'archive'
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
    
    #not ideal to duplicate will work on it later    
    def can_access(self, request):
        """can_access"""
        if not request.user.is_superuser:
            account_type = request.session['user_filter']['account_type']
            addresses = request.session['user_filter']['addresses']
            if account_type == 2:
                if (('@' not in self.to_address) and
                    ('@' not in self.from_address)
                    and (',' not in self.to_address)
                    and (',' not in self.from_address)):
                    return False
                else:
                    parts = self.to_address.split(',')
                    parts.extend(self.from_address.split(','))
                    for part in parts:
                        if '@' in part:
                            dom = part.split('@')[1]
                            if (dom in addresses) or (dom in addresses):
                                return True
                    return False
            if account_type == 3:
                addresses = request.session['user_filter']['addresses']
                if ((self.to_address not in addresses) and
                    (self.from_address not in addresses)):
                    return False
        return True
