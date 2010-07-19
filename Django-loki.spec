# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           Django-loki
Version:        0.8.0
Release:        3%{?dist}
Summary:        A Django web interface to manage Buildbots

Group:          Applications/Internet
License:        GPL3
URL:            https://fedorahosted.org/loki
Source0:        https://fedorahosted.org/released/loki/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
Requires:       Django, PyYAML, python-docutils, buildbot


%description
A Django web interface to manage Buildbots


%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_usr}/share/django/apps/loki


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING LICENSE
%dir %{_datadir}/django/apps/loki/
%{_datadir}/django/apps/loki/*
%{python_sitelib}/*egg-info

%changelog
* Fri Jul 16 2010 Dan Radez <dradez@redhat.com> - 0.8.0-3
- handling the egg info according to fedora packageing guidlines and releasing the 0.8.0 version

* Wed Jul 14 2010 Dan Radez <dradez@redhat.com> - 0.7.2-2
- added ghost for egg info

* Wed Jul 14 2010 Dan Radez <dradez@redhat.com> - 0.7.2-1
- updates and cleanup for packaging in fedora, distributed node support and bug fixes

* Tue Nov 24 2009 Dan Radez <dradez@redhat.com> - 0.6.0-1
- Initial spec for loki rewrite
