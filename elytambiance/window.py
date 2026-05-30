import os
import json
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio, GObject, GLib
from elytambiance.player import AmbientPlayer
from elytambiance.mpris import MPRISManager

class AmbientWindow(Gtk.ApplicationWindow):
    def __init__(self, app, sounds_path: str, icons_path: str, **kwargs):
        super().__init__(application=app, title="ElytAmbience", **kwargs)
        self.set_icon_name("elytambiance")
        
        self.sounds_path = sounds_path
        self.icons_path = icons_path
        
        self.settings = Gio.Settings.new("org.elytlabs.elytambiance")
        self.player = AmbientPlayer(self.sounds_path)
        self.mpris = MPRISManager(self)
        self.sleep_timer_id = None
        self.sleep_timer_end_time = 0
        
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
        
        stop_btn = Gtk.Button(label="_Stop", use_underline=True)
        stop_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-stop-symbolic", Gtk.IconSize.BUTTON))
        stop_btn.set_always_show_image(True)
        stop_btn.set_tooltip_text("Stop all sounds (Alt+S)")
        stop_btn.connect("clicked", self.on_stop_all_clicked)
        hb.pack_start(stop_btn)
        
        self.play_pause_btn = Gtk.Button(label="_Play", use_underline=True)
        self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))
        self.play_pause_btn.set_always_show_image(True)
        self.play_pause_btn.set_tooltip_text("Play/Pause (Alt+P)")
        self.play_pause_btn.connect("clicked", self.on_play_pause_clicked)
        hb.pack_start(self.play_pause_btn)

        # Sleep Timer Button
        self.timer_btn = Gtk.MenuButton(label="_Timer", use_underline=True)
        self.timer_btn.set_image(Gtk.Image.new_from_icon_name("alarm-symbolic", Gtk.IconSize.BUTTON))
        self.timer_btn.set_always_show_image(True)
        self.timer_btn.set_tooltip_text("Sleep Timer (Alt+T)")
        
        self.timer_popover = Gtk.Popover()
        self.timer_popover.connect("map", self.on_popover_map)
        self.timer_btn.set_popover(self.timer_popover)
        self.update_timer_popover()
        
        hb.pack_end(self.timer_btn)
        
        self.timer_label = Gtk.Label()
        hb.pack_end(self.timer_label)

        # Help Button
        self.shortcuts_btn = Gtk.Button(label="_Help", use_underline=True)
        self.shortcuts_btn.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.BUTTON))
        self.shortcuts_btn.set_always_show_image(True)
        self.shortcuts_btn.set_tooltip_text("Keyboard Shortcuts (Alt+H or ?)")
        self.shortcuts_btn.connect("clicked", self.on_shortcuts_clicked)
        hb.pack_end(self.shortcuts_btn)

        # Presets Button
        self.presets_btn = Gtk.MenuButton(label="P_resets", use_underline=True)
        self.presets_btn.set_tooltip_text("Manage Presets (Alt+R)")
        
        self.presets_popover = Gtk.Popover()
        self.presets_popover.connect("map", self.on_popover_map)
        self.presets_btn.set_popover(self.presets_popover)
        self.update_presets_menu()
        
        hb.pack_end(self.presets_btn)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolled)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(4)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_can_focus(True)
        self.flowbox.set_activate_on_single_click(False)
        self.flowbox.connect("child-activated", self.on_child_activated)
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
        self.connect("key-press-event", self.on_key_press_event)

        self.show_all()
        self.timer_label.hide()

    def on_child_activated(self, flowbox, child):
        box = child.get_child()
        if isinstance(box, Gtk.Box):
            # The switch is the 3rd child (index 2)
            switch = box.get_children()[2]
            if isinstance(switch, Gtk.Switch):
                switch.set_active(not switch.get_active())

    def update_timer_popover(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        
        durations = [
            (0, "_Off"),
            (15, "_15 Minutes"),
            (30, "_30 Minutes"),
            (45, "_45 Minutes"),
            (60, "_60 Minutes"),
            (90, "_90 Minutes")
        ]
        
        for mins, label in durations:
            btn = Gtk.Button(label=label, use_underline=True)
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.get_child().set_xalign(0)
            btn.connect("clicked", lambda b, m=mins: (self.on_sleep_timer_selected(None, m), self.timer_popover.popdown()))
            vbox.pack_start(btn, False, False, 0)
            
        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 3)
        
        custom_btn = Gtk.Button(label="_Custom...", use_underline=True)
        custom_btn.set_relief(Gtk.ReliefStyle.NONE)
        custom_btn.get_child().set_xalign(0)
        custom_btn.connect("clicked", lambda b: (self.on_custom_timer_clicked(None), self.timer_popover.popdown()))
        vbox.pack_start(custom_btn, False, False, 0)
        
        vbox.show_all()
        
        child = self.timer_popover.get_child()
        if child:
            self.timer_popover.remove(child)
        self.timer_popover.add(vbox)

    def on_popover_map(self, popover):
        child = popover.get_child()
        if isinstance(child, Gtk.Container):
            inner_children = child.get_children()
            if inner_children:
                inner_children[0].grab_focus()
        elif child:
            child.grab_focus()

    def update_presets_menu(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_margin_top(10)
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        
        save_btn = Gtk.Button(label="S_ave Current as Preset...", use_underline=True)
        save_btn.connect("clicked", self.on_save_preset_clicked)
        vbox.pack_start(save_btn, False, False, 0)
        
        import_export_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        import_btn = Gtk.Button(label="_Import...", use_underline=True)
        import_btn.connect("clicked", self.on_import_preset_clicked)
        import_export_box.pack_start(import_btn, True, True, 0)
        
        export_btn = Gtk.Button(label="_Export All...", use_underline=True)
        export_btn.connect("clicked", self.on_export_presets_clicked)
        import_export_box.pack_start(export_btn, True, True, 0)
        vbox.pack_start(import_export_box, False, False, 0)
        
        vbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 3)
        
        try:
            presets = json.loads(self.settings.get_string("presets"))
        except:
            presets = {}
            
        if not presets:
            empty_label = Gtk.Label(label="No saved presets")
            empty_label.set_sensitive(False)
            vbox.pack_start(empty_label, False, False, 6)
        else:
            for name in sorted(presets.keys()):
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                
                label = Gtk.Label(label=name, xalign=0)
                hbox.pack_start(label, True, True, 0)
                
                btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                
                load_btn = Gtk.Button(label="Load")
                load_btn.connect("clicked", self.on_load_preset_btn_clicked, name)
                btn_box.pack_start(load_btn, False, False, 0)
                
                delete_btn = Gtk.Button()
                delete_btn.set_image(Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON))
                delete_btn.set_tooltip_text("Delete preset")
                delete_btn.connect("clicked", self.on_delete_preset_clicked, name)
                btn_box.pack_start(delete_btn, False, False, 0)
                
                hbox.pack_end(btn_box, False, False, 0)
                vbox.pack_start(hbox, False, False, 0)
                
        vbox.show_all()
        
        child = self.presets_popover.get_child()
        if child:
            self.presets_popover.remove(child)
            
        self.presets_popover.add(vbox)

    def on_save_preset_clicked(self, btn):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Save Preset"
        )
        dialog.format_secondary_text("Enter a name for your soundscape:")
        
        entry = Gtk.Entry()
        entry.set_activates_default(True)
        dialog.get_content_area().add(entry)
        dialog.show_all()
        
        if dialog.run() == Gtk.ResponseType.OK:
            name = entry.get_text().strip()
            if name:
                active = []
                volumes = {}
                for slug, data in self.player.players.items():
                    if data["active"]:
                        active.append(slug)
                    volumes[slug] = data["volume"]
                
                try:
                    presets = json.loads(self.settings.get_string("presets"))
                except:
                    presets = {}
                
                presets[name] = {"active": active, "volumes": volumes}
                self.settings.set_string("presets", json.dumps(presets))
                self.update_presets_menu()
                self.presets_popover.popdown()
        
        dialog.destroy()

    def on_import_preset_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Import Presets",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_mime_type("application/json")
        filter_json.add_pattern("*.json")
        dialog.add_filter(filter_json)
        
        if dialog.run() == Gtk.ResponseType.OK:
            try:
                with open(dialog.get_filename(), 'r') as f:
                    imported = json.load(f)
                    
                current = json.loads(self.settings.get_string("presets"))
                # Merge presets
                current.update(imported)
                self.settings.set_string("presets", json.dumps(current))
                self.update_presets_menu()
                self.presets_popover.popdown()
            except Exception as e:
                print(f"Failed to import presets: {e}")
                
        dialog.destroy()

    def on_export_presets_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Export Presets",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )
        dialog.set_current_name("elytambiance_presets.json")
        dialog.set_do_overwrite_confirmation(True)
        
        if dialog.run() == Gtk.ResponseType.OK:
            try:
                presets = self.settings.get_string("presets")
                with open(dialog.get_filename(), 'w') as f:
                    f.write(presets)
                self.presets_popover.popdown()
            except Exception as e:
                print(f"Failed to export presets: {e}")
                
        dialog.destroy()

    def on_load_preset_btn_clicked(self, btn, name):
        try:
            presets = json.loads(self.settings.get_string("presets"))
            preset = presets.get(name)
            if preset:
                self.apply_preset(preset.get("active", []), preset.get("volumes", {}))
                self.presets_popover.popdown()
        except Exception as e:
            print(f"Failed to load preset: {e}")

    def on_delete_preset_clicked(self, btn, name):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Delete Preset?"
        )
        dialog.format_secondary_text(f"Are you sure you want to delete '{name}'?")
        
        if dialog.run() == Gtk.ResponseType.OK:
            try:
                presets = json.loads(self.settings.get_string("presets"))
                if name in presets:
                    del presets[name]
                    self.settings.set_string("presets", json.dumps(presets))
                    self.update_presets_menu()
            except:
                pass
        
        dialog.destroy()

    def on_shortcuts_clicked(self, btn):
        shortcuts_window = Gtk.ShortcutsWindow(transient_for=self, modal=True)
        
        section = Gtk.ShortcutsSection()
        section.show()
        
        # Playback Group
        group_playback = Gtk.ShortcutsGroup(title="Playback")
        group_playback.show()
        
        playback_items = [
            ("Play / Pause", "space k <alt>p"),
            ("Stop all sounds", "s <alt>s"),
            ("Volume Up", "plus equal"),
            ("Volume Down", "minus underscore"),
        ]
        
        for title, accel in playback_items:
            shortcut = Gtk.ShortcutsShortcut(title=title, accelerator=accel)
            shortcut.show()
            group_playback.add(shortcut)
            
        section.add(group_playback)
        
        # Menus Group
        group_menus = Gtk.ShortcutsGroup(title="Menus")
        group_menus.show()
        
        menu_items = [
            ("Open Sleep Timer", "<alt>t"),
            ("Open Presets", "<alt>r"),
            ("Show Shortcuts", "h <alt>h question"),
        ]
        
        for title, accel in menu_items:
            shortcut = Gtk.ShortcutsShortcut(title=title, accelerator=accel)
            shortcut.show()
            group_menus.add(shortcut)
            
        section.add(group_menus)
        
        # Navigation Group
        group_nav = Gtk.ShortcutsGroup(title="Navigation")
        group_nav.show()
        
        nav_items = [
            ("Focus Sound Grid", "slash"),
            ("Toggle Focused Sound", "Return"),
            ("Close Menu / Popover", "Escape"),
            ("Quit", "<ctrl>q"),
        ]
        
        for title, accel in nav_items:
            shortcut = Gtk.ShortcutsShortcut(title=title, accelerator=accel)
            shortcut.show()
            group_nav.add(shortcut)
            
        section.add(group_nav)
        
        shortcuts_window.add(section)
        shortcuts_window.show_all()

    def on_key_press_event(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        state = event.state
        focused = self.get_focus()

        # Control shortcuts
        if state & Gdk.ModifierType.CONTROL_MASK:
            if keyname == "q":
                self.get_application().quit()
                return True
        
        popover_visible = self.presets_popover.is_visible() or self.timer_popover.is_visible()

        # Alt shortcuts
        if state & Gdk.ModifierType.MOD1_MASK:
            if keyname == "p" and not popover_visible:
                self.on_play_pause_clicked(None)
                return True
            elif keyname == "s" and not popover_visible:
                self.on_stop_all_clicked(None)
                return True

        # Avoid triggering shortcuts if an entry is focused
        if isinstance(focused, Gtk.Entry):
            if keyname == "Escape":
                self.flowbox.grab_focus()
                return True
            return False

        # If a popover is open, let GTK handle its own shortcuts/mnemonics
        if popover_visible:
            if keyname == "Escape":
                if self.presets_popover.is_visible():
                    self.presets_popover.popdown()
                if self.timer_popover.is_visible():
                    self.timer_popover.popdown()
                return True
            return False

        # Global shortcuts (only if no menu/popover is open)
        if keyname in ["space", "k"]:
            # If a switch, button, or slider is focused, let it handle space/enter
            if isinstance(focused, (Gtk.Switch, Gtk.Button, Gtk.Scale, Gtk.FlowBoxChild)):
                return False
            self.on_play_pause_clicked(None)
            return True
        elif keyname == "s":
            self.on_stop_all_clicked(None)
            return True
        elif keyname == "slash":
            self.flowbox.grab_focus()
            # Focus the first child if nothing is focused in flowbox
            if not self.flowbox.get_focus_child():
                children = self.flowbox.get_children()
                if children:
                    children[0].grab_focus()
            return True
        elif keyname == "question":
            self.on_shortcuts_clicked(None)
            return True
        elif keyname == "Escape":
            # Maybe focus back to flowbox if something else is focused
            if focused != self.flowbox:
                self.flowbox.grab_focus()
                return True

        # Volume control for focused sound card
        if keyname in ["plus", "equal", "minus", "underscore"]:
            if focused:
                # Find if focused is a Scale or child of FlowBoxChild
                scale = None
                if isinstance(focused, Gtk.Scale):
                    scale = focused
                else:
                    # Traverse up to find FlowBoxChild and then find Scale inside it
                    parent = focused
                    while parent and not isinstance(parent, Gtk.FlowBoxChild):
                        parent = parent.get_parent()
                    
                    if parent:
                        box = parent.get_child()
                        if isinstance(box, Gtk.Box):
                            scale = box.get_children()[3]
                
                if scale:
                    val = scale.get_value()
                    delta = 5 if keyname in ["plus", "equal"] else -5
                    scale.set_value(max(0, min(100, val + delta)))
                    return True

        return False

    def on_custom_timer_clicked(self, item):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Custom Sleep Timer"
        )
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.format_secondary_text("Enter minutes until pause:")
        
        # Use a SpinButton for numerical input
        adjustment = Gtk.Adjustment(value=30, lower=1, upper=1440, step_increment=1, page_increment=10, page_size=0)
        spin = Gtk.SpinButton(adjustment=adjustment, climb_rate=0, digits=0)
        spin.set_activates_default(True)
        spin.set_halign(Gtk.Align.CENTER)
        spin.set_margin_top(10)
        
        dialog.get_content_area().add(spin)
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            mins = int(spin.get_value())
            self.on_sleep_timer_selected(None, mins)
        
        dialog.destroy()

    def on_sleep_timer_selected(self, item, mins):
        if self.sleep_timer_id:
            GLib.source_remove(self.sleep_timer_id)
            self.sleep_timer_id = None
            
        if mins > 0:
            self.sleep_timer_end_time = time.time() + (mins * 60)
            self.sleep_timer_id = GLib.timeout_add_seconds(1, self.update_timer_indication)
            self.timer_label.show()
            self.update_timer_indication()
        else:
            self.timer_label.hide()
            self.timer_btn.set_tooltip_text("Sleep Timer")

    def update_timer_indication(self):
        remaining = int(self.sleep_timer_end_time - time.time())
        if remaining <= 0:
            self.on_sleep_timer_timeout()
            return False
            
        mm, ss = divmod(remaining, 60)
        time_str = f"{mm:02d}:{ss:02d}"
        self.timer_label.set_markup(f"<span size='small' color='gray'>{time_str}</span>")
        self.timer_btn.set_tooltip_text(f"Sleep Timer: {time_str} remaining")
        return True

    def on_sleep_timer_timeout(self):
        self.player.pause()
        self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON))
        self.play_pause_btn.set_label("_Play")
        self.sleep_timer_id = None
        self.timer_label.hide()
        self.timer_btn.set_tooltip_text("Sleep Timer")
        return False

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
        
        # Update button to match actual playing state
        if any(data["active"] for data in self.player.players.values()):
            self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))
            self.play_pause_btn.set_label("_Pause")
        
        self.show_all()

    def create_sound_card(self, name, slug, active, volume):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.slug = slug 
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
        switch.set_can_focus(True)
        switch.connect("state-set", self.on_toggle_clicked, slug)
        box.pack_start(switch, False, False, 0)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        scale.set_value(volume * 100)
        scale.set_draw_value(False)
        scale.set_can_focus(True)
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
            self.play_pause_btn.set_label("_Play")
        else:
            self.player.play()
            self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))
            self.play_pause_btn.set_label("_Pause")

    def on_stop_all_clicked(self, button):
        self.player.stop_all()
        self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON))
        self.play_pause_btn.set_label("_Play")
        for child in self.flowbox.get_children():
            box = child.get_child()
            if isinstance(box, Gtk.Box):
                switch = box.get_children()[2]
                if isinstance(switch, Gtk.Switch):
                    switch.set_active(False)
        self.save_state()

    def apply_preset(self, active_sounds, volumes):
        self.player.stop_all()
        self.player.is_playing = True
        self.play_pause_btn.set_image(Gtk.Image.new_from_icon_name("media-playback-pause-symbolic", Gtk.IconSize.BUTTON))
        self.play_pause_btn.set_label("_Pause")
        
        for child in self.flowbox.get_children():
            box = child.get_child()
            slug = getattr(box, 'slug', None)
            if not slug: continue
            
            switch = box.get_children()[2]
            scale = box.get_children()[3]
            
            active = slug in active_sounds
            volume = volumes.get(slug, 0.5)
            
            switch.set_active(active)
            scale.set_value(volume * 100)
            self.player.set_volume(slug, volume)
            if active:
                self.player.toggle_sound(slug, True)
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
        
        item_show = Gtk.MenuItem.new_with_mnemonic("_Show ElytAmbience")
        item_show.connect("activate", lambda w: self.present())
        menu.append(item_show)
        
        item_quit = Gtk.MenuItem.new_with_mnemonic("_Quit")
        item_quit.connect("activate", lambda w: self.get_application().quit())
        menu.append(item_quit)
        
        menu.show_all()
        menu.popup(None, None, None, None, button, activate_time)
