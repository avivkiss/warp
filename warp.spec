Summary: warp UDT-based file transfer
Name: warp
Version: 0.1
Release: 2
License: GPL
Vendor: University of California
Group: System Environment/Base
Source: %{name}-%{version}.tar.gz
%define _topdir %(echo $PWD)/
%define pkgroot /opt/%{name}

%description
UDT is a reliable UDP based application level data transport protocol for 
distributed data intensive applications over wide area high-speed networks.
Warp is a nice command-line client, written in Python, around UDT
%prep
%setup 
%build
printf "\n\n\n### build ###\n\n\n"
%install
printf "\n\n\n### install ###\n\n\n"

ROOT=$RPM_BUILD_ROOT
INSTALL=/usr/bin/install 

mkdir -p $ROOT/%{pkgroot}
mkdir -p $ROOT/usr/bin
		
$INSTALL *.py $ROOT/%{pkgroot} 
$INSTALL -m 755 warp.sh $ROOT/usr/bin/warp
$INSTALL -m 755 server.sh $ROOT/usr/bin/warp-server

%files 
%{pkgroot}
/usr/bin/*

