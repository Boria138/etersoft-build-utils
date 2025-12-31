# This spec is autoported from ALT Linux Sisyphus to AstraLinux orel automatically by rpmbph script from etersoft-build-utils.
# TODO make deps via links (for i586) - fakelinks?

# Spec for WINE@Etersoft LGPL part
# Copyright (c) 2004-2022 Etersoft llc., Russia, Saint-Petersburg.
#
# The source code can be downloaded from ftp://updates.etersoft.ru/pub/Etersoft/WINE@Etersoft/7.x/sources
# Please submit bugfixes or comments via wine@etersoft.ru

# Build instruction:
# install rpm-build-altlinux-compat for your system
# and run build src.rpm for your system with
#    $ rpmbuild -bb command
# or install etersoft-build-utils and rpm-build-altlinux-compat for your system
# and run
#    $ rpmbb wine-etersoft.spec for build rpm package on ALT
# or $ rpmbph wine-etersoft.spec for other distro (checked only within Korinf build system)
#

%define _unpackaged_files_terminate_build 1
%if %_vendor == "alt"
# hack for lib.req: ERROR: /tmp/.private/lav/wine-etersoft-buildroot/usr/lib64/wine/x86_64-unix/ws2_32.so: library ntdll.so not found
%filter_from_requires /^ntdll.so.*/d
%global __find_debuginfo_files %nil
%endif

%def_without vanilla
%define gecko_version 2.47.2
%define mono_version 7.2.0
%define winetricks_version 20220207

%define basemajor 7.x
%define major 7.6
%define rel %nil
%define stagingrel %nil

# used in wine staging only
%def_with gtk3

# build ping subpackage
%def_with set_cap_net_raw

%if_feature llvm 11.0
# build real PE libraries (.dll, not .dll.so), via clang
%def_with mingw
%else
%def_without mingw
%endif

# https://bugs.etersoft.ru/show_bug.cgi?id=15244
%def_with unwind

# keep debugging symbols in PE files (skip strip)
# TODO: check if we need debug info and pack it separately
%def_with debugpe

# use rpm-macros-features
%if_feature vulkan
%def_with vulkan
%endif

# TODO
# [00:01:19] In file included from dlls/opencl/pe_wrappers.c:22:
# [00:01:19] dlls/opencl/opencl_types.h:3:23: error: expected ';' after top level declarator
# [00:01:19] typedef int32_t cl_int DECLSPEC_ALIGN(4);
%if_with mingw
%def_without opencl
%else
%def_without opencl
%endif

%if_feature pcap 1.2.1
%def_with pcap
%else
%def_without pcap
%def_without set_cap_net_raw
%endif


%ifarch x86_64 aarch64
%def_with build64
%define winearch wine64
%define winepkgname wine-etersoft
%else
%def_without build64
%define winearch wine32
%define winepkgname wine32-etersoft
%endif

Name: wine-etersoft
Version: %major.1
Release: alt3astra
Epoch: 1

Summary: WINE@Etersoft - Environment for running Windows applications (main part)
Summary(ru_RU.UTF-8): WINE@Etersoft — Среда для запуска программ Windows (основная часть)

License: LGPLv2+
Group: Emulators
Url: https://winehq.org.ru/WINE@Etersoft

Packager: Vitaly Lipatov <lav@altlinux.ru>

# TODO: major in gear

# Source-url: https://dl.winehq.org/wine/source/%basemajor/wine-%major%rel.tar.xz
Source: %name-%version.tar
# Source1-url: https://github.com/wine-staging/wine-staging/archive/v%major%stagingrel.tar.gz
Source1: %name-staging-%version.tar

Source3: %name-%version-desktop.tar
Source4: %name-%version-icons.tar
# multilib wrapper scripts
Source6: %name-%version-bin-scripts.tar

# local patches
Source10: %name-patches-%version.tar
# Etersoft dir
Source20: etersoft.tar

AutoReq: yes, noperl, nomingw32



# set compilers
%ifarch aarch64
%def_with clang
# clang-12: error: unsupported argument 'auto' to option 'flto='
%define optflags_lto -flto=thin
%endif

# disable LTO: link error in particular, and unverified in general
#x86_64-alt-linux-gcc -m64 -o loader/wine64-preloader loader/preloader.o loader/preloader_mac.o -static -nostartfiles -nodefaultlibs \
#  -Wl,-Ttext=0x7d400000
#ld: /usr/src/tmp/wine64-preloader.yxZ9KH.ltrans0.ltrans.o: in function `_start':
#<artificial>:(.text+0x12): undefined reference to `thread_data'
#ld: <artificial>:(.text+0x2a): undefined reference to `wld_start'
%define optflags_lto %nil

# TODO: also check build64
# workaround for https://bugzilla.altlinux.org/38130
# notbuild64mingw = without mingw && without build64
%if %{expand:%%{?_without_mingw:1}%%{!?_without_mingw:0}} && %{expand:%%{?_without_build64:1}%%{!?_without_build64:0}}
%define notbuild64mingw 1
%endif

%define libdir %_libdir
%define libwinedir %libdir/wine
%define winebindir %_libexecdir/wine
%if_with build64
%define wineserver wineserver64
%define winepreloader wine64-preloader
%else
%define wineserver wineserver32
%define winepreloader wine-preloader
%endif

# set arch dependent dirs
%ifarch %{ix86}
%define winepedir i386-windows
%define winesodir i386-unix
%endif
%ifarch x86_64
%define winepedir x86_64-windows
%define winesodir x86_64-unix
%endif
%ifarch %{arm}
%define winepedir arm-windows
%define winesodir arm-unix
%endif
%ifarch aarch64
%define winepedir aarch64-windows
%define winesodir aarch64-unix
%endif


