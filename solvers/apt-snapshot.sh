#!/bin/sh
# Point apt at the Debian or Ubuntu snapshot archive as it was at $1
# (YYYYMMDDTHHMMSSZ), so the package versions a Dockerfile pins stay installable
# after the live mirrors move on, and the unpinned ones resolve the same way.
# A Dockerfile copies this in and runs it before each `apt-get update`, with the
# time that RUN's layer was first built; it may run again to move to another time.
set -eu
when="$1"
. /etc/os-release
case "$ID" in
  debian) pattern='s#https?://(deb|snapshot)\.debian\.org/(archive/)?(debian(-security)?)(/[0-9TZ]+)?#http://snapshot.debian.org/archive/\3/'"$when"'#g' ;;
  ubuntu) pattern='s#https?://((archive|security)\.ubuntu\.com/ubuntu|snapshot\.ubuntu\.com/ubuntu/[0-9TZ]+)/?#http://snapshot.ubuntu.com/ubuntu/'"$when"'/#g' ;;
  *) echo "apt-snapshot: unsupported distribution $ID" >&2; exit 1 ;;
esac
changed=0
for file in /etc/apt/sources.list /etc/apt/sources.list.d/*.list /etc/apt/sources.list.d/*.sources; do
  [ -f "$file" ] || continue
  sed -i -E "$pattern" "$file"
  grep -q "snapshot\.$ID\.\(org\|com\)/.*$when" "$file" && changed=1
done
[ "$changed" = 1 ] || { echo "apt-snapshot: no apt source was redirected" >&2; exit 1; }
# Snapshot Release files keep their original expiry dates.
echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99snapshot
