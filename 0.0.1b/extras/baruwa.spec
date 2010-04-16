%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name:           baruwa
Version:        0.0.1
Release:        0.2.b%{?dist}
Summary:        Ajax enabled MailScanner web frontend      
Group:          Development/Languages
License:        GPLv2
URL:            http://www.topdog.za.net/baruwa
Source0:        http://www.topdog-software.com/oss/files/%{name}-%{version}b.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools, python-sphinx
Requires:       Django >= 1.1.1, MySQL-python, python-GeoIP, python-IPy, httpd

%description
Baruwa is a mailwatch inspired web 2.0 MailScanner frontend
It provides an easy to use interface for users to view details
of messages processed by MailScanner as well as perform
operations such as releasing quarantined messages, spam learning,
whitelisting and blacklisting addresses etc.

It also provides reporting functionality with an easy to use
query builder, results are displayed in colorful graphs and
charts.

%prep
%setup -q -n %{name}-%{version}b


%build
%{__python} setup.py build
cd docs
%{__make} html


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
%{__chmod} 0755 $RPM_BUILD_ROOT%{python_sitelib}/%{name}/manage.py
%{__install} -d -p $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
%{__install} -p -m0644 extras/baruwa-mod_wsgi.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/%{name}.conf

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS LICENSE README BSD-LICENSE NOTICE extras/*.sql extras/*.pm docs/build/html docs/source
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{python_sitelib}/*


%changelog
* Mon Apr 05 2010 Andrew Colin Kissa <andrew@topdog.za.net> 0.0.1-0.2.b
- update to latest version

* Fri Mar 26 2010 Andrew Colin Kissa <andrew@topdog.za.net> 0.0.1-0.1.a
- Initial packaging
