%global _hardened_build 1

# this is a correct if, bcond_with actually means without and vice versa
%if 0%{?rhel} && 0%{?rhel} >= 9
%bcond_with    pkcs11
%bcond_with    rtlsdr
%else
%bcond_without pkcs11
%bcond_without rtlsdr
%endif

Summary:        Random number generator related utilities
Name:           rng-tools
Version:        6.15
Release:        3%{?dist}
License:        GPLv2+
URL:            https://github.com/nhorman/rng-tools
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        rngd.service
Source2:        rngd.sysconfig

BuildRequires: gcc make binutils
BuildRequires: gettext
BuildRequires: systemd systemd-rpm-macros
BuildRequires: autoconf >= 2.57, automake >= 1.7
BuildRequires: libgcrypt-devel libcurl-devel
BuildRequires: libxml2-devel openssl-devel
BuildRequires: jitterentropy-devel
BuildRequires: jansson-devel
BuildRequires: libcap-devel
%if %{with rtlsdr}
BuildRequires: rtl-sdr-devel
%endif
%if %{with pkcs11}
BuildRequires: libp11-devel
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

# This ensures that the selinux-policy package and all its dependencies
# are not pulled into containers and other systems that do not use SELinux.
Requires: (selinux-policy >= 34.1.31-2 if selinux-policy)

Patch0: 1-rt-comment-out-have-aesni.patch
Patch1: 2-rt-revert-build-randstat.patch

%description
This is a random number generator daemon and its tools. It monitors
a set of entropy sources present on a system (like /dev/hwrng, RDRAND,
TPM, jitter) and supplies entropy from them to a kernel entropy pool.

%prep
%autosetup -p0

%build
%if !%{with pkcs11}
%define _without_pkcs11 --without-pkcs11
%endif
%if !%{with rtlsdr}
%define _without_rtlsdr --without-rtlsdr
%endif

./autogen.sh
# a dirty hack so libdarn_impl_a_CFLAGS overrides common CFLAGS
sed -i -e 's/$(libdarn_impl_a_CFLAGS) $(CFLAGS)/$(CFLAGS) $(libdarn_impl_a_CFLAGS)/' Makefile.in
%configure %{?_without_pkcs11} %{?_without_rtlsdr}
%make_build

%install
%make_install

# install systemd unit file
install -Dt %{buildroot}%{_unitdir} -m0644 %{SOURCE1}
# install sysconfig file
install -D %{SOURCE2} -m0644 %{buildroot}%{_sysconfdir}/sysconfig/rngd

%post
%systemd_post rngd.service

%preun
%systemd_preun rngd.service

%postun
%systemd_postun_with_restart rngd.service

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS README.md
%{_bindir}/rngtest
%{_sbindir}/rngd
%{_mandir}/man1/rngtest.1.*
%{_mandir}/man8/rngd.8.*
%attr(0644,root,root)    %{_unitdir}/rngd.service
%config(noreplace) %attr(0644,root,root)    %{_sysconfdir}/sysconfig/rngd

%changelog
* Tue Dec 27 2022 Vladis Dronov <vdronov@redhat.com> - 6.15-3
- Update to the upstream v6.15 + tip of origin/master @ cb8cc624 (bz 2156554)
- Fix a number of issues found by covscan code scanner
- Add a jitter init timeout for tests
- Add a start condition for the FIPS mode (bz 2154804)

* Tue Oct 04 2022 Vladis Dronov <vdronov@redhat.com> - 6.15-2
- Update to the upstream v6.15 + tip of origin/master @ 6dcc9ec2 (bz 2124605)
- Do not require selinux-policy if it is not present

* Sat Apr 16 2022 Vladis Dronov <vdronov@redhat.com> - 6.15-1
- Update to the upstream v6.15 @ 172bf0e3 (bz 2075977)
- Allow rngd process to drop privileges with "-D user:group"
- Fix an error building with jitterentropy-3.4.0
- Add a requirement for selinux-policy of a certain version
- Fix a build failure on ppc64
- Small edits in test scripts

* Tue Nov 23 2021 Vladis Dronov <vdronov@redhat.com> - 6.14-2.git.b2b7934e
- Update to the upstream v6.14 @ b2b7934e (bz 2015566)
- Add a config file for storing rngd options

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 6.13-6.git.d207e0b6
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jul 27 2021 Vladis Dronov <vdronov@redhat.com> - 6.13-5.git.d207e0b6
- A version bump due to a necessary rebuild.

* Thu Jul 22 2021 Vladis Dronov <vdronov@redhat.com> - 6.13-4.git.d207e0b6
- Update to the upstream v6.13 + tip of origin/master + onecpu
  branch + revert of 2ce93190 (bz 1965318)
- Rebuild rng-tools against the latest jitterentropy library
  3.0.2-2.git.409828cf with fixes for an important issue
- Adjust Source0 to a more proper one

* Mon Jul 05 2021 Vladis Dronov <vdronov@redhat.com> - 6.13-3
- Adjust rngd-wake-threshold.service and post section so udevadm
  is not run in a container (bz 1965318)

* Thu Jun 17 2021 Mohan Boddu <mboddu@redhat.com> - 6.13-2
- Specbump for openssl 3.0
  Related: rhbz#1971065

* Wed Jun 16 2021 Vladis Dronov <vdronov@redhat.com> - 6.13-1
- Update the sources to 6.13
- Add important fixes from the upstream
- Remove Provides: jitterentropy-rngd as it was retired in f29.

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 6.12-5
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Mon May 24 2021 Vladis Dronov <vdronov@redhat.com> - 6.12-4
- Allow rngd to run as non-privledged user (bz 1965318)
- Update the rngd.service file
- Add 3 small upstream patches fixing issues

