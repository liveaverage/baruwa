%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif

Name:           baruwa
Version:        1.1.0
Release:        9%{?dist}
Summary:        Ajax enabled MailScanner web frontend      
Group:          Applications/Internet
License:        GPLv2
URL:            http://www.baruwa.org/
Source0:        http://pypi.python.org/packages/source/b/baruwa/%{name}-%{version}.tar.bz2
Source1:        baruwa.httpd
Source2:        baruwa.cron
Source3:        baruwa.mailscanner
Source4:        baruwa.init
Source5:        baruwa.sysconfig
Source6:        baruwa.cron.monthly
Source7:        baruwa.cron.d
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  gettext
Requires:       Django >= 1.2
Requires:       Django-south
Requires:       django-celery
Requires:       python-GeoIP
Requires:       python-IPy
Requires:       python-reportlab
Requires:       python-lxml
Requires:       MySQL-python >= 1.2.2
Requires:       httpd
Requires:       mod_wsgi
Requires:       dojo >= 1.5.1
Requires:       mailscanner >= 4.80.10
%if ! (0%{?fedora} > 6 || 0%{?rhel} > 5)
Requires:       python-uuid
%endif
Requires(pre): shadow-utils
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(postun): initscripts

%description
Baruwa (swahili for letter or mail) is a web 2.0 MailScanner
front-end. 

It provides an easy to use interface for managing a MailScanner
installation. It is used to perform operations such as releasing
quarantined messages, spam learning, whitelisting and 
blacklisting addresses, monitoring the health of the services etc. 
Baruwa is implemented using web 2.0 features (AJAX) where deemed 
fit, graphing is also implemented on the client side using SVG, 
Silverlight or VML. Baruwa has full support for i18n, letting you
support any language of your choosing.

It includes reporting functionality with an easy to use query 
builder, results can be displayed as message lists or graphed
as colorful and pretty interactive graphs.

Custom MailScanner modules are provided to allow for logging of 
messages to the mysql database with SQLite as backup, managing 
whitelists and blacklists and managing per user spam check 
settings.

%prep
%setup -q -n %{name}-%{version}

%{__cat} <<'EOF' > %{name}.logrotate
/var/log/baruwa/*.log {
       weekly
       rotate 10
       copytruncate
       delaycompress
       compress
       notifempty
       missingok
}
EOF
for dir in $(find src/baruwa/locale -mindepth 1 -maxdepth 1 -type d); do
locale=`basename ${dir}`;
msgfmt -o "src/baruwa/locale/${locale}/LC_MESSAGES/django.mo" "src/baruwa/locale/${locale}/LC_MESSAGES/django.po";
msgfmt -o "src/baruwa/locale/${locale}/LC_MESSAGES/djangojs.mo" "src/baruwa/locale/${locale}/LC_MESSAGES/djangojs.po";
done

%build
%{__python} setup.py build
cd docs
mkdir -p build/html
mkdir -p source/_static
%{__make} html
%{__rm}  -rf build/html/.buildinf


%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__install} -d -p $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
%{__install} -p -m0644 src/baruwa/settings.py $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/settings.py
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__chmod} 0755 $RPM_BUILD_ROOT%{python_sitelib}/%{name}/manage.py
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/cron.d
%{__install} -d $RPM_BUILD_ROOT%{_initrddir}
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/cron.monthly
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%{__install} -d $RPM_BUILD_ROOT%{_datadir}/%{name}/CustomFunctions
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/MailScanner/conf.d
%{__install} -d $RPM_BUILD_ROOT%{_sysconfdir}/MailScanner/signatures/{users,domains}/{html,text,imgs}
%{__install} -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
%{__install} -d $RPM_BUILD_ROOT%{_localstatedir}/run/%{name}
%{__install} -d $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
%{__install} -p -m0644 extras/*.pm $RPM_BUILD_ROOT%{_datadir}/%{name}/CustomFunctions
%{__install} -p -m0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
%{__install} -p -m0644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/MailScanner/conf.d/%{name}.conf
%{__install} -p -m0755 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/%{name}
%{__install} -p -m0755 %{SOURCE4} $RPM_BUILD_ROOT%{_initrddir}/%{name}
%{__install} -p -m0755 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/cron.monthly/%{name}
%{__install} -p -m0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -m0644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/%{name}
%{__sed} -i -e "s:/usr/lib/python2.4/site-packages:%{python_sitelib}:g" \
$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name} \
$RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
%{__install} -p -m0644 %{name}.logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}
%{__rm} -f $RPM_BUILD_ROOT%{python_sitelib}/%{name}/settings.py*
pushd $RPM_BUILD_ROOT%{python_sitelib}/%{name}
ln -s ../../../../../etc/baruwa/settings.py .
popd
pushd $RPM_BUILD_ROOT%{python_sitelib}/%{name}/static/js
ln -s ../../../../../../share/dojo/dojo .
ln -s ../../../../../../share/dojo/dojox .
ln -s ../../../../../../share/dojo/dijit .
popd 
(cd $RPM_BUILD_ROOT && find . -name 'django*.mo') | %{__sed} -e 's|^.||' | %{__sed} -e \
  's:\(.*/locale/\)\([^/_]\+\)\(.*\.mo$\):%lang(\2) \1\2\3:' \
  >> %{name}.lang
