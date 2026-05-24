import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

class AmbientPlayer:
    def __init__(self, sounds_path: str):
        Gst.init(None)
        self.sounds_path = sounds_path
        self.players = {} # slug: {"playbin": Gst.Element, "active": bool, "volume": float}
        self.is_playing = True

    def load_sound(self, filename: str):
        slug = filename.replace('.ogg', '')
        playbin = Gst.ElementFactory.make("playbin", f"player_{slug}")
        uri = "file://" + os.path.join(self.sounds_path, filename)
        playbin.set_property("uri", uri)
        
        bus = playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self._on_eos)
        
        self.players[slug] = {
            "playbin": playbin,
            "active": False,
            "volume": 0.5
        }
        playbin.set_property("volume", 0.5)
        return slug

    def toggle_sound(self, slug: str, state: bool):
        player_data = self.players.get(slug)
        if not player_data:
            return
            
        if state:
            player_data["active"] = True
            if self.is_playing:
                player_data["playbin"].set_state(Gst.State.PLAYING)
            else:
                player_data["playbin"].set_state(Gst.State.PAUSED)
        else:
            player_data["playbin"].set_state(Gst.State.NULL)
            player_data["active"] = False

    def set_volume(self, slug: str, volume: float):
        player_data = self.players.get(slug)
        if player_data:
            player_data["playbin"].set_property("volume", volume)
            player_data["volume"] = volume

    def stop_all(self):
        self.is_playing = False
        for slug, data in self.players.items():
            data["playbin"].set_state(Gst.State.NULL)
            data["active"] = False

    def pause(self):
        self.is_playing = False
        for slug, data in self.players.items():
            if data["active"]:
                data["playbin"].set_state(Gst.State.PAUSED)

    def play(self):
        self.is_playing = True
        for slug, data in self.players.items():
            if data["active"]:
                data["playbin"].set_state(Gst.State.PLAYING)

    def _on_eos(self, bus, message):
        player = message.src
        player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
