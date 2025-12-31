#!/bin/sh

. `dirname $0`/../share/eterbuild/functions/common
load_mod strings

check()
{
	[ "$2" != "$3" ] && echo "FATAL with '$1': result '$2' do not match with '$3'" || echo "OK for '$1' with '$2'"
}

# TODO: move to lib
#isnumber()
#{
#	#local num="$(("$*"))"
#	echo "$*" | filter_strip_spaces | grep -q "^[0-9]\+$"
#	#[ "$num" != "0" ]
#}

check_arg()
{
	check "$1 >= $2" "$(version_more_version "$1" "$2" ; echo $?)" "$3"
}

check_arg "c9" "c9f2" 1
check_arg "c9" "c9" 0
check_arg "c9f2" "c9f1" 0
check_arg "c9f1" "c9f2" 1
check_arg "c9f2" "c10" 1
check_arg "c10f1" "c10" 0
check_arg "c9f2" "c9" 0
check_arg "c9f2" "c8" 0