find $RPM_BUILD_ROOT -name "*.po" | xargs rm -f

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pre
getent group celeryd >/dev/null || groupadd -r celeryd
getent passwd celeryd >/dev/null || \
        useradd -r -g celeryd -d %{_localstatedir}/lib/%{name} \
        -s /sbin/nologin -c "Celeryd user" celeryd
exit 0

%post
/sbin/chkconfig --add %{name}

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README UPGRADE docs/build/html docs/source
%config(noreplace) %{_sysconfdir}/%{name}/settings.py
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/MailScanner/conf.d/%{name}.conf
%{_initrddir}/%{name}
%{_bindir}/*
%dir %{python_sitelib}/%{name}
%{python_sitelib}/%{name}*.egg-info
%{python_sitelib}/%{name}/*.py*
%{python_sitelib}/%{name}/*.wsgi
%{python_sitelib}/%{name}/messages
%{python_sitelib}/%{name}/lists
%{python_sitelib}/%{name}/status
%{python_sitelib}/%{name}/reports
%{python_sitelib}/%{name}/config
%{python_sitelib}/%{name}/static
%{python_sitelib}/%{name}/utils
%{python_sitelib}/%{name}/accounts
%{python_sitelib}/%{name}/auth
%{python_sitelib}/%{name}/templates
%{_datadir}/%{name}/
%dir %{_sysconfdir}/%{name}
%{_sysconfdir}/cron.daily/%{name}
%{_sysconfdir}/cron.monthly/%{name}
%exclude %{_sysconfdir}/%{name}/settings.pyc
%exclude %{_sysconfdir}/%{name}/settings.pyo
%attr(0755,celeryd,celeryd) %{_sysconfdir}/MailScanner/signatures
%attr(0700,celeryd,celeryd) %{_localstatedir}/lib/%{name}
%attr(0700,celeryd,celeryd) %{_localstatedir}/run/%{name}
%attr(0700,celeryd,celeryd) %{_localstatedir}/log/%{name}


%changelog
* Thu Sep 15 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-9
- FEATURE: Support Email Signatures/Disclaimer management
- FEATURE: Added migrations support

* Fri Aug 26 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-8
- FIX: logging of number of settings read from DB

* Fri Aug 26 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-7
- FIX: Silence depreciation errors in cron
- FIX: exception in top hosts report
- FIX: postfix queue manager not picking up some messages
- FIX: increase the character length of spamassassin rules
- FIX: make sa learn command more portable across various os's
- FIX: cleanly handle sa learn exceptions
- FIX: SMTP server tests failing
- FIX: add base tag to the tags sanitized by the previewer
- FIX: logging to both mysql and sqlite
- FIX: IE8 caching ajax requests
- FIX: celery jobs hanging and not returning results
- FEATURE: support alternative postfix configuration directory when
  running queuestats
- FEATURE: support default filter to only show todays messages
- Update language translations
- Make InnoDB the default engine
- Improve error handling in the perl modules

* Mon Aug 01 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-6
- Depend on mod_wsgi
- move cron.d out of spec
- build fro Fedora 15

* Mon Jul 18 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-5
- FIX: EL6 sysconfig python site lib path
- FIX: Exception on viewing top hosts

* Tue Jun 28 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-4
- FIX: baruwa celeryd worker pid path

* Sat Jun 25 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-3
- Build for RHEL6
- FIX: mailscanner requires version
- FIX: mailq status localization
- FIX: Exception handling ip's with ports in relayed_via
- FIX: Decode internationalized attachment names
- FIX: Handle XHTML with encodings
- FIX: Log message subject in unicode

* Wed Jun 22 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-2
- fix celery worker pid path

* Wed Apr 27 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.1.0-1
- upgrade to latest version

* Sat Apr 23 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.2-4
 - FIX: exchange duplicate delivery suppression blocks releases
 - FIX: some RBL names not being displayed

* Thu Apr 14 2011 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.2-3
- Fix mailauth exception

* Sat Feb 22 2011 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.2-2
- Fix CSRF protection issues preventing users of Django 1.x.x from
  performing Ajax POST operations.

* Sat Feb 19 2011 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.2-1
- upgrade to the latest version

* Mon Feb 06 2011 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.1-2
- fix the annotation regression introduced by django 1.2.4
- fix the js alert and redirection on the login page

* Wed Dec 29 2010 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.1-1
- upgrade to latest version

* Sun Nov 21 2010 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.0-3
- Various bug fixes

* Fri Oct 29 2010 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.0-2
- remove MySQL-python as dependency as installing from source

* Tue Oct 26 2010 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.0-1
- Upgrade to latest version

* Wed Jun 30 2010 Andrew Colin Kissa <andrew@topdog.za.net> 1.0.0-0.1.a
- Upgrade to latest version

* Tue May 11 2010 Andrew Colin Kissa <andrew@topdog.za.net> 0.0.1-0.3.rc1
- update to latest version

* Mon Apr 05 2010 Andrew Colin Kissa <andrew@topdog.za.net> 0.0.1-0.2.b
- update to latest version

* Fri Mar 26 2010 Andrew Colin Kissa <andrew@topdog.za.net> 0.0.1-0.1.a
- Initial packaging
