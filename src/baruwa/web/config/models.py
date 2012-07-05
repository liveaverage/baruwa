#
# Baruwa - Web 2.0 MailScanner front-end.
# Copyright (C) 2010-2012  Andrew Colin Kissa <andrew@topdog.za.net>
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
from django.core.exceptions import ValidationError
from south.modelsinspector import add_introspection_rules

from baruwa.utils.regex import HOST_OR_IPV4_RE


class HostnameField(models.CharField):
    REGEX = HOST_OR_IPV4_RE

    def clean(self, value, *extraargs, **extraextraargs):
        value = super(HostnameField, self).clean(value,
                                            *extraargs,
                                            **extraextraargs)
        result = self.REGEX.search(value)
        if len(result.groups()) == 0:
            raise ValidationError("You need to enter a valid hostname/domain")
        return value

add_introspection_rules([], ["^baruwa\.web\.config\.models\.HostnameField"])


class ModelWithNameRules(models.Model):
    '''The abstract parent model that enforces rules to the names of objects:
    1) Do not allow NAME changes for instances with an UPPERCASE name.
    2) Do not allow modification of some selected object instances
    (e.g. the ALWAYS Time object, the EVERYONE Source object, ...)'''
    def clean(self):
        if self.pk:
            name_in_db = self.__class__.objects.get(pk=self.pk).name
            if name_in_db.isupper():
                if name_in_db != self.name:
                    raise ValidationError("""Definitions with UPPERCASE names
                    are predefined, their names cannot not be changed.""")
            read_only_names = []
            classname = self.__class__.__name__ 
            if classname == 'Time':
                read_only_names = ['ALWAYS',]
            if classname == 'Source':
                read_only_names = ['EVERYONE',]
            if name_in_db in read_only_names:
                raise ValidationError("""The %s definition is read-only and
                cannot be modified.""" % name_in_db)

    class Meta:
        abstract = True

class SquidGuardBasicModel(ModelWithNameRules):
    '''The generic, abstract parent model for squidguard basic configuration
    blocks (Source, Destination, Time).'''
    CONF_TEMPLATE = """
### %(name)s
%(cfgtype)s %(name)s {
%(content)s
}

    """
    CONF_TEMPLATE_DEST = """
### %(name)s
dest %(local_or_BL)s__%(name)s {
    domainlist         %(local_or_BL)s/%(name)s/domains
    urllist            %(local_or_BL)s/%(name)s/urls
    expressionlists    %(local_or_BL)s/%(name)s/expressionlist
    verbose squidguard-global.log
}

    """

    def __unicode__(self):
        return self.name

    def squidguard_config(self):
        '''Returns squidguard configuration text for this
        Django model instance (Source, Destination or Time).'''
        config = ''
        cfgtype = self.__class__.__name__.lower()

        if cfgtype in ('source','time'):
            content = ''
            for line in self.config.split('\n'):
                if line:
                    content += '    %s' % line 
            config = self.CONF_TEMPLATE % {'cfgtype':cfgtype,
                                            'name':self.name,
                                            'content':content}
        if cfgtype in ('destination',):
            if self.is_local():
                local_or_BL = 'local'
            else: 
                local_or_BL= 'BL'
            config = self.CONF_TEMPLATE_DEST % {'local_or_BL':local_or_BL,
                                                'name':self.name}
        return config

    class Meta:
        abstract = True


class Time(SquidGuardBasicModel):
    '''Defines a period of time, which is part of an AclRule.
    This can be configured using the config field, which 
    contains squidguard time definition. Example: weekly sunday.'''

    name = models.SlugField(unique=True)
    config = models.TextField(default='#Example: weekly sunday')

    def _ismutable(self):
        "check mutablity"
        return self.name not in ['ALWAYS', 'WORKTIME', 'FREETIME']

    mutable = property(_ismutable)

    def _canrename(self):
        "check if renameable"
        return self.name.isupper() == False

    renameable = property(_canrename)


