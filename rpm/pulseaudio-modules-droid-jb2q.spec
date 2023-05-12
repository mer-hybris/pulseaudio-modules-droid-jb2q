%define pulseversion %{expand:%(rpm -q --qf '[%%{version}]' pulseaudio)}
%define pulsemajorminor %{expand:%(echo '%{pulseversion}' | cut -d+ -f1)}
%define moduleversion %{pulsemajorminor}.%{expand:%(echo '%{version}' | cut -d. -f3)}

Name:       pulseaudio-modules-droid-jb2q

Summary:    PulseAudio Droid HAL modules
Version:    %{pulsemajorminor}.102
Release:    1
License:    LGPLv2+
URL:        https://github.com/mer-hybris/pulseaudio-modules-droid-jb2q
Source0:    %{name}-%{version}.tar.bz2
Requires:   pulseaudio >= %{pulseversion}
Requires:   %{name}-common = %{version}-%{release}
Requires:   pulseaudio-module-keepalive >= 1.0.0
BuildRequires:  libtool-ltdl-devel
BuildRequires:  meson
BuildRequires:  pkgconfig(pulsecore) >= %{pulsemajorminor}
BuildRequires:  pkgconfig(android-headers)
BuildRequires:  pkgconfig(libhardware)
BuildRequires:  pkgconfig(expat)
Provides:   pulseaudio-modules-droid = %{version}
Obsoletes:  pulseaudio-modules-droid <= 14.2.95

%description
PulseAudio Droid HAL modules, supports Android versions from 4 to 10.

%package common
Summary:    Common libs for the PulseAudio droid modules
Requires:   pulseaudio >= %{pulseversion}
Provides:   pulseaudio-modules-droid-common = %{version}
Obsoletes:  pulseaudio-modules-droid-common <= 14.2.95

%description common
This contains common libs for the PulseAudio droid modules.

%package devel
Summary:    Development files for PulseAudio droid modules
Requires:   %{name}-common = %{version}-%{release}
Requires:   pulseaudio >= %{pulseversion}
Provides:   pulseaudio-modules-droid-devel = %{version}
Obsoletes:  pulseaudio-modules-droid-devel <= 14.2.95

%description devel
This contains development files for PulseAudio droid modules.

%prep
%autosetup -n %{name}-%{version}

%build
echo "%{moduleversion}" > .tarball-version
# Obtain the DEVICE from the same source as used in /etc/os-release
if [ -e "%{_includedir}/droid-devel/hw-release.vars" ]; then
. %{_includedir}/droid-devel/hw-release.vars
else
. %{_libdir}/droid-devel/hw-release.vars
fi
%meson -Ddroid-device=$MER_HA_DEVICE
%meson_build

%install
%meson_install

%files
%defattr(-,root,root,-)
%{_libdir}/pulse-%{pulsemajorminor}/modules/libdroid-sink.so
%{_libdir}/pulse-%{pulsemajorminor}/modules/libdroid-source.so
%{_libdir}/pulse-%{pulsemajorminor}/modules/module-droid-sink.so
%{_libdir}/pulse-%{pulsemajorminor}/modules/module-droid-source.so
%{_libdir}/pulse-%{pulsemajorminor}/modules/module-droid-card.so
%license COPYING

%files common
%defattr(-,root,root,-)
%{_libdir}/pulse-%{pulsemajorminor}/modules/libdroid-util.so

%files devel
%defattr(-,root,root,-)
%dir %{_prefix}/include/pulsecore/modules/droid
%{_prefix}/include/pulsecore/modules/droid/version.h
%{_prefix}/include/pulsecore/modules/droid/conversion.h
%{_prefix}/include/pulsecore/modules/droid/droid-config.h
%{_prefix}/include/pulsecore/modules/droid/droid-util.h
%{_libdir}/pkgconfig/*.pc
