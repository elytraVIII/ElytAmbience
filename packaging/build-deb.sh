#!/bin/bash
set -e

# Get version from meson.build
VERSION=$(grep "version:" meson.build | head -n1 | cut -d"'" -f2)
echo "Building Debian package for version ${VERSION}..."

# Setup separate Linux build system
cp meson_linux.build meson.build

# Setup and build
rm -rf build staging
meson setup build --prefix=/usr
meson compile -C build

# Install to staging directory
mkdir -p staging
DESTDIR=$(pwd)/staging meson install -C build

# Prepare Debian control file
mkdir -p staging/DEBIAN
cp packaging/debian/control.in staging/DEBIAN/control
sed -i "s/%%VERSION%%/${VERSION}/g" staging/DEBIAN/control

# Build package
dpkg-deb --build staging "elytambiance_${VERSION}_all.deb"

# Clean up and restore FreeBSD build system
rm -rf staging
git checkout meson.build
echo "Debian package successfully built: elytambiance_${VERSION}_all.deb"