* Wed Apr 28 2021 Vladis Dronov <vdronov@redhat.com> - 6.12-3
- There is no need to hardcode _sbindir anymore, also the old
  value is incorrect (bz 1965318)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 6.12-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021.
  Related: rhbz#1947937

* Fri Mar 12 2021 Vladis Dronov <vdronov@redhat.com> - 6.12-1
- Update to 6.12
- Drop libsysfs dependency since it is not used anymore
- Remove jitterentropy-remove-install.patch since we depend on
  a system jitterentropy library now
- Remove rngd-shutdown.patch since it is the upstream commit 62fbff0a
- Remove rngd-exit-code-for-list.patch since it is the upstream commit
  fb46dc48
- Remove pkcs11-path.patch since it is the upstream commit 1993eca9

* Tue Mar 02 2021 Vladis Dronov <vdronov@redhat.com> - 6.11-3
- Replace outdated systemd-units

* Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 6.11-2
- Rebuilt for updated systemd-rpm-macros
  See https://pagure.io/fesco/issue/2583.

* Fri Jan 29 2021 Dan Horák <dan[at]danny.cz> - 6.11-1
- Update to 6.11

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 6.10-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Nov 16 2020 Vladis Dronov <vdronov@redhat.com> - 6.10-7
- Make rtl-sdr optional
- For RHEL9 and above, do not build with rtl-sdr

* Mon Oct 05 2020 Troy Dawson <tdawson@redhat.com> - 6.10-6
- Make pkcs11 optional
- For RHEL9 and above, do not build with pkcs11

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.10-5
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Mar 27 2020 Neil Horman <nhorman@redhat.com> - 6.10-3
- Fix missing buildrequires

* Fri Mar 27 2020 Neil Horman <nhorman@redhat.com> - 6.10-2
- Fix missing buildrequires

* Fri Mar 27 2020 Neil Horman <nhorman@redhat.com> - 6.10-1
- Update to latest upstream

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 13 2020 Neil Horman <nhorman@redhat.com> - 6.9-2
- Correct default pkcs11 path on 32 bit arch (bz 1788083)

* Tue Dec 17 2019 Neil Horman <nhorman@redhat.com> - 6.9-1
- update to latest upstream

* Mon Aug 05 2019 Volker Froehlich <volker27@gmx.at> - 6.7-4
- Remove explicit Requires for libraries

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 6.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri May 24 2019 Neil Horman <nhorman@redhat.com> -6.7-2
- Fix race in shutdown leading to hang (bz 1690364)
- bump version number

* Thu Feb 14 2019 Neil Horman <nhorman@redhat.com> - 6.7-1
- Update to latest upstream

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 6.3.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Oct 01 2018 Neil Horman <nhorman@redhat.com> - 6.3.1-2
- Add Provides for jitterentropy-rngd (bz 1634788)

* Mon Jul 16 2018 Neil Horman <nhorman@redhat.com> - 6.3.1-1
- Update to latest upstream

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jul 06 2018 Neil Horman <nhorman@redhat.com> - 6.3-1
- update to latest upstream (#1598608)

* Thu May 10 2018 Neil Horman <nhorman@redhat.com>
- Update to latest upstream

* Thu Feb 15 2018 Adam Williamson <awilliam@redhat.com> - 6.1-4
- Drop all attempts to 'fix' #1490632, revert spec to same as 6.1-1

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Nov 02 2017 Neil Horman <nhorman@redhat.com> - 6.1-2
- Enable rngd on entropy src availability (bz 1490632)

* Tue Oct 10 2017 Neil Horman <nhorman@redhat.com> - 6.1-1
- update to latest upstream

* Fri Jul 28 2017 Neil Horman <nhorman@redhat.com> - 6-1
- Update to latest upstream

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 5-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Oct 18 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 5-8
- If device is not found exit immediately (#892178)

* Sun Mar  6 2016 Peter Robinson <pbrobinson@fedoraproject.org> 5-7
- Use %%license

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Dec 10 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 5-4
- Build with hardening flags (#1051344)
- Fail nicely if no hardware generator is found (#892178)
- Drop unneeded dependency

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 23 2014 Luke Macken <lmacken@redhat.com> - 5-1
- Update to release version 5.
- Remove rng-tools-man.patch

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Sep 25 2012 Jaromir Capik <jcapik@redhat.com> - 4-2
- Migration to new systemd macros

* Mon Aug 6 2012 Jeff Garzik <jgarzik@redhat.com> - 4-1
- Update to release version 4.

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 12 2012 Jiri Popelka <jpopelka@redhat.com> - 3-4
- 2 patches from RHEL-6
- systemd service
- man page fixes
- modernize spec file

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jul  3 2010 Jeff Garzik <jgarzik@redhat.com> - 3-2
- comply with renaming guidelines, by Providing rng-utils = 1:2.0-4.2

* Sat Jul  3 2010 Jeff Garzik <jgarzik@redhat.com> - 3-1
- Update to release version 3.

* Fri Mar 26 2010 Jeff Garzik <jgarzik@redhat.com> - 2-3
- more minor updates for package review

* Thu Mar 25 2010 Jeff Garzik <jgarzik@redhat.com> - 2-2
- several minor updates for package review

* Wed Mar 24 2010 Jeff Garzik <jgarzik@redhat.com> - 2-1
- initial revision (as rng-tools)
