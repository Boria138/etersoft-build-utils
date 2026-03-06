#!/bin/sh

. `dirname $0`/../share/eterbuild/functions/common
load_mod git

check()
{
	[ "$2" != "$3" ] && echo "FATAL with '$1': result '$2' do not match with '$3'" || echo "OK for '$1' with '$2'"
}

# version_to_tag
check "tilde" "$(version_to_tag "1.0~rc1-alt1")" "1.0.tilde.rc1-alt1"
check "plus" "$(version_to_tag "1.0+dfsg-alt1")" "1.0.plus.dfsg-alt1"
check "both" "$(version_to_tag "1.0~rc1+dfsg-alt1")" "1.0.tilde.rc1.plus.dfsg-alt1"
check "no special" "$(version_to_tag "1.0-alt1")" "1.0-alt1"
check "multiple tilde" "$(version_to_tag "1.0~alpha~1-alt1")" "1.0.tilde.alpha.tilde.1-alt1"

# tag_to_version
check "tilde back" "$(tag_to_version "1.0.tilde.rc1-alt1")" "1.0~rc1-alt1"
check "plus back" "$(tag_to_version "1.0.plus.dfsg-alt1")" "1.0+dfsg-alt1"
check "both back" "$(tag_to_version "1.0.tilde.rc1.plus.dfsg-alt1")" "1.0~rc1+dfsg-alt1"
check "no special back" "$(tag_to_version "1.0-alt1")" "1.0-alt1"

# roundtrip
for ver in "1.0~rc1-alt1" "2.3+dfsg-alt2" "1.0~beta1+repack-alt1" "3.14-alt1" ; do
	check "roundtrip $ver" "$(tag_to_version "$(version_to_tag "$ver")")" "$ver"
done