class Source(SquidGuardBasicModel):
    '''Defines the source of a web request, used by Webfilter
    AclRules.
    This can be configured using the config field, which contains
    squidguard config: (combination of) ipaddress, user or ldapsearch.
    Example: user jjansens'''

    name = models.SlugField(unique=True)
    config = models.TextField(default='#Example: user jjansens')

    def _ismutable(self):
        "check mutablity"
        return self.name not in ['EVERYONE']

    mutable = property(_ismutable)

    def _canrename(self):
        "check if renameable"
        return self.name.isupper() == False

    renameable = property(_canrename)


class DestinationComponent(models.Model):
    '''Defines the destination of a web request, can be either a url,
    domain or regular expression. It is part of a *locally* defined 
    Destination database.
    For example http://www.trustteam.be/some/page'''

    DESTINATION_TYPE_CHOICES = (
        ('u', 'url'),
        ('d','domain'),
        ('r','regular expression'),
    )

    DESTINATION_TYPE_DICT = {'u':'url','d':'domain','r':'regular expression'}

    destination_type = models.CharField(max_length=1,
                        choices=DESTINATION_TYPE_CHOICES)
    destination_type.help_text = '''Can be either an url
                                (http://wwww.example.org/and/then/some.html),
                                a domain (www.example.org), or a regular
                                expression (http://.+\.exe$).
                                Regular expressions url filtering SLOWdown,
                                do not use it unless strictly necessary.'''
    url = models.URLField(max_length=255, blank=True)
    domain = HostnameField(max_length=255, blank=True)
    regex = models.CharField(max_length=255, blank=True)
    destinations = models.ManyToManyField('Destination', blank=True,
                    limit_choices_to = {'is_local__exact': True})

    def clean(self):
        type_validation_dict = {'u':self.url, 'd':self.domain, 'r':self.regex}
        if self.destination_type:
            destination_value = type_validation_dict[self.destination_type]
            if not destination_value:
                raise ValidationError('''DestinationComponent of type %(desttype)s
                        should have a %(desttype)s defined.''' %
                        {'desttype':self.DESTINATION_TYPE_DICT[self.destination_type]})

    def __unicode__(self):
        type_validation_dict = {'u':self.url,'d':self.domain,'r':self.regex}
        return type_validation_dict[self.destination_type]

    class Meta:
        unique_together = ('destination_type', 'url', 'domain', 'regex',)


class Destination(SquidGuardBasicModel):
    '''A Destination is collection of similar DestinationComponents.
    For example destination 'searchengines' contains DestinationComponents:
    www.google.com, wwww.yahoo.com, ... .
    Destinations may be locally defined, or they may be predefined by an
    external database (eg ShallaList).'''

    name = models.CharField(max_length=255,unique=True)
    is_local = models.BooleanField(default=True)
    is_local.help_text  = '''A destination is local when it is locally defined
                            by the system administrator, not part of an
                            externaldatabase. Only local destinations can be
                            modified by the webfilter administrator.'''


class DestinationPolicy(ModelWithNameRules):
    '''An DestinationPolicy defines what destinations are allowed, and
    what destinations are denied. It is composed of OrderedDestinations.'''

    name = models.SlugField(unique=True)
    permit_other_access = models.BooleanField(default=True)
    permit_other_access.help_text = '''Wether to permit or deny all 
                other/undefined access by this DestinationPolicy.'''

    def __unicode__(self):
        return self.name

    def squidguard_config(self):
        cfg = ''
        remaining_destinations = list(Destination.objects.all())
        for ordereddestination in self.ordereddestination_set.order_by('order'):
            cfg += ordereddestination.squidguard_config()
            if ordereddestination.destination in remaining_destinations:
                remaining_destinations.remove(ordereddestination.destination)

        for remaining_destination in remaining_destinations:
            if self.permit_other_access:
                cfg += '%s ' % remaining_destination.name
            else:
                cfg += "!%s " % remaining_destination.name

        if self.permit_other_access:
            cfg += 'all'
        else:
            cfg += 'none'
        return cfg

    def _ismutable(self):
        "check mutablity"
        return self.name not in ['PERMITALL', 'PERMITNONE']

    mutable = property(_ismutable)

    def _canrename(self):
        "Check if renaming is allowed"
        return self.name.isupper() == False

    renameable = property(_canrename)


