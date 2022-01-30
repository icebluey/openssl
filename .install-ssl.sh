#!/usr/bin/env bash
export PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
TZ='UTC'; export TZ

cd "$(dirname "$0")"

_VERIFY="$(ls -1 openssl/openssl1.1-libs-1.1*.rpm 2>/dev/null | grep '^openssl/openssl1.1-libs-1.1')"

if [[ -z "${_VERIFY}" ]]; then
    echo
    echo ' no file:  openssl/openssl1.1-libs-1.1*.rpm'
    echo
    exit 1
fi

cd openssl

sha256sum --check sha256sums.txt 2>/dev/null; _rc_status="$?"
if [[ ${_rc_status} != "0" ]]; then
    echo
    printf '\033[01;31m%s\033[m\n' 'Checksum failed' 'Aborted'
    echo
fi

if rpm -qa | grep -i '^openssl1.1-' 2>/dev/null ; then
    rpm -evh --nodeps openssl1.1-static 2>/dev/null || : 
    rpm -evh --nodeps openssl1.1-devel 2>/dev/null || : 
    rpm -evh --nodeps openssl1.1 2>/dev/null || : 
    rpm -evh --nodeps openssl1.1-libs 2>/dev/null || : 
fi
rm -fr /etc/ld.so.conf.d/openssl-1.1.1.conf
rm -vfr /usr/local/openssl-1.1.1
echo
sleep 1
rpm -ivh openssl1.1-libs-*.rpm
sleep 1
yum -y reinstall openssl1.1-libs-*.rpm
sleep 1
yum -y install openssl1.1-1.1*.rpm openssl1.1-devel-*.rpm
sleep 1
yum -y install openssl1.1-static-*.rpm
sleep 1
cd /tmp
[ -f /usr/local/openssl-1.1.1/bin/openssl ] && rm -vfr /usr/bin/openssl
install -v -c -m 0755 /usr/local/openssl-1.1.1/bin/openssl /usr/bin/
/sbin/ldconfig
echo
rpm -qa | grep -i '^openssl1.1-'
echo
exit

