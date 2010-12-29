%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name:           baruwa
Version:        1.0.1
Release:        1%{?dist}
Summary:        Ajax enabled MailScanner web frontend      
Group:          Development/Languages
License:        GPLv2
URL:            http://www.topdog.za.net/baruwa
Source0:        http://www.topdog-software.com/oss/files/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools, python-sphinx
Requires:       Django >= 1.1.1, python-GeoIP, python-IPy, httpd, dojo, mailscanner, python-reportlab, python-lxml, python-uuid, MySQL-python >= 1.2.2

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
%{__sed} -i 's:/usr/lib/python2.4/site-packages:%{python_sitelib}:' extras/baruwa-mod_wsgi.conf

%{__cat} <<'EOF' > %{name}.cron
#!/bin/sh
#
# %{name} - %{version}
#

# send quarantine reports
%{python_sitelib}/%{name}/manage.py sendquarantinereports
# clean quarantine 
%{python_sitelib}/%{name}/manage.py cleanquarantine
# clean up the DB
%{python_sitelib}/%{name}/manage.py dbclean
# update sa rule definitions
%{python_sitelib}/%{name}/manage.py updatesarules
# clean up stale sessions
%{python_sitelib}/%{name}/manage.py cleanup
# update geoip database
perl /usr/share/doc/GeoIP-*/fetch-geoipdata.pl
EOF

%build
%{__python} setup.py build
cd docs
mkdir -p build/html
mkdir -p source/_static
%{__make} html
%{__rm}  -rf build/html/.buildinf


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__chmod} 0755 $RPM_BUILD_ROOT%{python_sitelib}/%{name}/manage.py
%{__install} -d -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
%{__install} -d -p $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily
%{__install} -d -p $RPM_BUILD_ROOT%{_prefix}/lib/MailScanner/MailScanner/CustomFunctions
%{__install} -d -p $RPM_BUILD_ROOT%{_prefix}/lib/%{name}
%{__install} -p -m0644 extras/*.pm $RPM_BUILD_ROOT%{_prefix}/lib/%{name}/
%{__install} -p -m0644 extras/baruwa-mod_wsgi.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf
%{__install} -p -m0755 %{name}.cron $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/%{name}
pushd $RPM_BUILD_ROOT%{python_sitelib}/%{name}/static/js
ln -s ../../../../../../share/dojo/dojo .
ln -s ../../../../../../share/dojo/dojox .
ln -s ../../../../../../share/dojo/dijit .
popd
pushd $RPM_BUILD_ROOT%{_prefix}/lib/MailScanner/MailScanner/CustomFunctions
ln -s ../../../baruwa/BaruwaSQL.pm .
ln -s ../../../baruwa/BaruwaLists.pm .
ln -s ../../../baruwa/BaruwaUserSettings.pm .
popd  
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README UPGRADE docs/build/html docs/source
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{_sysconfdir}/cron.daily/%{name}
%{python_sitelib}/*
%{_prefix}/lib/%{name}/
%{_prefix}/lib/MailScanner/MailScanner/CustomFunctions/BaruwaSQL.pm
%{_prefix}/lib/MailScanner/MailScanner/CustomFunctions/BaruwaLists.pm
%{_prefix}/lib/MailScanner/MailScanner/CustomFunctions/BaruwaUserSettings.pm


%changelog
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