class OrderedDestination(models.Model):
    '''Each OrderedDestination represents part of an DestinationPolicy:
    a destination for which its order is specified, and wether it should
    be permitted.'''

    order = models.PositiveIntegerField()
    destination_policy = models.ForeignKey(DestinationPolicy)
    destination = models.ForeignKey(Destination)
    permit = models.BooleanField(default=False)

    def squidguard_config(self):
        config = ''
        if not self.permit:
            config = '!'
        config += self.destination.name
        return config

    def swap_order(self, other):
        "Swap item"
        maxorder = OrderedDestination\
                    .objects\
                    .filter(destination_policy__exact=self.destination_policy)\
                    .all()[0].order + 1
        prev_order, self.order = self.order, maxorder
        self.save()
        self.order, other.order = other.order, prev_order
        other.save()
        self.save()

    def save(self, *args, **kwargs):
        "Generate order if not set and save to DB"
        if self.order is None:
            try:
                self.order = OrderedDestination\
                            .objects\
                            .filter(destination_policy__exact=self.destination_policy)\
                            .all()[0].order + 1
            except(IndexError):
                self.order = 0
        super(OrderedDestination, self).save(*args, **kwargs)

    def move_up(self):
        "Move up"
        try:
            if self.is_first():
                raise IndexError
            next_item = OrderedDestination\
                        .objects\
                        .filter(destination_policy__exact=self.destination_policy)\
                        .filter(order__gt=self.order).reverse()[0]
        except IndexError:
            pass
        else:
            self.swap_order(next_item)

    def move_down(self):
        "Move down"
        try:
            if self.is_last():
                raise IndexError
            prev_item = OrderedDestination\
                        .objects\
                        .filter(destination_policy__exact=self.destination_policy)\
                        .filter(order__lt=self.order).all()[0]
        except IndexError:
            pass
        else:
            self.swap_order(prev_item)

    def is_first(self):
        "Returns true if first item"
        return OrderedDestination\
                .objects\
                .filter(destination_policy__exact=self.destination_policy)\
                .filter(order__gt=self.order).count() == 0

    first = property(is_first)

    def is_last(self):
        "Returns true if last item"
        return OrderedDestination\
                .objects\
                .filter(destination_policy__exact=self.destination_policy)\
                .filter(order__lt=(self.order)).count() == 0

    last = property(is_last)

    class Meta:
        ordering = ['destination_policy','-order']
        #ordering = ["-order",]
        unique_together = ('destination_policy', 'destination', 'permit',)


