import os
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject
from elytambiance.player import AmbientPlayer

class AmbientWindow(Gtk.ApplicationWindow):
    def __init__(self, app, sounds_path: str, icons_path: str, **kwargs):
        super().__init__(application=app, title="ElytAmbience", **kwargs)
        self.set_icon_name("elytambiance")
        
        self.sounds_path = sounds_path
        self.icons_path = icons_path
        
        self.settings = Gio.Settings.new("org.elytlabs.elytambiance")
        self.player = AmbientPlayer(self.sounds_path)
        
        # UI Setup
        self.set_default_size(
            self.settings.get_int("window-width"),
            self.settings.get_int("window-height")
        )
        if self.settings.get_boolean("window-maximized"):
            self.maximize()

        # HeaderBar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.set_title("ElytAmbience")
        hb.set_subtitle("Ambient sounds for BSD")
        self.set_titlebar(hb)
        
        stop_btn = Gtk.Button()
        stop_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-stop-symbolic", Gtk.IconSize.BUTTON))
        stop_btn.connect("clicked", self.on_stop_all_clicked)
        hb.pack_start(stop_btn)
        
        self.play_pause_btn = Gtk.Button()
        self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))
        self.play_pause_btn.connect("clicked", self.on_play_pause_clicked)
        hb.pack_start(self.play_pause_btn)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolled)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(4)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(self.flowbox)

        # Tray Icon
        self.status_icon = Gtk.StatusIcon.new_from_icon_name("elytambiance")
        self.status_icon.set_tooltip_text("ElytAmbience")
        self.status_icon.connect("activate", self.on_tray_activate)
        self.status_icon.connect("popup-menu", self.on_tray_popup_menu)
        self.status_icon.set_visible(True)

        self.load_sounds()
        
        self.connect("configure-event", self.on_configure_event)
        self.connect("window-state-event", self.on_window_state_event)
        self.connect("delete-event", self.on_delete_event)

        self.show_all()

    def load_sounds(self):
        if not os.path.exists(self.sounds_path):
            return

        active_sounds = self.settings.get_strv("active-sounds")
        try:
            volumes = json.loads(self.settings.get_string("sound-volumes"))
        except:
            volumes = {}

        sound_files = sorted([f for f in os.listdir(self.sounds_path) if f.endswith('.ogg')])
        for filename in sound_files:
            slug = self.player.load_sound(filename)
            name = slug.replace('-', ' ').title()
            
            # Initial state from settings
            active = slug in active_sounds
            volume = volumes.get(slug, 0.5)
            self.player.set_volume(slug, volume)
            
            card = self.create_sound_card(name, slug, active, volume)
            self.flowbox.add(card)
            
            if active:
                self.player.toggle_sound(slug, True)
        self.show_all()

    def create_sound_card(self, name, slug, active, volume):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_size_request(140, 180)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)

        # Icon from resource
        icon_path = f"/org/elytlabs/elytambiance/assets/icons/com.rafaelmardojai.Blanket-{slug}-symbolic.svg"
        image = Gtk.Image.new_from_resource(icon_path)
        image.set_pixel_size(48)
        box.pack_start(image, False, False, 0)

        label = Gtk.Label(label=name)
        label.set_ellipsize(3)
        box.pack_start(label, False, False, 0)

        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.CENTER)
        switch.set_active(active)
        switch.connect("state-set", self.on_toggle_clicked, slug)
        box.pack_start(switch, False, False, 0)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        scale.set_value(volume * 100)
        scale.set_draw_value(False)
        scale.connect("value-changed", self.on_volume_changed, slug)
        box.pack_start(scale, False, False, 0)

        return box

    def on_toggle_clicked(self, switch, state, slug):
        self.player.toggle_sound(slug, state)
        self.save_state()
        return False

    def on_volume_changed(self, scale, slug):
        vol = scale.get_value() / 100.0
        self.player.set_volume(slug, vol)
        self.save_state()

    def on_play_pause_clicked(self, button):
        if self.player.is_playing:
            self.player.pause()
            self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON))
        else:
            self.player.play()
            self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))

    def on_stop_all_clicked(self, button):
        self.player.stop_all()
        self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))
        for child in self.flowbox.get_children():
            box = child.get_child()
            if isinstance(box, Gtk.Box):
                switch = box.get_children()[2]
                if isinstance(switch, Gtk.Switch):
                    switch.set_active(False)
        self.save_state()

    def save_state(self):
        active = []
        volumes = {}
        for slug, data in self.player.players.items():
            if data["active"]:
                active.append(slug)
            volumes[slug] = data["volume"]
        
        self.settings.set_strv("active-sounds", active)
        self.settings.set_string("sound-volumes", json.dumps(volumes))

    def on_configure_event(self, widget, event):
        if not self.is_maximized():
            self.settings.set_int("window-width", event.width)
            self.settings.set_int("window-height", event.height)

    def on_window_state_event(self, widget, event):
        self.settings.set_boolean("window-maximized", bool(event.new_window_state & Gdk.WindowState.MAXIMIZED))

    def on_delete_event(self, widget, event):
        self.hide()
        return True

    def on_tray_activate(self, icon):
        if self.is_visible():
            self.hide()
        else:
            self.present()

    def on_tray_popup_menu(self, icon, button, activate_time):
        menu = Gtk.Menu()
        
        item_show = Gtk.MenuItem(label="Show ElytAmbience")
        item_show.connect("activate", lambda w: self.present())
        menu.append(item_show)
        
        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda w: self.get_application().quit())
        menu.append(item_quit)
        
        menu.show_all()
        menu.popup(None, None, None, None, button, activate_time)
