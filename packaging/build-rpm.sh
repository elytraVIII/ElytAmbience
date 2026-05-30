#!/bin/bash
set -e

# Get version from meson.build
VERSION=$(grep "version:" meson.build | head -n1 | cut -d"'" -f2)
echo "Building RPM package for version ${VERSION}..."

# Setup separate Linux build system
cp meson_linux.build meson.build

# Setup and build
rm -rf build staging rpmbuild
meson setup build --prefix=/usr
meson compile -C build

# Install to staging directory
mkdir -p staging
DESTDIR=$(pwd)/staging meson install -C build

# Prepare rpmbuild workspace
mkdir -p rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
STAGING_DIR=$(pwd)/staging

# Generate Spec file
cp packaging/rpm/elytambiance.spec.in rpmbuild/SPECS/elytambiance.spec
sed -i "s|%%VERSION%%|${VERSION}|g" rpmbuild/SPECS/elytambiance.spec
sed -i "s|%%STAGING_DIR%%|${STAGING_DIR}|g" rpmbuild/SPECS/elytambiance.spec

# Build package
rpmbuild -bb --define "_topdir $(pwd)/rpmbuild" rpmbuild/SPECS/elytambiance.spec

# Copy generated RPM to root
cp rpmbuild/RPMS/noarch/*.rpm .

# Clean up and restore FreeBSD build system
rm -rf staging rpmbuild
git checkout meson.build
echo "RPM package successfully built!"