class AclRule(models.Model):
    '''Access Control List Rules. Each AclRule instance is a rule
    permitting or denying access to web resources. For each access
    through the webfilter, rules are evaluated one by one
    (order property determines priority). First matching rule wins.'''

    CONF_TEMPLATE = """
### %(name)s
%(source_and_time)s {
    pass %(destination_policy)s
    redirect http://localhost/cgi-bin/squidguard/squidGuard.cgi?clientaddr=%%a&clientname=%%n&clientuser=%%i&clientgroup=%%s&targetgroup=%%t&url=%%u
    logfile verbose squidguard-global.log
}
    """

    order = models.PositiveIntegerField()
    time = models.ForeignKey(Time)
    time.help_text = '''WHEN. Time when this rule applies. Can be either
                    outside or inside the given timeframe, depending on
                    the time_invert setting.'''
    time_invert = models.BooleanField(default=False)
    time_invert.help_text = '''WHEN. Determines wether this rule applies
                            INSIDE (False) or OUTSIDE (True) the specified
                            time setting.'''
    source = models.ForeignKey(Source)
    source.help_text = '''WHO. Source to which this rule applies. Is
                        (a combination of) username, ip, ldapgroup'''
    destination_policy =  models.ForeignKey(DestinationPolicy)
    destination_policy.help_text = '''WHAT. Defines what destinations this
                        rule permits and what destinations this rule denies.'''

    def clean(self):
        if self.pk:
            destination_policy_name_in_db = self.__class__.objects.get(pk=self.pk).destination_policy.name
            if ((destination_policy_name_in_db == 'DEFAULT_POLICY') and
                (self.destination_policy.name != destination_policy_name_in_db)):
                raise ValidationError('''Changing the rule pointing to the
                                    default policy is not allowed.''')
        else:
            if (hasattr(self, 'destination_policy') and
                self.destination_policy.name == 'DEFAULT_POLICY'):
                count_default_policies = self.__class__.objects\
                .filter(destination_policy__name='DEFAULT_POLICY').count()
                if count_default_policies != 0:
                    raise ValidationError('''A rule pointing to the 
                            DEFAULT_POLICY is already in place. You
                            cannot have multiple DEFAULT_POLICY rules.''')

    def _get_source_and_time(self):
        c = self.source.name
        if self.time_invert:
            c += ' outside '
        else:
            c += ' within '
        c += self.time.name
        return c

    def squidguard_config(self):
        conf = {}
        conf['name'] = self.source.name
        conf['source_and_time'] += self._get_source_and_time()
        conf['destination_policy'] = self.destination_policy.squidguard_config()
        return self.CONF_TEMPLATE % conf

    def swap_order(self, other):
        "Swap item"
        maxorder = AclRule.objects.all()[0].order + 1
        prev_order, self.order = self.order, maxorder
        self.save()
        self.order, other.order = other.order, prev_order
        other.save()
        self.save()

    def save(self, *args, **kwargs):
        "Generate order if not set and save to DB"
        if self.order is None:
            try:
                self.order = AclRule.objects.all()[0].order + 1
            except(IndexError):
                self.order = 0
        super(AclRule, self).save(*args, **kwargs)

    def move_up(self):
        "Move up"
        try:
            if self.is_default():
                raise IndexError
            next_item = AclRule.objects.filter(order__gt=self.order).reverse()[0]
        except IndexError:
            pass
        else:
            self.swap_order(next_item)

    def move_down(self):
        "Move down"
        try:
            if self.is_last():
                raise IndexError
            prev_item = AclRule.objects.filter(order__lt=self.order).all()[0]
        except IndexError:
            pass
        else:
            self.swap_order(prev_item)

    def is_first(self):
        "Returns true if first item"
        return AclRule.objects.filter(order__gt=self.order).count() == 0

    first = property(is_first)

    def is_last(self):
        "Returns true if last item"
        return AclRule.objects.filter(order__lt=(self.order - 1)).count() == 0

    last = property(is_last)

    def is_default(self):
        "Returns true if default policy"
        return self.destination_policy.name == 'DEFAULT_POLICY'

    default = property(is_default)

    class Meta:
        ordering = ["-order",]


def update_predefined_destinationpolicies(sender, instance, **kwargs):
    '''Whenever a Destination is added/changed/removed, update the special
    DestinationPolicies.
    - PERMITALL should contain all destinations (permitted)
    - PERMITNONE should contain all destinations (denied)'''
    # Rebuild PERMIT_EVERYTHING
    try:
        permit_everything = DestinationPolicy.objects.get(name__exact='PERMITALL')
    except models.ObjectDoesNotExist:
        # create it if it does not exist
        permit_everything = DestinationPolicy()
        permit_everything.name = 'PERMITALL'
        permit_everything.permit_other_access = True
        permit_everything.save()
    else:
        permit_everything.ordereddestination_set.all().delete()
    # Rebuild DENY_EVERYTHING
    try:
        deny_everything = DestinationPolicy.objects.get(name__exact='PERMITNONE')
    except models.ObjectDoesNotExist:
        # create it if it does not exist
        deny_everything = DestinationPolicy()
        deny_everything.name = 'PERMITNONE'
        deny_everything.permit_other_access = True
        deny_everything.save()
    else:
        deny_everything.ordereddestination_set.all().delete()
    count = 0
    for dest in Destination.objects.all():
        count +=1
        # od_permit
        od_permit = OrderedDestination()
        od_permit.order = count
        od_permit.destination_policy = permit_everything
        od_permit.destination = dest
        od_permit.permit = True
        od_permit.save()
        # od_deny
        od_deny = OrderedDestination()
        od_deny.order = count
        od_deny.destination_policy = deny_everything
        od_deny.destination = dest
        od_deny.permit = False
        od_deny.save()

models.signals.post_save.connect(update_predefined_destinationpolicies , sender=Destination)
models.signals.post_delete.connect(update_predefined_destinationpolicies , sender=Destination)