project('elytambiance',
  version: '0.3.0',
  meson_version: '>= 0.59.0',
)

python = import('python').find_installation('python3.11')
gnome = import('gnome')

# Paths
prefix = get_option('prefix')
datadir = get_option('datadir')
pkgdatadir = prefix / datadir / 'elytambiance'
moduledir = python.get_install_dir() / 'elytambiance'

# GResource
gnome.compile_resources('elytambiance',
  'data/elytambiance.gresource.xml',
  source_dir: '.',
  gresource_bundle: true,
  install_dir: pkgdatadir,
  install: true
)

# GSettings
install_data('data/org.elytlabs.elytambiance.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas'
)

# Python Modules
install_data([
    'elytambiance/__init__.py',
    'elytambiance/main.py',
    'elytambiance/window.py',
    'elytambiance/player.py',
    'elytambiance/mpris.py',
  ],
  install_dir: moduledir
)

# Launcher script
conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'bin/elytambiance.in',
  output: 'elytambiance',
  configuration: conf,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

# Assets (Sounds)
install_subdir('assets/sounds',
  install_dir: pkgdatadir
)

# Desktop file
install_data('elytambiance.desktop',
  install_dir: get_option('datadir') / 'applications'
)

# App icon
install_data('assets/icons/elytambiance.svg',
  install_dir: get_option('datadir') / 'icons/hicolor/scalable/apps'
)
