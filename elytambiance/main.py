import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib
from elytambiance.window import AmbientWindow

class ElytAmbienceApplication(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(
            application_id="org.elytlabs.elytambiance",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            **kwargs
        )
        self.pkgdatadir = os.environ.get('ELYTAMBIANCE_PKGDATADIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        self._load_resources()

    def _load_resources(self):
        resource_path = os.path.join(self.pkgdatadir, 'elytambiance.gresource')
        if os.path.exists(resource_path):
            try:
                resource = Gio.Resource.load(resource_path)
                resource._register()
            except Exception as e:
                print(f"Failed to load resource: {e}")
        else:
            # Local dev fallback: try to find it in build dir or current dir
            local_res = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'build', 'elytambiance.gresource'))
            if os.path.exists(local_res):
                resource = Gio.Resource.load(local_res)
                resource._register()

    def do_activate(self):
        win = self.get_active_window()
        if not win:
            sounds_path = os.path.join(self.pkgdatadir, 'sounds')
            if not os.path.exists(sounds_path):
                # Local dev fallback
                sounds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds'))
            
            icons_path = os.path.join(self.pkgdatadir, 'icons')
            win = AmbientWindow(self, sounds_path, icons_path)
        win.present()

def main():
    app = ElytAmbienceApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
