%global dist .el7

# For the curious:
# 0.9.5a soversion = 0
# 0.9.6  soversion = 1
# 0.9.6a soversion = 2
# 0.9.6c soversion = 3
# 0.9.7a soversion = 4
# 0.9.7ef soversion = 5
# 0.9.8ab soversion = 6
# 0.9.8g soversion = 7
# 0.9.8jk + EAP-FAST soversion = 8
# 1.0.0 soversion = 10
# 1.0.2 soversion = 10

%define soversion 1.1

# Number of threads to spawn when testing some threading fixes.
%define thread_test_threads %{?threads:%{threads}}%{!?threads:1}

# Arches on which we need to prevent arch conflicts on opensslconf.h, must
# also be handled in opensslconf-new.h.
%define multilib_arches %{ix86} ia64 %{mips} ppc ppc64 s390 s390x sparcv9 sparc64 x86_64

%global _performance_build 1

%global _prefix                /usr/local/openssl-1.1.1
%global _exec_prefix           %{_prefix}
%global _bindir                %{_exec_prefix}/bin
%global _sbindir               %{_exec_prefix}/sbin
%global _libexecdir            %{_exec_prefix}/libexec
%global _datadir               %{_prefix}/share
%global _sysconfdir            /usr/local/openssl-1.1.1/etc
%global _sharedstatedir        %{_prefix}/com
%global _localstatedir         %{_prefix}/var
%global _lib                   lib
%global _libdir                %{_exec_prefix}/%{_lib}
%global _includedir            %{_prefix}/include
%global _infodir               %{_datadir}/info
%global _mandir                %{_datadir}/man


Summary: Utilities from the general purpose cryptography library with TLS implementation
Name: openssl1.1
Version: 1.1.1X
Release: 1%{?dist}
Epoch: 1
# We have to remove certain patented algorithms from the openssl source
# tarball with the hobble-openssl script which is included below.
# The original openssl upstream tarball cannot be shipped in the .src.rpm.
Source: openssl1.1-1.1.1X.tar.gz
Source2: Makefile.certificate
Source6: make-dummy-cert
Source7: renew-dummy-cert
# Build changes
# Bug fixes
# Functionality changes
# Backported fixes including security fixes

License: OpenSSL
Group: System Environment/Libraries
URL: https://www.openssl.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: coreutils, krb5-devel, perl, sed, zlib-devel, /usr/bin/cmp
BuildRequires: lksctp-tools-devel
BuildRequires: /usr/bin/rename
BuildRequires: /usr/bin/pod2man
Requires: coreutils, make
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}

%description
The OpenSSL toolkit provides support for secure communications between
machines. OpenSSL includes a certificate management tool and shared
libraries which provide various cryptographic algorithms and
protocols.

%package libs
Summary: A general purpose cryptography library with TLS implementation
Group: System Environment/Libraries
Requires: ca-certificates >= 2008-5
# Needed obsoletes due to the base/lib subpackage split
Obsoletes: openssl < 1:1.0.1-0.3.beta3

%description libs
OpenSSL is a toolkit for supporting cryptography. The openssl-libs
package contains the libraries that are used by various applications which
support cryptographic algorithms and protocols.

%package devel
Summary: Files for development of applications which will use OpenSSL
Group: Development/Libraries
Requires: %{name}-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: krb5-devel%{?_isa}, zlib-devel%{?_isa}
Requires: pkgconfig

%description devel
OpenSSL is a toolkit for supporting cryptography. The openssl-devel
package contains include files needed to develop applications which
support various cryptographic algorithms and protocols.

%package static
Summary:  Libraries for static linking of applications which will use OpenSSL
Group: Development/Libraries
Requires: %{name}-devel%{?_isa} = %{epoch}:%{version}-%{release}

%description static
OpenSSL is a toolkit for supporting cryptography. The openssl-static
package contains static libraries needed for static linking of
applications which support various cryptographic algorithms and
protocols.

%package perl
Summary: Perl scripts provided with OpenSSL
Group: Applications/Internet
Requires: perl
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}

%description perl
OpenSSL is a toolkit for supporting cryptography. The openssl-perl
package provides Perl scripts for converting certificates and keys
from other formats to the formats used by the OpenSSL toolkit.

%prep
%setup -q -n %{name}-%{version}

#sed -i 's/SHLIB_VERSION_NUMBER "1.0.0"/SHLIB_VERSION_NUMBER "%{version}"/' crypto/opensslv.h
#sed -i 's/SHLIB_VERSION_NUMBER "1.1"/SHLIB_VERSION_NUMBER "%{version}"/' include/openssl/opensslv.h

# Modify the various perl scripts to reference perl in the right location.
#perl util/perlpath.pl `dirname %{__perl}`