%if_without build64
# skip -fPIC checking (-fnoPIC need in new wine to skip DECLSPEC_HOTPATCH)
%add_verify_elf_skiplist %libwinedir/%winesodir/*.so
# -fPIC is totally disabled for i586
%add_verify_elf_skiplist %_bindir/*
%add_verify_elf_skiplist %winebindir/*
%endif


# TODO: remove it for mingw build (when there will no any dll.so files)
%add_verify_elf_skiplist %libwinedir/%winesodir/*.*.so
%add_findreq_skiplist %libwinedir/%winepedir/*

#
# /usr/bin/strip: ./usr/lib64/wine/x86_64-windows/stqrTIUz/stPNVRry/dsound.dll: warning: line number count (0x10000) exceeds section size (0x8)
# /usr/bin/strip: ./usr/lib64/wine/x86_64-windows/stbguFIA: file format not recognized
# see also our strip below
%if_with debugpe
%brp_strip_none %libwinedir/%winepedir/*
%endif

# we don't need provide anything
AutoProv:no

# for wine-staging gitapply.sh script


# used llvm/clang toolchain if needed
%define llvm_version 11
%define llvm_br clang >= %llvm_version llvm >= %llvm_version lld >= %llvm_version

%if_with clang
BuildRequires: %llvm_br
%else
BuildRequires: gcc:any
%endif

%if_with mingw
BuildRequires: %llvm_br
%endif

# General dependencies
BuildRequires: rpm-build-altlinux-compat:any >= 2.1.14
# due _localstatedir
BuildRequires: rpm-build-altlinux-compat:any
BuildRequires: rpm-build-altlinux-compat:any
BuildRequires: util-linux:any flex:any bison:any
BuildRequires: libfontconfig1-dev:i386 libfreetype6-dev:i386

BuildRequires: libgphoto2-dev:i386 libsane-dev:i386 libcups2-dev:i386
BuildRequires: libv4l-dev:i386
BuildRequires: libasound2-dev:i386 libjack-dev:i386 libpulse-dev:i386 libgsm1-dev:i386
BuildRequires: libopenal-dev:i386

BuildRequires: libusb-dev:i386 libieee1284-3-dev:i386
BuildRequires:  libgnutls28-dev:i386 libsasl2-dev:i386 libkrb5-dev:i386 libldap2-dev:i386
BuildRequires: unixodbc-dev:any
%if_with pcap

%endif

%if_with unwind

%endif

#BuildRequires: gstreamer-devel gst-plugins-devel
# TODO: osmesa

%if_with vulkan

%endif

%if_with opencl
BuildRequires: ocl-icd-devel opencl-headers
%endif

# Staging part
%if_with gtk3
# GTK3 theme support: staging only

%endif


# udev needed for udev version detect
BuildRequires: libudev-dev:i386 udev:any libdbus-1-dev:i386

# all Xorg dependencies

BuildRequires: libice-dev:i386 libsm-dev:i386
BuildRequires: libx11-dev:i386 libxau-dev:i386  libxrandr-dev:i386
BuildRequires: libxext-dev:i386 libxfixes-dev:i386   libxi-dev:i386
BuildRequires: libxmu-dev:i386  libxrender-dev:i386
BuildRequires:   libxinerama-dev:i386 libxt-dev:i386
BuildRequires: libxxf86dga-dev:i386  libxcomposite-dev:i386
BuildRequires: libxxf86vm-dev:i386
BuildRequires:  libxcursor-dev:i386

# a long way to get needed perl-XML-LibXML?


BuildRequires: desktop-file-utils:any

#BuildRequires(pre): rpm-macros-wine


%if "%winepkgname" == "wine32-etersoft"
%package -n %winepkgname
Summary: WINE@Etersoft - Environment for running Windows applications (main part)
Summary(ru_RU.UTF-8): WINE@Etersoft — Среда для запуска программ Windows (основная часть)

License: LGPLv2+
Group: Emulators
Url: https://winehq.org.ru/WINE@Etersoft

AutoProv: no
%endif

# Use it instead proprietary MS Core Fonts
# Requires: fonts-ttf-liberation

# Actually for x86_32
Requires: libc6:i386 libc6:i386

Requires: wine-gecko:any = %gecko_version
Conflicts: wine-mono < %mono_version

%if_without libwine
Provides: lib%name = %EVR
Obsoletes: lib%name
%endif

# For menu/MIME subsystem
Requires: desktop-file-utils:any

Requires: %name-common = %EVR

Conflicts: wine-vanilla wine

# FIXME:
# Runtime linked
Requires: libcups2:i386
Requires: libxrender1:i386 libxi6:i386 libxext6:i386 libx11-6:i386 libice6:i386 libxcomposite1:i386 libxcursor1:i386 libxinerama1:i386 libxrandr2:i386
Requires:  libgnutls30:i386

%if_with gtk3

%endif

%if_with vulkan
Requires: libvulkan1:i386
%endif

# Many programs depends on unixODBC
# Requires: libunixODBC2

%if_with set_cap_net_raw

%endif

%if_with pcap
# Recommended
# Requires: libpcap0.8
%endif

Requires: libfontconfig1:i386 libfreetype6:i386

# old gl part
Provides: %winepkgname-gl = %EVR
Obsoletes: %winepkgname-gl < %EVR

Conflicts: libwine-vanilla-gl libwine-gl
Conflicts: wine-vanilla-gl wine-gl
Obsoletes: lib%name-gl

# Runtime linked (via dl_open)


# wine-staging only





# old twain part
Provides: %winepkgname-twain = %EVR
Obsoletes: %winepkgname-twain < %EVR

Conflicts: libwine-vanilla-twain libwine-twain
Conflicts: wine-vanilla-twain wine-twain
Obsoletes: lib%name-twain

# Runtime linked (via dl_open)
Requires: libsane:i386


# Provides/Obsoletes Fedora packages
%define common_provobs wine-filesystem wine-desktop wine-systemd wine-sysvinit
%define base_provobs wine-alsa wine-capi wine-cms wine-ldap wine-openal wine-pulseaudio wine-wow wine-alsa wine-capi wine-cms wine-ldap wine-openal wine-opencl wine-pulseaudio
%define fonts_provobs wine-fonts wine-arial-fonts wine-courier-fonts wine-fixedsys-fonts wine-marlett-fonts wine-ms-sans-serif-fonts wine-small-fonts wine-symbol-fonts wine-system-fonts wine-tahoma-fonts wine-times-new-roman-fonts wine-wingdings-fonts
#Provides: %common_provobs %base_provobs %fonts_provobs
Obsoletes: %common_provobs %base_provobs %fonts_provobs


%if "%winepkgname" == "wine32-etersoft"
BuildRequires: rpm-build-altlinux-compat >= 0.95 ia32-libs-dev gcc-multilib make gcc
%define _default_patch_fuzz 3

%description -n %winepkgname
This build is a LGPL-part of WINE@Etersoft product prepared for
using commercial programs
Wine is a program which allows running Windows programs
on Unix. It consists of a program loader which loads and executes a
Windows binary, and a library (called Winelib) that implements Windows
API calls using their Unix or X11 equivalents.  The library may also
be used for porting Win32 code into native Unix executables.

This build based on wine source with wine-staging project patches.
Don't expect everything to work.
Check http://winehq.org.ru or http://winehq.org if you experience some problems.

You can obtain commercial support of the product from Etersoft company:
wine@etersoft.ru

%description -n %winepkgname -l ru_RU.UTF-8
Данная сборка является LGPL-частью продукта WINE@Etersoft,
предназначенного для исполнения коммерческих Windows-программ.
WINE Не Является Эмулятором. Это альтернативная реализация API Windows.
Wine предоставляет как инструментарий разработки (Winelib)
для переноса унаследованных исходных кодов из среды Windows в среду
Unix, так и программный загрузчик, позволяющий исполнять двоичный код, разработанный
для Windows, в среде разных вариантов.
Wine не требует наличия Microsoft Windows,
поскольку это полностью альтернативная реализация, состоящая из полностью
свободного кода.

Не ожидайте, что всё будет работать.

Обращайтесь за дополнительной информацией на сайт https://winehq.org.ru

Вы можете получить коммерческую поддержку данного продукта от компании Этерсофт:
wine@etersoft.ru

%endif

#=========================================================================

%description
This build is a LGPL-part of WINE@Etersoft product prepared for
using commercial programs
Wine is a program which allows running Windows programs
on Unix. It consists of a program loader which loads and executes a
Windows binary, and a library (called Winelib) that implements Windows
API calls using their Unix or X11 equivalents.  The library may also
be used for porting Win32 code into native Unix executables.

This build based on wine source with wine-staging project patches.
Don't expect everything to work.
Check http://winehq.org.ru or http://winehq.org if you experience some problems.

You can obtain commercial support of the product from Etersoft company:
wine@etersoft.ru

%description -l ru_RU.UTF-8
Данная сборка является LGPL-частью продукта WINE@Etersoft,
предназначенного для исполнения коммерческих Windows-программ.
WINE Не Является Эмулятором. Это альтернативная реализация API Windows.
Wine предоставляет как инструментарий разработки (Winelib)
для переноса унаследованных исходных кодов из среды Windows в среду
Unix, так и программный загрузчик, позволяющий исполнять двоичный код, разработанный
для Windows, в среде разных вариантов.
Wine не требует наличия Microsoft Windows,
поскольку это полностью альтернативная реализация, состоящая из полностью
свободного кода.

Не ожидайте, что всё будет работать.

Обращайтесь за дополнительной информацией на сайт https://winehq.org.ru

Вы можете получить коммерческую поддержку данного продукта от компании Этерсофт:
wine@etersoft.ru



%package -n %winepkgname-test
Summary: WinAPI test for Wine
Summary(ru_RU.UTF-8): Тест WinAPI для Wine
Group: Emulators
Requires: %winepkgname = %EVR
Conflicts: wine-vanilla-test wine-test

%description -n %winepkgname-test
WinAPI test for Wine (unneeded for usual work).
Warning: it may kill your X server suddenly.


%package  -n %winepkgname-full
Summary: Wine meta package
Summary(ru_RU.UTF-8): Мета пакет Wine
Group: Emulators
# due ExclusiveArch
#BuildArch: noarch
Requires: %winepkgname = %EVR
Requires: %winepkgname-programs = %EVR

Requires: wine-mono:any = %mono_version
Requires: wine-gecko:any = %gecko_version
Requires: winetricks:any >= %winetricks_version

Conflicts: wine-vanilla-full wine-full

%description -n %winepkgname-full
Wine meta package. Use it for install all wine subpackages.


%package common
Summary: Common wine files and scripts
Summary(ru_RU.UTF-8): Общие файлы и скрипты Wine
Group: Emulators
BuildArch: noarch
Conflicts: wine-vanilla-common wine-common
Conflicts: libwine libwine-vanilla
# we don't need provide anything
AutoProv:no

%description common
Common arch independent wine files and scripts.

%description common -l ru_RU.UTF-8
Общие архитектурно-независимые файлы Wine.


%package programs
Summary: Wine programs
Group: Emulators
Requires: %winepkgname = %EVR
# due ExclusiveArch
#BuildArch: noarch

Conflicts: wine-vanilla-programs wine-programs

%description programs
Wine GUI programs:
* winefile
* notepad
* winemine


%package ping
Summary: Set capability for Wine ping
Group: Emulators
Requires: %winepkgname = %EVR
# due ExclusiveArch
#BuildArch: noarch
Conflicts: wine-vanilla-ping wine-ping

%description ping
Set capability for Wine ping in post install script.

Also you can control in manually:

$ wine-cap_net_raw [on|off]



%package -n %winepkgname-devel-tools
Summary: Development tools for %name-devel
Group: Development/C
Requires: %winepkgname-devel = %EVR
Conflicts: wine-vanilla-devel-tools wine-devel-tools
Conflicts: libwine-vanilla-devel libwine-devel
Conflicts: lib%name-devel < %version
%if_without vanilla
Provides: libwine-devel = %EVR
%endif
# we don't need provide anything
AutoProv:no

# due winegcc requires
Requires: gcc:any g++:any gcc-multilib:any ia32-libs-dev:any libstdc++-devel


%description -n %winepkgname-devel-tools
%name-devel-tools contains tools needed to
develop programs using %name.

%description -n %winepkgname-devel-tools -l ru_RU.UTF-8
%name-devel содержит файлы для разработки программ,
использующих Wine: заголовочные файлы и утилиты,
предназначенные для компилирования программ с %name.


%package -n %winepkgname-devel
Summary: Headers for %name-devel
Group: Development/C
Requires: %winepkgname = %EVR
Obsoletes: lib%name-devel < %version
#Provides: lib%name-devel = %EVR
Conflicts: libwine-vanilla-devel
# libwine-devel is a sacral name
# we don't need provide anything
AutoProv:no


%description -n %winepkgname-devel
%name-devel contains the header files and some utilities needed to
develop programs using %name.

%description -n %winepkgname-devel -l ru_RU.UTF-8
%name-devel содержит файлы для разработки программ, использующих Wine:
заголовочные файлы и утилиты, предназначенные
для компилирования программ с %name.


%prep
%setup -q -a 1 -a 10 -a 20
# Apply wine-staging patches
%name-staging/patches/patchinstall.sh DESTDIR=$(pwd) --all --backend=patch

# disable rpath using for executable
#__subst "s|^\(LDRPATH_INSTALL =\).*|\1|" Makefile.in

# Apply local patches
%name-patches/patchapply.sh

# TODO: make it in a patch? (eterbug #14110)
echo "WINE@Etersoft version %version-%release" >VERSION
%__subst "s|Staging|WINE@Etersoft|" libs/wine/Makefile.in
autoreconf -f

%__subst 's|$(sysconfdir)/udev/rules.d|%_udevrulesdir|g' tools/Makefile.in

%build
%if_with clang
%remove_optflags -frecord-gcc-switches
export CC=clang
%endif
%if_with mingw
export CROSSCC=clang
%endif


%configure --with-x \
%if_with build64
--enable-win64 \
%endif
--disable-tests \
--without-gstreamer \
--without-oss \
--without-capi \
%{subst_with pcap} \
%{subst_with unwind} \
%{subst_with mingw} \
--with-xattr \
%{subst_with vulkan} \
--bindir=%winebindir \
%nil

%__make depend
%make_build

cd etersoft
%configure
%make_build

%install
%makeinstall_std
%makeinstall_std -C etersoft

# clean permissions (via find to hide file list)
find %buildroot%libwinedir/%winesodir -type f | xargs chmod 0644
find %buildroot%libwinedir/%winepedir -type f | xargs chmod 0644

%if_with libwine
# keep in libdir for compatibility
mv -v %buildroot%libwinedir/%winesodir/libwine.so.1* %buildroot%libdir
%else
rm -v %buildroot%libwinedir/%winesodir/libwine.so.1*
%endif

# hack for lib.req: ERROR: /tmp/.private/lav/wine-etersoft-buildroot/usr/lib64/wine/x86_64-unix/ws2_32.so: library ntdll.so not found
%if %_vendor == "alt"
cp -v %buildroot%libwinedir/%winesodir/ntdll.so %buildroot%libdir
%endif

mkdir -p %buildroot%_bindir/

# hack: move all programs back to _bindir
find %buildroot%winebindir -mindepth 0 -maxdepth 1 -not -type d | \
egrep -v '/wine$|/wine-preloader$|/wineserver$|/wine64$|/wine64-preloader$|/wineserver64|/winegcc|/wineg++|/winecpp|/winebuild$' | \
xargs mv -v -t %buildroot%_bindir/
[ -s %buildroot%_bindir/wineg++ ] || ln -sv --relative %buildroot%winebindir/wineg++ %buildroot%_bindir/
[ -s %buildroot%_bindir/winecpp ] || ln -sv --relative %buildroot%winebindir/winecpp %buildroot%_bindir/

# wine64 and wine64-preloader are already built as wine64*
mv -v %buildroot%winebindir/wineserver %buildroot%winebindir/%wineserver
%if_with build64
[ -s %buildroot%_bindir/wine64 ] || ln -sv --relative %buildroot%winebindir/wine64 %buildroot%_bindir/
%endif


# FIXME: it is missed on 64 bit (it is supposed to be installed with wine 32)
%if_with build64
install -p -m 0644 loader/wine.man %buildroot%_man1dir/wine.1
%endif

# unpack desktop files
cd %buildroot%_desktopdir/
tar xvf %SOURCE3
mkdir -p %buildroot%_datadir/desktop-directories/
mv *.directory %buildroot%_datadir/desktop-directories/
cd - >/dev/null

# unpack icons files
mkdir -p %buildroot%_iconsdir/
cd %buildroot%_iconsdir/
tar xvf %SOURCE4
cd - >/dev/null

# unpack bin scripts files
mkdir -p %buildroot%_bindir/
tar xvf %SOURCE6
for i in bin-scripts/*.in ; do
tbin=%buildroot%_bindir/$(basename $i .in)
sed -e "s:@BINDIR@:%winebindir:g" $i > $tbin
chmod +x $tbin
done

%if_with set_cap_net_raw
# script for %name-ping
mkdir -p %buildroot%_sbindir/
mv %buildroot%_bindir/wine-cap_net_raw %buildroot%_sbindir/
%endif

# Do not pack non english man pages yet
rm -rv %buildroot%_mandir/*.UTF-8

# Do not pack dangerous association to run windows executables
rm -v %buildroot%_desktopdir/wine.desktop

%if_without debugpe
# [aarch64] /usr/bin/strip: /usr/src/tmp/wine-staging-buildroot/usr/lib64/wine/aarch64-windows/xinput1_1.dll: file format not recognized
%ifarch aarch64
# /usr/src/tmp/wine-staging-buildroot/usr/lib64/wine/aarch64-windows/xpssvcs.dll
# [aarch64] llvm-strip: error: unsupported object file format
llvm-strip %buildroot%libwinedir/%winepedir/* || :
%else
strip %buildroot%libwinedir/%winepedir/*
%endif
# fix against old broken strip: restore builtin mark
tools/winebuild/winebuild --builtin %buildroot%libwinedir/%winepedir/*
%endif


%if_with set_cap_net_raw
%files ping
%defattr(-, root, root)
%_sbindir/wine-cap_net_raw

%post ping
%_sbindir/wine-cap_net_raw on || :

%preun ping
if [ $1 = 0 ]; then
%_sbindir/wine-cap_net_raw off || :
fi
%endif

%pre
%groupadd wine || :
%groupadd wineadmin || :


%files -n %winepkgname
%defattr(-, root, root)
%if "%winebindir" != "%libwinedir"
%dir %winebindir/
%endif
%if_with build64
%winebindir/wine64
%_bindir/wine64
%else
%winebindir/wine
%endif
%winebindir/%wineserver
%winebindir/%winepreloader

# Etersoft part
%if_with build64
%exclude %_bindir/winesplash
%else
%_bindir/winesplash
%endif

%dir %libwinedir/
%dir %libwinedir/%winesodir/
%dir %libwinedir/%winepedir/

%if %_vendor == "alt"
%exclude %libdir/ntdll.so
%endif

%libwinedir/%winesodir/avicap32.so
%libwinedir/%winesodir/ntdll.so
%libwinedir/%winesodir/ctapi32.so
%libwinedir/%winesodir/dnsapi.so
%libwinedir/%winesodir/dwrite.so
%libwinedir/%winesodir/bcrypt.so
%libwinedir/%winesodir/qcap.so
%libwinedir/%winesodir/odbc32.so
%libwinedir/%winesodir/crypt32.so
%libwinedir/%winesodir/kerberos.so
%libwinedir/%winesodir/mountmgr.so
%libwinedir/%winesodir/netapi32.so
%libwinedir/%winesodir/nsiproxy.so
%libwinedir/%winesodir/wldap32.so
%libwinedir/%winesodir/winspool.so
%libwinedir/%winesodir/msv1_0.so
%libwinedir/%winesodir/win32u.so
%libwinedir/%winesodir/ws2_32.so
%if_with opencl
%libwinedir/%winesodir/opencl.so
%endif
%libwinedir/%winesodir/secur32.so
%libwinedir/%winesodir/winepulse.so
%libwinedir/%winesodir/winealsa.so
%if_with pcap
%libwinedir/%winesodir/wpcap.so
%endif
%libwinedir/%winesodir/winebus.so

%if_without mingw
#if_without vanilla
%libwinedir/%winesodir/windows.networking.connectivity.so
#endif
%libwinedir/%winesodir/*.com.so
%libwinedir/%winesodir/*.cpl.so
%libwinedir/%winesodir/*.ocx.so
%libwinedir/%winesodir/*.ax.so
%libwinedir/%winesodir/*.exe.so
%libwinedir/%winesodir/*.acm.so
%endif

%ifdef notbuild64mingw
%libwinedir/%winesodir/*.dll16.so
%libwinedir/%winesodir/*.drv16.so
%libwinedir/%winesodir/*.exe16.so
%libwinedir/%winesodir/winoldap.mod16.so
%libwinedir/%winesodir/*.vxd.so
%endif

# some dll still compiled not as PE in any way
%libwinedir/%winesodir/*.drv.so
%libwinedir/%winesodir/*.dll.so
%libwinedir/%winesodir/*.sys.so

%libwinedir/%winepedir/*.com
%libwinedir/%winepedir/*.cpl
%libwinedir/%winepedir/*.drv
%libwinedir/%winepedir/*.dll
%libwinedir/%winepedir/*.acm
%libwinedir/%winepedir/*.ocx
%libwinedir/%winepedir/*.tlb
%libwinedir/%winepedir/*.sys
%libwinedir/%winepedir/*.exe
%libwinedir/%winepedir/*.ax
%libwinedir/%winepedir/*.ds
%if_without vanilla
%libwinedir/%winepedir/windows.networking.connectivity
%endif
%libwinedir/%winepedir/light.msstyles
%if_without build64
%libwinedir/%winepedir/*.dll16
%libwinedir/%winepedir/*.drv16
%libwinedir/%winepedir/*.exe16
%libwinedir/%winepedir/winoldap.mod16
%libwinedir/%winepedir/*.vxd
%endif

# twain
%libwinedir/%winepedir/twain_32.dll
%libwinedir/%winepedir/gphoto2.ds
%libwinedir/%winesodir/gphoto2.so
%libwinedir/%winesodir/sane.so
%if_without mingw
%libwinedir/%winesodir/twain_32.dll.so
%libwinedir/%winesodir/gphoto2.ds.so
%libwinedir/%winesodir/sane.ds.so
%endif
%ifdef notbuild64mingw
%libwinedir/%winesodir/twain.dll16.so
%endif

%ifdef notbuild64mingw
%exclude %libwinedir/%winesodir/twain.dll16.so
%endif

# gl
%libwinedir/%winesodir/winevulkan.so
%if_without mingw
%libwinedir/%winesodir/winevulkan.dll.so
%libwinedir/%winesodir/d3d10.dll.so
%libwinedir/%winesodir/d3d8.dll.so
%libwinedir/%winesodir/d3d9.dll.so
%libwinedir/%winesodir/d3dxof.dll.so
%libwinedir/%winesodir/opengl32.dll.so
%libwinedir/%winesodir/glu32.dll.so
%libwinedir/%winesodir/wined3d.dll.so
%endif


%files common
%defattr(-, root, root)
%doc ANNOUNCE AUTHORS LICENSE README
%lang(de) %doc documentation/README.de
%lang(es) %doc documentation/README.es
%lang(fr) %doc documentation/README.fr
%lang(hu) %doc documentation/README.hu
%lang(it) %doc documentation/README.it
%lang(ko) %doc documentation/README.ko
%lang(nb) %doc documentation/README.no
%lang(pt) %doc documentation/README.pt
%lang(pt_BR) %doc documentation/README.pt_br
%lang(tr) %doc documentation/README.tr

%_bindir/wine
%_bindir/wineserver
%_bindir/wine-preloader

%_bindir/wineapploader

%_bindir/regsvr32
%_bindir/winecfg
%_bindir/regedit
%_bindir/msiexec

%_bindir/wineconsole

%_bindir/winedbg
%_bindir/wineboot
%_bindir/winepath

%_iconsdir/*

%_desktopdir/wine-mime-msi.desktop
%_desktopdir/wine-regedit.desktop
#_desktopdir/wine-serverkill.desktop
%_desktopdir/wine-uninstaller.desktop
%_desktopdir/wine-winecfg.desktop
%_desktopdir/wine-wineconsole.desktop
#_desktopdir/wine-winehelp.desktop

# danger
#_desktopdir/wine.desktop

%_datadir/desktop-directories/*.directory

%_man1dir/wine.*
%_man1dir/msiexec.*
%_man1dir/regedit.*
%_man1dir/regsvr32.*
%_man1dir/wineboot.*
%_man1dir/winecfg.*
%_man1dir/wineconsole.*
%_man1dir/winepath.*
%_man1dir/wineserver.*
%_man1dir/winedbg.*


%dir %_datadir/wine/
%_datadir/wine/wine.inf
%_datadir/wine/nls/
%_datadir/wine/fonts/

# Etersoft part
%_bindir/setnethasp
%_bindir/wineregdiff
%_bindir/winelog
%_bindir/winefar
%_bindir/wine_install_*

%_datadir/wine/splash/
%_datadir/wine/skel/

%attr(0775 root wineadmin) %dir %_localstatedir/lib/wine/
# rules for fix permissions on protection keys
#_udevrulesdir/99-winekeys.rules
#%_sysconfdir/sysctl.d/wine.conf
%dir %_sysconfdir/wine/
%dir %_sysconfdir/wine/reg.d/
%dir %_sysconfdir/wine/script.d/
%_sysconfdir/wine/reg.d/*.reg*
%_sysconfdir/wine/script.d/*.sh*


%files -n %winepkgname-full
%defattr(-, root, root)

%files programs
%defattr(-, root, root)
%_bindir/notepad
%_bindir/winefile
%_bindir/winemine
%_man1dir/notepad.*
%_man1dir/winefile.*
%_man1dir/winemine.*
%_desktopdir/wine-notepad.desktop
%_desktopdir/wine-winefile.desktop
%_desktopdir/wine-winemine.desktop

%files -n %winepkgname-devel-tools
%defattr(-, root, root)
%doc LICENSE
%_bindir/function_grep.pl
%_bindir/winebuild
%winebindir/winebuild
%_bindir/wmc
%_bindir/wrc
%_bindir/widl
%_bindir/wineg++
%winebindir/wineg++
%_bindir/winegcc
%winebindir/winegcc
%_bindir/winecpp
%winebindir/winecpp
%_bindir/winedump
%_bindir/winemaker
%_bindir/msidb

%_includedir/wine/
#%_aclocaldir/wine.m4

%_man1dir/wmc.*
%_man1dir/wrc.*
%_man1dir/widl.*
%_man1dir/winebuild.*
%_man1dir/winedump.*
%_man1dir/wineg++.*
%_man1dir/winegcc.*
%_man1dir/winecpp.*
%_man1dir/winemaker.*


%files -n %winepkgname-devel
%defattr(-, root, root)
%if_with mingw
%libwinedir/%winepedir/lib*.a
%endif
%libwinedir/%winesodir/lib*.a

%changelog
* Mon Apr 18 2022 Etersoft Builder <builder@etersoft.ru> 1:7.6.1-alt3astra
- autoport to AstraLinux orel (by rpmbph script)

* Fri Apr 15 2022 Vitaly Lipatov <lav@altlinux.ru> 1:7.6.1-alt3
- abolish twain and gl subpackages

* Fri Apr 15 2022 Vitaly Lipatov <lav@altlinux.ru> 1:7.6.1-alt2
- drop webclient require
- drop libwine subpackage build support
- produce wine32-etersoft for 32 bit

* Mon Apr 11 2022 Vitaly Lipatov <lav@altlinux.ru> 1:7.6.1-alt1
- new version 7.6.1 (with rpmrb script)
- set strict require wine-mono 7.2.0

* Sat Apr 02 2022 Vitaly Lipatov <lav@altlinux.ru> 1:7.5.1-alt4
- new version (7.5.1) with rpmgs script
- drop out unneeded build requires (many libs is embedded now)
- drop out unneeded requires
- set strict require wine-mono 7.1.1

* Fri Mar 25 2022 Vitaly Lipatov <lav@altlinux.ru> 1:6.23.1-alt4
- set version for provided libwine-devel
- skip linking wine64 to bindir if it is already exists
- don't pack libwinecrt0.a twice
- fix checking for build64mingw, fix build

* Mon Mar 21 2022 Vitaly Lipatov <lav@altlinux.ru> 1:6.23.1-alt3
- fix build without PE
- pack lib*.a needed for build with wine

* Tue Feb 22 2022 Vitaly Lipatov <lav@altlinux.ru> 1:6.23.1-alt2
- etersoft/winesplash: update default splash
- fix wpcap packing
- fix build with new lib.req on ALT
- spec: make links in usr/bin only if missed

* Tue Feb 08 2022 Vitaly Lipatov <lav@altlinux.ru> 1:6.23.1-alt1
- new version (6.23.1) with rpmgs script

* Tue Feb 08 2022 Vitaly Lipatov <lav@altlinux.ru> 1:6.22.1-alt1
- step to build wine biarch (sync with public wine builds)

* Wed Jan 19 2022 Vitaly Lipatov <lav@altlinux.ru> 1:6.21.3-alt1
- update patches to staging wine-6.23

* Tue Dec 28 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.21.2-alt1
- add wine_install_kompas

* Thu Dec 16 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.21.1-alt2
- add hacks

* Sun Nov 14 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.21.1-alt1
- new version 6.21.1 (with rpmrb script)

* Sat Aug 14 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.15.1-alt1
- new version 6.15.1 (with rpmrb script)

* Sat Jul 31 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.14.1-alt1
- new version 6.14.1 (with rpmrb script)
- set strict require wine-mono 6.3.0

* Fri Jul 23 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.13.1-alt1
- new version 6.13.1 (with rpmrb script)

* Fri Jun 25 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.11.1-alt1
- new version 6.11 (with rpmrb script)
- set strict require wine-mono 6.2.0

* Wed Mar 31 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.5.0-alt1
- new version 6.5.0 (with rpmrb script)

* Wed Mar 17 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.4.0-alt1
- new version 6.4.0 (with rpmrb script)

* Fri Feb 19 2021 Vitaly Lipatov <lav@altlinux.ru> 1:6.2.0-alt1
- WINE@Etersoft 6
- set strict require wine-mono 6.0.0
- set strict require wine-gecko 2.47.2

* Thu Dec 24 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.22.0-alt2
- build without gcrypt, fix loop initializing (eterbug #14846)

* Sat Nov 21 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.22.0-alt1
- new version 5.22.0 (with rpmrb script)

* Mon Nov 16 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.21.0-alt1
- new version 5.21.0 (with rpmrb script)

* Sun Oct 25 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.20.0-alt1
- new version 5.20.0 (with rpmrb script)

* Sat Oct 10 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.19.1-alt1
- new version 5.19.1 (with rpmrb script)

* Mon Sep 28 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.18.1-alt1
- new version 5.18.1 (with rpmrb script)
- console no longer requires the curses library
- prepared for vulkan build
- disable static subpackage

* Sun Aug 30 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.16.1-alt1
- new version 5.16.1 (with rpmrb script)

* Sat Aug 01 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.12.1-alt1
- new version 5.12.1 (with rpmrb script)
- set strict require wine-mono 5.1.0

* Tue May 12 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.8.1-alt1
- new version 5.8.1 (with rpmrb script)
- update wine-mono require to 5.0.0

* Fri Mar 06 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.3.1-alt1
- new version 5.3.1 (with rpmrb script)

* Fri Mar 06 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.2.1-alt2
- use libdir and libwinedir in depends to build arch
- spec: update dependencies

* Wed Feb 19 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.2.1-alt1
- new version 5.2.1 (with rpmrb script)
- based on wine 5.2 release

* Wed Jan 22 2020 Vitaly Lipatov <lav@altlinux.ru> 1:5.0.1-alt1
- new version 5.0.1 (with rpmrb script)
- based on wine 5.0 release

* Sun Nov 17 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.19.2-alt1
- add WINE@Etersoft specific patch
- update patches to staging wine-4.19

* Tue Nov 05 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.19.1-alt1
- new version (4.19.1) with rpmgs script

* Sat Sep 28 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.17.1-alt1
- new version 4.17 (with rpmrb script)
- update wine-mono require to 4.9.3

* Mon Sep 16 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.16.1-alt1
- new version (4.16.1) with rpmgs script
- wine/debug.h: Make wine_dbgstr_wn use UTF-8 for output (eterbug #14134)
- reapply ntoskrnl.exe: Ignore CProCtrl initialization failure (eterbug #13466)

* Thu Aug 29 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.14.1-alt2
- disable checking libs in libdir via strings (eterbug #12915)

* Wed Aug 21 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.14.1-alt1
- new version 4.14.1 (with rpmrb script)

* Tue Aug 13 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.13.1-alt1
- new version 4.13.1 (with rpmrb script)

* Sun Jul 07 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.12.1.1-alt1
- new version (4.12.1.1) with rpmgs script
- fix 64 bit build

* Sun Jul 07 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.12.1-alt1
- new version 4.12.1 (with rpmrb script)
- enable ExclusiveArch for x86 and aarch64
- remove BR: prelink

* Sat Jun 22 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.11.1-alt1
- new version 4.11.1 (with rpmrb script)
- strict require wine-mono 4.9.0

* Tue Jun 11 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.10.1-alt1
- new version 4.10.1 (with rpmrb script)

* Wed May 29 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.9.1-alt1
- new version 4.9.1 (with rpmrb script)
- strict require wine-mono 4.8.3

* Wed May 22 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.8.1-alt1
- new version 4.8.1 (with rpmrb script)

* Wed Apr 24 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.6.1-alt1
- new version (4.6.1) with rpmgs script

* Fri Apr 19 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.3.2-alt1
- get project name from VERSION file, replace contacts
- fix segfault when run wine in a directory with nonlatin letters in their name (ALT bug 36268)
- add patch: disable file open association by default (eterbug #11069)

* Tue Mar 05 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.3.1-alt1
- new version 4.3.1 (with rpmrb script)

* Fri Jan 25 2019 Vitaly Lipatov <lav@altlinux.ru> 1:4.0-alt1
- new version 4.0 (with rpmrb script)

* Mon Nov 12 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.19.1-alt1
- new version (3.19.1) with rpmgs script

* Sat Oct 13 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.17.1-alt1
- new version 3.17.1 (with rpmrb script)
- use external winetricks

* Wed Aug 15 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.13.3-alt1
- ntdll: Don't allow blocking on a critical section during (eterbug #12662)

* Tue Jul 31 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.13.2-alt1
- add patch kernel32: Set environment variable PUBLIC on the process (eterbug #13054)

* Sat Jul 21 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.13.1-alt1
- new version 3.13.1 (with rpmrb script)

* Fri Jul 13 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.12.1-alt1
- new version 3.12.1 (with rpmrb script)

* Fri Jun 29 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.11.1-alt1
- new version (3.11.1) with rpmgs script
- drop -fno-omit-frame-pointer

* Wed Jun 13 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.10.1-alt1
- new version 3.10.1 (with rpmrb script)
- use clang on aarch64

* Tue May 29 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.9.1-alt1
- new version 3.9.1 (with rpmrb script)

* Fri May 18 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.8.1-alt1
- new version 3.8.1 (with rpmrb script)

* Sat May 12 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.7.1-alt1
- new version 3.7.1 (with rpmrb script)

* Wed Apr 25 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.6.1-alt1
- new version 3.6.1 (with rpmrb script)
- fix missed wined3d-csmt.dll (ALT bug 34777)

* Sat Mar 31 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.5.0-alt1
- new version 3.5.0 (with rpmrb script)

* Thu Mar 22 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.4.1-alt1
- new version 3.4.1 (with rpmrb script)

* Mon Mar 05 2018 Vitaly Lipatov <lav@altlinux.ru> 1:3.3.1-alt1
- new version (3.3)
- build with winehq 3.3 incorporated Kerberos related code only

* Tue Jan 16 2018 Vitaly Lipatov <lav@altlinux.ru> 1:2.21.3-alt1
- update winetricks up to 20171222
- wine.inf: Add the Kerberos SSP/AP registration

* Thu Jan 11 2018 Vitaly Lipatov <lav@altlinux.ru> 1:2.21.1-alt2
- add the font replacement for Microsoft Sans Serif as Tahoma
- update and rewrite Kerberos related patches

* Thu Nov 30 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.21.1-alt1
- update winetricks up to 20171018-next
- remove obsoleted patches
- use separated patch list and apply script
- add local_build.sh script

* Fri Nov 24 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.21.0-alt1
- new version (2.21) with rpmgs script
- update Kerberos patches against wine staging 2.21

* Wed Nov 08 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.20.2-alt1
- add server APC patches (eterbug #12054, redmine #356)

* Mon Nov 06 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.20.1-alt1
- new version (2.20.1) with rpmgs script
- update Kerberos patches against wine staging 2.20

* Wed Oct 11 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.18.0-alt1
- new version (2.18.0) with rpmgs script
- update Kerberos patches (eterbug #11982)

* Fri Sep 29 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.17.1-alt1
- add Kerberos SSPI (via GSSIAPI support)

* Fri Sep 29 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.17.0-alt1
- new version (2.17.0) with rpmgs script

* Mon Sep 11 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.16.0-alt1
- new version (2.16.0) with rpmgs script
- update winetricks up to 20170823-next
- add dotnet47 support in winetricks

* Sun Aug 27 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.15.0-alt1
- new version (2.15.0) with rpmgs script

* Tue Aug 08 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.14.0-alt1
- new version (2.14.0) with rpmgs script
- enable font smoothing by default
- add libpng16, libjpeg requires

* Sun Jul 30 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.13.0-alt1
- new version (2.13.0) with rpmgs script
- add fix debug output patches

* Wed Jul 12 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.12.0-alt1
- new version 2.12.0 (with rpmrb script)

* Thu Jun 29 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.11.0-alt1
- new version (2.11.0) with rpmgs script

* Thu Jun 15 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.10.1-alt1
- new version (2.10.1) with rpmgs script
- replace RegQueryValueEx HKEY_PERFORMANCE hack with wine-staging one

* Tue May 30 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.9.1-alt1
- new version (2.9.1) with rpmgs script

* Fri May 26 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.8.1-alt1
- new version 2.8.1 (with rpmrb script)
- update winetricks to 20170517-next

* Fri May 05 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.7.1-alt1
- new version (2.7.1) with rpmgs script

* Sun Apr 09 2017 Vitaly Lipatov <lav@altlinux.ru> 1:2.4.1-alt2
- set Epoche:1 for compatibility
- fix build requires
- add if_enabled static
- add Obsoletes for Fedora packages, fix conflicts with wine-vanilla

* Sat Apr 08 2017 Vitaly Lipatov <lav@altlinux.ru> 2.4.1-alt1
- patches moving:
 + enable linking with freetype and fontconfig
 + add PERF_DATA_BLOCK struct definition
 + add fast hack for RegQueryValueEx-HKEY_PERFORMANCE_DATA_BLOCK
 + make OleLoadPicture load DIBs using WIC decoder

* Sat Apr 08 2017 Vitaly Lipatov <lav@altlinux.ru> 2.4.0-alt1
- initial build wine-staging for ALT Sisyphus
