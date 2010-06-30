from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    help = "Updates the database with the spam descriptions"

    def handle_noargs(self, **options):
        import re, glob, os
        from django.conf import settings
        from baruwa.messages.models import SaRules

        search_dirs = getattr(settings, 'SA_RULES_DIRS',[])
        regex = re.compile(r'^describe\s+(\S+)\s+(.+)$')
        for dir in search_dirs:
            if not dir.endswith(os.sep):
                dir = dir + os.sep
            for file in glob.glob(dir + '*.cf'):
                f = open(file,'r')
                for line in f.readlines():
                    m = regex.match(line)
                    if m:
                        print m.groups()[0] + ' ' + m.groups()[1]
                        rule = SaRules(rule=m.groups()[0],rule_desc=m.groups()[1])
                        try:
                            rule.save()
                        except:
                            pass
                f.close()