# Generate a table with the compile settings for my perusal.
#touch Makefile
#make TABLE PERL=%{__perl}

%build
# Figure out which flags we want to use.
# default
sslarch=%{_os}-%{_target_cpu}
%ifarch %ix86
sslarch=linux-elf
if ! echo %{_target} | grep -q i686 ; then
	sslflags="no-asm 386"
fi
%endif
%ifarch x86_64
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch sparcv9
sslarch=linux-sparcv9
sslflags=no-asm
%endif
%ifarch sparc64
sslarch=linux64-sparcv9
sslflags=no-asm
%endif
%ifarch alpha alphaev56 alphaev6 alphaev67
sslarch=linux-alpha-gcc
%endif
%ifarch s390 sh3eb sh4eb
sslarch="linux-generic32 -DB_ENDIAN"
%endif
%ifarch s390x
sslarch="linux64-s390x"
%endif
%ifarch %{arm}
sslarch=linux-armv4
%endif
%ifarch aarch64
sslarch=linux-aarch64
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch sh3 sh4
sslarch=linux-generic32
%endif
%ifarch ppc64 ppc64p7
sslarch=linux-ppc64
%endif
%ifarch ppc64le
sslarch="linux-ppc64le"
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch mips mipsel
sslarch="linux-mips32 -mips32r2"
%endif
%ifarch mips64 mips64el
sslarch="linux64-mips64 -mips64r2"
%endif
%ifarch mips64el
sslflags=enable-ec_nistp_64_gcc_128
%endif
%ifarch riscv64
sslarch=linux-generic64
%endif

# ia64, x86_64, ppc are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.
#./Configure \
#	--prefix=%{_prefix} --openssldir=%{_sysconfdir}/pki/tls ${sslflags} \
#	zlib sctp enable-camellia enable-seed enable-tlsext enable-rfc3779 \
#	enable-cms enable-md2 enable-rc5 \
#	no-mdc2 no-ec2m no-gost no-srp \
#	--with-krb5-flavor=MIT --enginesdir=%{_libdir}/openssl/engines \
#	--with-krb5-dir=/usr shared  ${sslarch} %{?!nofips:fips}

CC='gcc'
export CC
CXX='g++'
export CXX
LDFLAGS="-Wl,-z,relro -Wl,--as-needed -Wl,-z,now -Wl,-rpath,%{_exec_prefix}/%{_lib}"
export LDFLAGS

# Add -Wa,--noexecstack here so that libcrypto's assembler modules will be
# marked as not requiring an executable stack.
# Also add -DPURIFY to make using valgrind with openssl easier as we do not
# want to depend on the uninitialized memory as a source of entropy anyway.
RPM_OPT_FLAGS="$RPM_OPT_FLAGS -Wa,--noexecstack -DPURIFY"

export HASHBANGPERL=/usr/bin/perl

# openssl-1.1.1-no-html.patch
sed 's|^install_docs: install_man_docs install_html_docs|install_docs: install_man_docs|g' -i Configurations/unix-Makefile.tmpl

# ia64, x86_64, ppc are OK by default
# Configure the build tree.  Override OpenSSL defaults with known-good defaults
# usable on all platforms.  The Configure script already knows to use -fPIC and
# RPM_OPT_FLAGS, so we can skip specifiying them here.

./Configure \
    --prefix=%{_prefix} \
    --openssldir=%{_sysconfdir}/pki/tls \
    zlib enable-tls1_3 threads shared \
    enable-camellia enable-seed enable-rfc3779 \
    enable-sctp enable-cms enable-md2 enable-rc5 \
    no-mdc2 no-ec2m \
    no-sm2 no-sm3 no-sm4 \
    enable-ec_nistp_64_gcc_128 \
    ${sslarch} $RPM_OPT_FLAGS '-DDEVRANDOM="\"/dev/urandom\""' 

sed 's@engines-1.1@engines@g' -i Makefile

make all

# Generate hashes for the included certs.
#make rehash

# Clean up the .pc files
for i in libcrypto.pc libssl.pc openssl.pc ; do
  sed -i '/^Libs.private:/{s/-L[^ ]* //;s/-Wl[^ ]* //}' $i
done

%check
# Verify that what was compiled actually works.

