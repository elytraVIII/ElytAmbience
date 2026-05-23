import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, GLib

MPRIS_INTERFACE_XML = """
<node>
  <interface name="org.mpris.MediaPlayer2">
    <method name="Raise"/>
    <method name="Quit"/>
    <property name="CanQuit" type="b" access="read"/>
    <property name="CanRaise" type="b" access="read"/>
    <property name="HasTrackList" type="b" access="read"/>
    <property name="Identity" type="s" access="read"/>
    <property name="SupportedUriSchemes" type="as" access="read"/>
    <property name="SupportedMimeTypes" type="as" access="read"/>
  </interface>
  <interface name="org.mpris.MediaPlayer2.Player">
    <method name="Next"/>
    <method name="Previous"/>
    <method name="Pause"/>
    <method name="PlayPause"/>
    <method name="Stop"/>
    <method name="Play"/>
    <method name="Seek">
      <arg direction="in" name="Offset" type="x"/>
    </method>
    <method name="SetPosition">
      <arg direction="in" name="TrackId" type="o"/>
      <arg direction="in" name="Position" type="x"/>
    </method>
    <method name="OpenUri">
      <arg direction="in" name="Uri" type="s"/>
    </method>
    <property name="PlaybackStatus" type="s" access="read"/>
    <property name="LoopStatus" type="s" access="readwrite"/>
    <property name="Rate" type="d" access="readwrite"/>
    <property name="Shuffle" type="b" access="readwrite"/>
    <property name="Metadata" type="a{sv}" access="read"/>
    <property name="Volume" type="d" access="readwrite"/>
    <property name="Position" type="x" access="read"/>
    <property name="MinimumRate" type="d" access="read"/>
    <property name="MaximumRate" type="d" access="read"/>
    <property name="CanGoNext" type="b" access="read"/>
    <property name="CanGoPrevious" type="b" access="read"/>
    <property name="CanPlay" type="b" access="read"/>
    <property name="CanPause" type="b" access="read"/>
    <property name="CanSeek" type="b" access="read"/>
    <property name="CanControl" type="b" access="read"/>
  </interface>
</node>
"""

class MPRISManager:
    def __init__(self, window):
        self.window = window
        self.player = window.player
        
        self.node_info = Gio.DBusNodeInfo.new_for_xml(MPRIS_INTERFACE_XML)
        self.owner_id = Gio.bus_own_name(
            Gio.BusType.SESSION,
            "org.mpris.MediaPlayer2.elytambiance",
            Gio.BusNameOwnerFlags.NONE,
            self.on_bus_acquired,
            None, None
        )

    def on_bus_acquired(self, conn, name):
        for interface in self.node_info.interfaces:
            if interface.name == "org.mpris.MediaPlayer2":
                conn.register_object(
                    "/org/mpris/MediaPlayer2",
                    interface,
                    self.handle_method_call,
                    self.get_property,
                    None
                )
            elif interface.name == "org.mpris.MediaPlayer2.Player":
                conn.register_object(
                    "/org/mpris/MediaPlayer2",
                    interface,
                    self.handle_method_call,
                    self.get_property,
                    None
                )

    def handle_method_call(self, conn, sender, path, interface, method, params, invocation):
        if interface == "org.mpris.MediaPlayer2":
            if method == "Raise":
                GLib.idle_add(self.window.present)
            elif method == "Quit":
                GLib.idle_add(self.window.get_application().quit)
        elif interface == "org.mpris.MediaPlayer2.Player":
            if method == "PlayPause":
                GLib.idle_add(self.window.on_play_pause_clicked, None)
            elif method == "Play":
                if not self.player.is_playing:
                    GLib.idle_add(self.window.on_play_pause_clicked, None)
            elif method == "Pause":
                if self.player.is_playing:
                    GLib.idle_add(self.window.on_play_pause_clicked, None)
            elif method == "Stop":
                GLib.idle_add(self.window.on_stop_all_clicked, None)
        
        invocation.return_value(None)

    def get_property(self, conn, sender, path, interface, prop):
        if interface == "org.mpris.MediaPlayer2":
            if prop == "CanQuit": return GLib.Variant("b", True)
            if prop == "CanRaise": return GLib.Variant("b", True)
            if prop == "HasTrackList": return GLib.Variant("b", False)
            if prop == "Identity": return GLib.Variant("s", "ElytAmbience")
            if prop == "SupportedUriSchemes": return GLib.Variant("as", [])
            if prop == "SupportedMimeTypes": return GLib.Variant("as", [])
        elif interface == "org.mpris.MediaPlayer2.Player":
            if prop == "PlaybackStatus":
                status = "Playing" if self.player.is_playing else "Paused"
                return GLib.Variant("s", status)
            if prop == "CanControl": return GLib.Variant("b", True)
            if prop == "CanPlay": return GLib.Variant("b", True)
            if prop == "CanPause": return GLib.Variant("b", True)
            if prop == "Volume": return GLib.Variant("d", 1.0)
            if prop == "Metadata":
                return GLib.Variant("a{sv}", {
                    "mpris:trackid": GLib.Variant("o", "/org/elytlabs/elytambiance/mpris"),
                    "xesam:title": GLib.Variant("s", "Ambient Sounds"),
                    "xesam:artist": GLib.Variant("as", ["ElytAmbience"])
                })
        return None
