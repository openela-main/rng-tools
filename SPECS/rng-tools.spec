%global _hardened_build 1

Summary:        Random number generator related utilities
Name:           rng-tools
Version:        6.15
Release:        3%{?dist}
Group:          System Environment/Base
License:        GPLv2+
URL:            https://github.com/nhorman/rng-tools
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        rngd.service
Source2:        rngd.sysconfig
Source3:        jitterentropy-library-3.4.1.tar.gz

BuildRequires: gcc make binutils
BuildRequires: gettext
BuildRequires: systemd systemd-rpm-macros
BuildRequires: autoconf >= 2.57, automake >= 1.7
BuildRequires: libgcrypt-devel libcurl-devel
BuildRequires: libxml2-devel openssl-devel
BuildRequires: jansson-devel
BuildRequires: libcap-devel

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

# This ensures that the selinux-policy package and all its dependencies
# are not pulled into containers and other systems that do not use SELinux.
Requires: (selinux-policy >= 3.14.3-98 if selinux-policy)

Patch0: 1-je-rh-makefile.patch
Patch1: 2-je-remove-install.patch
Patch2: 3-rt-use-jitter-static.patch
Patch3: 4-rt-comment-out-have-aesni.patch
Patch4: 5-rt-revert-build-randstat.patch

%description
This is a random number generator daemon and its tools. It monitors
a set of entropy sources present on a system (like /dev/hwrng, RDRAND,
TPM, jitter) and supplies entropy from them to a kernel entropy pool.

%prep
%setup -q
tar xf %{SOURCE3}
mv jitterentropy-library-3.4.1 jitterentropy-library
%autopatch -p0

%build
./autogen.sh
# a dirty hack so libdarn_impl_a_CFLAGS overrides common CFLAGS
sed -i -e 's/$(libdarn_impl_a_CFLAGS) $(CFLAGS)/$(CFLAGS) $(libdarn_impl_a_CFLAGS)/' Makefile.in
%configure --without-pkcs11 --without-rtlsdr
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
- Update rng-tools to v6.15 @ cb8cc624 (bz 2141379)
- Update jitterentropy library to v3.4.1 @ 7bf9f85d
- Fix a stack corruption on s390x
- Fix a number of issues found by covscan code scanner
- Add a jitter init timeout for tests
- Add a start condition for the FIPS mode (bz 2154804)

* Tue Oct 04 2022 Vladis Dronov <vdronov@redhat.com> - 6.15-2
- Update rng-tools to v6.15 @ 6dcc9ec2 (bz 2124602)
- Update jitterentropy library to v3.4.1 @ 4544e113
- Do not require selinux-policy if it is not present

* Sat Apr 16 2022 Vladis Dronov <vdronov@redhat.com> - 6.15-1
- Update rng-tools to v6.15 @ 172bf0e3 (bz 2075974)
- Update jitterentropy library to v3.4.0 @ 887c9871
- Allow rngd process to drop privileges with "-D user:group"
- Fix an error building with jitterentropy-3.4.0
- Add a requirement for selinux-policy of a certain version
- Fix a build failure on ppc64
- Small edits in test scripts

* Mon Nov 22 2021 Vladis Dronov <vdronov@redhat.com> - 6.14-4.git.b2b7934e
- Update rng-tools to v6.14 @ b2b7934e (bz 2015570)
- Update jitterentropy library to v3.3.1 @ 887c9871
- Add a config file for storing rngd options
- Fix a security issue found by a covscan in jitterentropy library

* Thu Jul 22 2021 Vladis Dronov <vdronov@redhat.com> - 6.13-1.git.d207e0b6
- Update to the upstream v6.13 + tip of origin/master + onecpu
  branch + revert of 2ce93190
- Rebuild rng-tools against the latest jitterentropy library
  3.0.2-2.git.409828cf with fixes for an important issue
- Fix a number of issues (bz 1974103, bz 1980421, bz 1859154)

* Mon Jul 05 2021 Vladis Dronov <vdronov@redhat.com> - 6.8-6
- Adjust rngd-wake-threshold.service and post section so udevadm is not
  run in a container (bz 1975554)

* Thu May 27 2021 Vladis Dronov <vdronov@redhat.com> - 6.8-5
- Fix /dev/hwrng permissions issue at boot time (bz 1955522)

* Mon May 24 2021 Vladis Dronov <vdronov@redhat.com> - 6.8-4
- There is no need to hardcode _sbindir anymore, also the old value is
  incorrect
- Update the rngd.service file
- Fix a busyloop bug (bz 1956248)
- Fix /dev/hwrng permission issue (bz 1955522)

* Tue Feb 18 2020 Neil Horman <nhorman@redhat.com> - 6.8-3
- Fix coarse clock time on Azure (bz 180155)

* Mon Dec 02 2019 Neil Horman <nhorman@redhat.com> - 6.8-2
- Fix erroneous message due to bad errno check (bz 1776710)
- Enable addition of 0 value for fill-watermark (bz 1776710)

* Fri Nov 15 2019 Neil Horman <nhorman@redhat.com> - 6.8-1
- Update to latest upstream (bz 1769916)

* Wed Oct 09 2019 Neil Horman <nhorman@redhat.com> 6.6-5
- Fix group typo in rngd.service (bz 1751810)

* Fri Oct 04 2019 Neil Horman <nhorman@redhat.com> 6.6-4
- Revision bump to rebuild for new CI runs

* Mon Mar 25 2019 Neil Horman <nhorman@redhat.com> 6.2-3
- Allow rngd to run as non-privledged user (bz 1692435)

* Mon Dec 17 2018 Neil Horman <nhorman@redhat.com> 6.2-2
- default to 1 thread on cpu 0 if getaffinty returns error (bz 1658855)

* Thu May 17 2018 Neil Horman <nhorman@redhat.com> 6.2-1
- Update to latest upstream
- Add CI self tests

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