LD_LIBRARY_PATH=`pwd`${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_LIBRARY_PATH
OPENSSL_ENABLE_MD5_VERIFY=
export OPENSSL_ENABLE_MD5_VERIFY
#make -C test apps tests
#%{__cc} -o openssl-thread-test \
#	`krb5-config --cflags` \
#	-I./include \
#	$RPM_OPT_FLAGS \
#	%{SOURCE8} \
#	-L. \
#	-lssl -lcrypto \
#	`krb5-config --libs` \
#	-lpthread -lz -ldl
#./openssl-thread-test --threads %{thread_test_threads}

# Add generation of HMAC checksum of the final stripped library
#%define __spec_install_post \
#    %{?__debug_package:%{__debug_install_post}} \
#    %{__arch_install_post} \
#    %{__os_install_post} \
#    crypto/fips/fips_standalone_hmac $RPM_BUILD_ROOT%{_libdir}/libcrypto.so.%{version} >$RPM_BUILD_ROOT%{_libdir}/.libcrypto.so.%{version}.hmac \
#    ln -sf .libcrypto.so.%{version}.hmac $RPM_BUILD_ROOT%{_libdir}/.libcrypto.so.%{soversion}.hmac \
#   crypto/fips/fips_standalone_hmac $RPM_BUILD_ROOT%{_libdir}/libssl.so.%{version} >$RPM_BUILD_ROOT%{_libdir}/.libssl.so.%{version}.hmac \
#    ln -sf .libssl.so.%{version}.hmac $RPM_BUILD_ROOT%{_libdir}/.libssl.so.%{soversion}.hmac \
#%{nil}

%define __provides_exclude_from %{_libdir}/openssl

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
# Install OpenSSL.
install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir},%{_libdir},%{_mandir},%{_libdir}/openssl}
make DESTDIR=$RPM_BUILD_ROOT install
rm -fr $RPM_BUILD_ROOT%{_libdir}/openssl
rm -fr $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/man
#rename so.%{soversion} so.%{version} $RPM_BUILD_ROOT%{_libdir}/*.so.%{soversion}
mkdir $RPM_BUILD_ROOT/%{_lib}
#for lib in $RPM_BUILD_ROOT%{_libdir}/*.so.%{version} ; do
#	chmod 755 ${lib}
#	ln -s -f `basename ${lib}` $RPM_BUILD_ROOT%{_libdir}/`basename ${lib} .%{version}`
#	ln -s -f `basename ${lib}` $RPM_BUILD_ROOT%{_libdir}/`basename ${lib} .%{version}`.%{soversion}
#done

for lib in $RPM_BUILD_ROOT%{_libdir}/*.so.%{soversion} ; do
        chmod 0755 ${lib}
        ln -s -f `basename ${lib}` $RPM_BUILD_ROOT%{_libdir}/`basename ${lib} .%{soversion}`
done

# Install a makefile for generating keys and self-signed certs, and a script
# for generating them on the fly.
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/Makefile
install -m 0755 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/make-dummy-cert
install -m 0755 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/renew-dummy-cert

# Make sure we actually include the headers we built against.
for header in $RPM_BUILD_ROOT%{_includedir}/openssl/* ; do
	if [ -f ${header} -a -f include/openssl/$(basename ${header}) ] ; then
		install -m644 include/openssl/`basename ${header}` ${header}
	fi
done

# Rename man pages so that they don't conflict with other system man pages.
#pushd $RPM_BUILD_ROOT%{_mandir}
#ln -s -f config.5 man5/openssl.cnf.5
#for manpage in man*/* ; do
#	if [ -L ${manpage} ]; then
#		TARGET=`ls -l ${manpage} | awk '{ print $NF }'`
#		ln -snf ${TARGET}ssl ${manpage}ssl
#		rm -f ${manpage}
#	else
#		mv ${manpage} ${manpage}ssl
#	fi
#done
#for conflict in passwd rand ; do
#	rename ${conflict} ssl${conflict} man*/${conflict}*
#done
#popd

pushd $RPM_BUILD_ROOT%{_mandir}
ln -s -f config.5 man5/openssl.cnf.5
#for manpage in man*/* ; do
#   if [ -L ${manpage} ]; then
#       #TARGET=`ls -l ${manpage} | awk '{ print $NF }'`
#       #ln -snf ${TARGET}ssl ${manpage}ssl
#       rm -f ${manpage}
#   else
#       #mv ${manpage} ${manpage}ssl
#       echo > /dev/null
#   fi
#done
#for conflict in passwd rand ; do
#   rename ${conflict} ssl${conflict} man*/${conflict}*
#done
popd

# Pick a CA script.
pushd  $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/misc
#mv CA.sh CA
popd

# Ensure the openssl.cnf timestamp is identical across builds to avoid
# mulitlib conflicts and unnecessary renames on upgrade
#touch -r %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/openssl.cnf
touch -r $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/openssl.cnf $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/Makefile
touch -r $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/openssl.cnf $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/make-dummy-cert
touch -r $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/openssl.cnf $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/renew-dummy-cert
ln -sf /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/ca-bundle.crt
ln -sf /etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/certs/ca-bundle.trust.crt
ln -sf /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem $RPM_BUILD_ROOT%{_sysconfdir}/pki/tls/cert.pem

