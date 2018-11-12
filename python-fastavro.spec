# https://fedoraproject.org/wiki/Packaging:DistTag?rd=Packaging/DistTag#Conditionals
%if 0%{?fedora} >= 30
%bcond_with py2
%else
%bcond_without py2
%endif

# Fail only on i686 for some reason. Issue filed upstream:
# https://github.com/tebeka/fastavro/issues/147
%bcond_with tests

%global srcname     fastavro
%global sum     Fast Avro for Python
%global _description %{expand: \
Apache Avro is a data serialization system. The current Python avro package is
packed with features but dog slow. fastavro is less feature complete than avro,
however it is much faster.}

Name:       python-%{srcname}
Version:    0.21.13
Release:    1%{?dist}
Summary:    %{sum}

# https://github.com/tebeka/fastavro/issues/60
# Apache avro is under ASL 2.0
# https://avro.apache.org/docs/1.8.2/api/cpp/html/ResolvingReader_8hh_source.html etc
License:    ASL 2.0
URL:        https://github.com/tebeka/%{srcname}
Source0:    %pypi_source %{srcname}

BuildRequires:  gcc

%description
%{_description}

%if %{with py2}
%package -n python2-%{srcname}
Summary:        %{sum}
BuildRequires:  python2-devel
BuildRequires:  %{py2_dist setuptools}
BuildRequires:  %{py2_dist Cython} >= 0.29
BuildRequires:  %{py2_dist pytest}
BuildRequires:  %{py2_dist numpy}
Requires:       %{py2_dist python-snappy}

%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
%{_description}
%endif


%package -n python3-%{srcname}
Summary:        %{sum}
BuildRequires:  python3-devel
BuildRequires:  %{py3_dist setuptools}
# Not available in < F30 at the moment.
BuildRequires:  %{py3_dist Cython} >= 0.29
BuildRequires:  %{py3_dist pytest}
BuildRequires:  %{py3_dist numpy}
BuildRequires:  %{py3_dist sphinx}
Requires:       %{py3_dist python-snappy}
%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
%{_description}

%package doc
Summary:        %{sum}
%description doc
Documentation for %{name}.

%prep
%autosetup -n %{srcname}-%{version}
rm -rf *.egg-info
# We don't run the flake8 and manifest check tests so we remove this from the
# setup.py file to prevent it from trying to fetch stuff from pypi
sed -i "/tests_require=/d" setup.py

# Remove the already generated C files so we generate them ourselves
find fastavro/ -name "*.c" -print -delete

%build
export FASTAVRO_USE_CYTHON=1
%if %{with py2}
%py2_build
%endif

%py3_build

pushd docs
    PYTHONPATH=../ make html man
    pushd _build/html
        rm .buildinfo -f || exit -1
        sed -i 's/\r$//' objects.inv
        iconv -f iso8859-1 -t utf-8 objects.inv > objects.inv.conv && mv -fv objects.inv.conv objects.inv
    popd
popd


%install
export FASTAVRO_USE_CYTHON=1
%if %{with py2}
%py2_install
%endif

%py3_install

# Install man page
install -v -p -D -m 0644 docs/_build/man/%{srcname}.1 %{buildroot}%{_mandir}/man1/%{srcname}.1 || exit -1

%check
%if %{with tests}
%if %{with py2}
%{__python2} setup.py build_ext --inplace
PYTHONPATH=. pytest-2  tests
%endif

%{__python3} setup.py build_ext --inplace
PYTHONPATH=. pytest-3 tests
%endif

%if %{with py2}
%files -n python2-%{srcname}
%license NOTICE.txt
%{python2_sitearch}/%{srcname}-%{version}-py?.?.egg-info
%{python2_sitearch}/%{srcname}/
%endif

%files -n python3-%{srcname}
%license NOTICE.txt
%{python3_sitearch}/%{srcname}-%{version}-py?.?.egg-info
%{python3_sitearch}/%{srcname}/
%{_bindir}/%{srcname}
%{_mandir}/man1/%{srcname}.*

%files doc
%doc README.md
%license NOTICE.txt
%doc docs/_build/html

%changelog
* Mon Nov 12 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.21.13-1
- Disable py3 on F30+
- Update to latest release
- Use pypi source

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.19.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 0.19.8-2
- Rebuilt for Python 3.7

* Fri Jun 29 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.19.8-1
- Update to 0.19.8

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.19.6-2
- Rebuilt for Python 3.7

* Sat Jun 09 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.19.6-1
- Update to new release
- Tests still failing for i686 so disabling

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.17.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 23 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.17.3-3
- Re-enable tests for testing

* Mon Jan 22 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.17.3-2
- Disable tests temporarily - fail on i686 only. Issue filed upstream.

* Sun Jan 21 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.17.3-1
- Update for review (rhbz#1534787)
- Update to latest upstream release
- Generate separate doc subpackage for docs
- Install man page
- Rectify license
- Fix tests

* Mon Jan 15 2018 Ankur Sinha <ankursinha AT fedoraproject DOT org> - 0.17.1-1
- Initial build
