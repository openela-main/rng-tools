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
Version:        6.17
Release:        5%{?dist}
License:        GPL-2.0-or-later
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
Suggests: opensc
%endif

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

# This ensures that the selinux-policy package and all its dependencies
# are not pulled into containers and other systems that do not use SELinux.
Requires: (selinux-policy >= 36.5 if selinux-policy)

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
# a dirty hack to force PIC for a PIC-aware assembly code for i686
# /usr/lib/rpm/redhat/redhat-hardened-cc1 in Koji/Brew does not
# force PIC for assembly sources as of now
%ifarch i386 i686
sed -i -e '/^#define RDRAND_RETRY_LIMIT\t10/a#define __PIC__ 1' rdrand_asm.S
%endif
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
* Thu Jun 26 2025 Vladis Dronov <vdronov@redhat.com> - 6.17-5
- Disable jitter entropy source by default (RHEL-91113)

* Tue Oct 29 2024 Troy Dawson <tdawson@redhat.com> - 6.17-4
- Bump release for October 2024 mass rebuild:
  Resolves: RHEL-64018

* Mon Jun 24 2024 Troy Dawson <tdawson@redhat.com> - 6.17-3
- Bump release for June 2024 mass rebuild

* Wed Jun 19 2024 Vladis Dronov <vdronov@redhat.com> - 6.17-2
- Add Intel CET IBT instrumentation to assembly code
- Update to the upstream v6.17 @ ac43f912 (RHEL-36771)

* Wed Jun 05 2024 Vladis Dronov <vdronov@redhat.com> - 6.17-1
- Update to the upstream v6.17 @ 2160b9c3 (RHEL-36771)

* Sat Mar 30 2024 Vladis Dronov <vdronov@redhat.com> - 6.16-7
- Update to the upstream v6.16 + tip of origin/master @ 98cf8d63

* Fri Jan 26 2024 Vladis Dronov <vdronov@redhat.com> - 6.16-6
- Initial import from Fedora 40