# Determine which arch opensslconf.h is going to try to #include.
basearch=%{_arch}
%ifarch %{ix86}
basearch=i386
%endif
%ifarch sparcv9
basearch=sparc
%endif
%ifarch sparc64
basearch=sparc64
%endif

#%ifarch %{multilib_arches}
# Do an opensslconf.h switcheroo to avoid file conflicts on systems where you
# can have both a 32- and 64-bit version of the library, and they each need
# their own correct-but-different versions of opensslconf.h to be usable.
#install -m644 %{SOURCE10} \
#	$RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf-${basearch}.h
#cat $RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf.h >> \
#	$RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf-${basearch}.h
#install -m644 %{SOURCE9} \
#	$RPM_BUILD_ROOT/%{_prefix}/include/openssl/opensslconf.h
#%endif

# Remove unused files from upstream fips support
rm -rf $RPM_BUILD_ROOT/%{_bindir}/openssl_fips_fingerprint
rm -rf $RPM_BUILD_ROOT/%{_libdir}/fips_premain.*
rm -rf $RPM_BUILD_ROOT/%{_libdir}/fipscanister.*

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc FAQ NEWS README README.FIPS
%{_sysconfdir}/pki/tls/certs/make-dummy-cert
%{_sysconfdir}/pki/tls/certs/renew-dummy-cert
%{_sysconfdir}/pki/tls/certs/Makefile
%attr(0755,root,root) %{_bindir}/openssl
%attr(0644,root,root) %{_mandir}/man1*/*
%exclude %{_mandir}/man1*/*.pl*
%exclude %{_mandir}/man1*/c_rehash*
%exclude %{_mandir}/man1*/rehash*
%exclude %{_mandir}/man1*/tsget*
%exclude %{_mandir}/man1*/openssl-c_rehash*
%exclude %{_mandir}/man1*/openssl-rehash*
%exclude %{_mandir}/man1*/openssl-tsget*
%attr(0644,root,root) %{_mandir}/man5*/*
%attr(0644,root,root) %{_mandir}/man7*/*

%files libs
%defattr(-,root,root)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%dir %{_sysconfdir}/pki/tls
%dir %{_sysconfdir}/pki/tls/certs
%dir %{_sysconfdir}/pki/tls/misc
%dir %{_sysconfdir}/pki/tls/private
%config %{_sysconfdir}/pki/tls/ct_log_list.cnf
%config %{_sysconfdir}/pki/tls/ct_log_list.cnf.dist
%config %{_sysconfdir}/pki/tls/openssl.cnf
%config %{_sysconfdir}/pki/tls/openssl.cnf.dist
%{_sysconfdir}/pki/tls/cert.pem
%{_sysconfdir}/pki/tls/certs/ca-bundle.crt
%{_sysconfdir}/pki/tls/certs/ca-bundle.trust.crt
%attr(0755,root,root) %{_libdir}/libcrypto.so.%{soversion}
%attr(0755,root,root) %{_libdir}/libcrypto.so
%attr(0755,root,root) %{_libdir}/libssl.so.%{soversion}
%attr(0755,root,root) %{_libdir}/libssl.so
%attr(0755,root,root) %{_libdir}/engines

%files devel
%defattr(-,root,root)
%doc CHANGES
%{_prefix}/include/openssl
%attr(0644,root,root) %{_mandir}/man3*/*
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files static
%defattr(-,root,root)
%attr(0644,root,root) %{_libdir}/*.a

%files perl
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/c_rehash
%attr(0644,root,root) %{_mandir}/man1*/*.pl*
%attr(0644,root,root) %{_mandir}/man1*/c_rehash*
%attr(0644,root,root) %{_mandir}/man1*/rehash*
%attr(0644,root,root) %{_mandir}/man1*/tsget*
%attr(0644,root,root) %{_mandir}/man1*/openssl-c_rehash*
%attr(0644,root,root) %{_mandir}/man1*/openssl-rehash*
%attr(0644,root,root) %{_mandir}/man1*/openssl-tsget*
%{_sysconfdir}/pki/tls/misc/*.pl
%{_sysconfdir}/pki/tls/misc/tsget

%post libs
/bin/rm -f /etc/ld.so.conf.d/openssl-1.1.1.conf
/bin/echo '/usr/local/openssl-1.1.1/lib' > /etc/ld.so.conf.d/openssl-1.1.1.conf
/sbin/ldconfig

%postun libs
/bin/rm -f /etc/ld.so.conf.d/openssl-1.1.1.conf
/sbin/ldconfig

