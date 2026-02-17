#!/usr/bin/env python3
# Oply Video Player - Estilo Celluloid/GNOME
# Autor: josejp2424
# Versión: 2.1 (GTK3)
# License: GPL-3.0
# ====================================================================
# GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
# Copyright (C) 2025 josejp2424
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Author: josejp2424
# Proyecto: Oply
# ====================================================================

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio
from mpv import MPV
import json
import os
import locale
import sys
from pathlib import Path

CONFIG_DIR = os.path.expanduser("~/.config/oply")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LANG_FILE = os.path.join(CONFIG_DIR, "language.json")
ICON_PATH = "/usr/local/Oply/icons/oply.svg"

LANGUAGES = {
    "en": {
        "fullscreen": "Fullscreen",
        "title": "Oply Video Player",
        "open": "Open",
        "play_pause": "Play/Pause",
        "stop": "Stop",
        "volume": "Volume",
        "exit": "Exit",
        "subtitle": "No video loaded",
        "playing": "Playing"
    },
    "es": {
        "fullscreen": "Pantalla completa",
        "title": "Oply Reproductor de Video",
        "open": "Abrir",
        "play_pause": "Reproducir/Pausa",
        "stop": "Detener",
        "volume": "Volumen",
        "exit": "Salir",
        "subtitle": "Sin video cargado",
        "playing": "Reproduciendo"
    },
    "fr": {
        "fullscreen": "Plein écran",
        "title": "Lecteur Vidéo Oply",
        "open": "Ouvrir",
        "play_pause": "Lecture/Pause",
        "stop": "Arrêter",
        "volume": "Volume",
        "exit": "Quitter",
        "subtitle": "Aucune vidéo chargée",
        "playing": "Lecture en cours"
    },
    "it": {
        "fullscreen": "Schermo intero",
        "title": "Lettore Video Oply",
        "open": "Apri",
        "play_pause": "Riproduci/Pausa",
        "stop": "Ferma",
        "volume": "Volume",
        "exit": "Esci",
        "subtitle": "Nessun video caricato",
        "playing": "Riproduzione"
    },
    "pt": {
        "fullscreen": "Tela cheia",
        "title": "Oply Reprodutor de Vídeo",
        "open": "Abrir",
        "play_pause": "Reproduzir/Pausa",
        "stop": "Parar",
        "volume": "Volume",
        "exit": "Sair",
        "subtitle": "Nenhum vídeo carregado",
        "playing": "Reproduzindo"
    },
    "ca": {
        "fullscreen": "Pantalla completa",
        "title": "Oply Reproductor de Vídeo",
        "open": "Obrir",
        "play_pause": "Reproduir/Pausa",
        "stop": "Aturar",
        "volume": "Volum",
        "exit": "Sortir",
        "subtitle": "Sense vídeo carregat",
        "playing": "Reproduint"
    },
    "ar": {
        "fullscreen": "ملء الشاشة",
        "title": "مشغل فيديو Oply",
        "open": "فتح",
        "play_pause": "تشغيل/إيقاف مؤقت",
        "stop": "إيقاف",
        "volume": "مستوى الصوت",
        "exit": "خروج",
        "subtitle": "لم يتم تحميل فيديو",
        "playing": "قيد التشغيل"
    },
    "hu": {
        "fullscreen": "Teljes képernyő",
        "title": "Oply Videolejátszó",
        "open": "Megnyitás",
        "play_pause": "Lejátszás/Szünet",
        "stop": "Leállítás",
        "volume": "Hangerő",
        "exit": "Kilépés",
        "subtitle": "Nincs videó betöltve",
        "playing": "Lejátszás"
    },
    "ru": {
        "fullscreen": "Полноэкранный",
        "title": "Oply Видеоплеер",
        "open": "Открыть",
        "play_pause": "Воспроизведение/Пауза",
        "stop": "Стоп",
        "volume": "Громкость",
        "exit": "Выход",
        "subtitle": "Видео не загружено",
        "playing": "Воспроизведение"
    },
    "ja": {
        "fullscreen": "全画面",
        "title": "Oply ビデオプレーヤー",
        "open": "開く",
        "play_pause": "再生/一時停止",
        "stop": "停止",
        "volume": "音量",
        "exit": "終了",
        "subtitle": "ビデオが読み込まれていません",
        "playing": "再生中"
    },
    "zh": {
        "fullscreen": "全屏",
        "title": "Oply 视频播放器",
        "open": "打开",
        "play_pause": "播放/暂停",
        "stop": "停止",
        "volume": "音量",
        "exit": "退出",
        "subtitle": "未加载视频",
        "playing": "正在播放"
    }
}

def set_language(lang_code=None):
    if not lang_code:
        try:
            sys_lang = locale.getdefaultlocale()[0][:2]
            lang_code = sys_lang if sys_lang in LANGUAGES else "en"
        except:
            lang_code = "en"
    return LANGUAGES.get(lang_code, LANGUAGES["en"])

def load_language():
    try:
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, "r") as f:
                config = json.load(f)
                return set_language(config.get("language"))
    except:
        pass
    return set_language()

class OplyVideoPlayer(Gtk.Window):
    def __init__(self, initial_file=None):
        super().__init__(title="Oply Video Player")
        
        self.text = load_language()
        self.is_fullscreen = False
        self.updating_progress = True
        
        self.set_default_size(900, 550)
        self.set_position(Gtk.WindowPosition.CENTER)
        
   
        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except:
                pass
        
 
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = self.text["title"]
        hb.props.subtitle = self.text["subtitle"]
        self.set_titlebar(hb)
        self.headerbar = hb
        
   
        icon_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_PATH, 32, 32, True)
                icon_image = Gtk.Image.new_from_pixbuf(pixbuf)
                icon_image.set_margin_start(5)
                icon_image.set_margin_end(10)
                icon_box.pack_start(icon_image, False, False, 0)
            except Exception as e:
                print(f"Error loading icon: {e}")
        hb.pack_start(icon_box)
        
   
        btn_open = Gtk.Button()
        btn_open.add(Gtk.Image.new_from_icon_name("document-open-symbolic", Gtk.IconSize.BUTTON))
        btn_open.set_tooltip_text(self.text["open"])
        btn_open.connect("clicked", self.on_open_file)
        hb.pack_start(btn_open)
        
   
        self.menu_button = Gtk.MenuButton()
        self.menu_button.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        self.create_menu()
        hb.pack_end(self.menu_button)
        
  
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)
        
   
        self.video_area = Gtk.DrawingArea()
        self.video_area.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
        main_vbox.pack_start(self.video_area, True, True, 0)
        
 
        self.setup_drag_drop()
        
   
        self.progress_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.progress_scale.set_draw_value(False)
        self.progress_scale.set_margin_start(10)
        self.progress_scale.set_margin_end(10)
        self.progress_scale.connect("button-press-event", self.on_progress_press)
        self.progress_scale.connect("button-release-event", self.on_progress_release)
        main_vbox.pack_start(self.progress_scale, False, False, 0)
        
    
        controls_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        controls_hbox.set_border_width(10)
        main_vbox.pack_start(controls_hbox, False, False, 0)
        
    
        self.btn_play = Gtk.Button()
        self.btn_play.add(Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON))
        self.btn_play.get_style_context().add_class("circular")
        self.btn_play.connect("clicked", self.on_play_pause)
        controls_hbox.pack_start(self.btn_play, False, False, 0)
        
    
        btn_stop = Gtk.Button.new_from_icon_name("media-playback-stop-symbolic", Gtk.IconSize.BUTTON)
        btn_stop.connect("clicked", self.on_stop)
        controls_hbox.pack_start(btn_stop, False, False, 0)
        
      
        btn_rev = Gtk.Button.new_from_icon_name("media-seek-backward-symbolic", Gtk.IconSize.BUTTON)
        btn_rev.set_tooltip_text("Retroceder 10s")
        btn_rev.connect("clicked", lambda x: self.seek_relative(-10))
        controls_hbox.pack_start(btn_rev, False, False, 0)
        
        btn_fwd = Gtk.Button.new_from_icon_name("media-seek-forward-symbolic", Gtk.IconSize.BUTTON)
        btn_fwd.set_tooltip_text("Avanzar 10s")
        btn_fwd.connect("clicked", lambda x: self.seek_relative(10))
        controls_hbox.pack_start(btn_fwd, False, False, 0)
        
     
        self.lbl_time = Gtk.Label(label="00:00:00 / 00:00:00")
        controls_hbox.pack_start(self.lbl_time, False, False, 5)
        
     
        controls_hbox.pack_start(Gtk.Box(), True, True, 0)
        
     
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        controls_hbox.pack_end(right_box, False, False, 0)
        
        btn_vol = Gtk.Button.new_from_icon_name("audio-volume-high-symbolic", Gtk.IconSize.BUTTON)
        right_box.pack_start(btn_vol, False, False, 0)
        
        self.vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.vol_scale.set_value(50)
        self.vol_scale.set_size_request(100, -1)
        self.vol_scale.set_draw_value(False)
        self.vol_scale.connect("value-changed", self.on_volume_changed)
        right_box.pack_start(self.vol_scale, False, False, 0)
        
        btn_fs = Gtk.Button.new_from_icon_name("view-fullscreen-symbolic", Gtk.IconSize.BUTTON)
        btn_fs.set_tooltip_text(self.text["fullscreen"])
        btn_fs.connect("clicked", self.on_fullscreen)
        right_box.pack_start(btn_fs, False, False, 0)
        
      
        self.connect("destroy", self.on_destroy)
        self.connect("realize", self.on_realize)
        
      
        self.player = None
        self.initial_file = initial_file
        
        self.show_all()
    
    def create_menu(self):
        menu = Gio.Menu()
        menu.append(self.text["open"], "win.open")
        menu.append(self.text["fullscreen"], "win.fullscreen")
        menu.append(self.text["exit"], "win.quit")
        
        self.menu_button.set_menu_model(menu)
        
       
        action_group = Gio.SimpleActionGroup()
        
      
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", lambda a, p: self.on_open_file(None))
        action_group.add_action(open_action)
        
        fs_action = Gio.SimpleAction.new("fullscreen", None)
        fs_action.connect("activate", lambda a, p: self.on_fullscreen(None))
        action_group.add_action(fs_action)
        
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda a, p: self.close())
        action_group.add_action(quit_action)
        
        self.insert_action_group("win", action_group)
    
    def setup_drag_drop(self):
        targets = [Gtk.TargetEntry.new("text/uri-list", 0, 0)]
        self.video_area.drag_dest_set(
            Gtk.DestDefaults.ALL,
            targets,
            Gdk.DragAction.COPY
        )
        self.video_area.connect("drag-data-received", self.on_drag_data_received)
    
    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        if uris:
            path = uris[0].replace("file://", "")
            import urllib.parse
            path = urllib.parse.unquote(path)
            if os.path.isfile(path):
                self.play_file(path)
    
    def on_realize(self, widget):
     
        GLib.timeout_add(100, self.init_mpv)
    
    def init_mpv(self):
        """Inicializar MPV después de que la ventana esté lista"""
        window = self.video_area.get_window()
        if not window:
            return True  
        
        try:
            wid = window.get_xid()
            self.player = MPV(
                wid=str(wid),
                vo="x11",
                input_default_bindings=True,
                input_vo_keyboard=True
            )
            self.player.volume = 50
            
            GLib.timeout_add(1000, self.update_progress)
            
            if self.initial_file and os.path.isfile(self.initial_file):
                self.play_file(self.initial_file)
            
            return False 
        except Exception as e:
            print(f"Error inicializando MPV: {e}")
            return True  
    
    def on_open_file(self, button):
        dialog = Gtk.FileChooserDialog(
            title=self.text["open"],
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_video = Gtk.FileFilter()
        filter_video.set_name("Videos")
        filter_video.add_mime_type("video/*")
        dialog.add_filter(filter_video)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            self.play_file(filepath)
        
        dialog.destroy()
    
    def on_play_pause(self, button):
        if self.player:
            self.player.cycle("pause")
    
    def on_stop(self, button):
        if self.player:
            self.player.stop()
            self.headerbar.props.subtitle = self.text["subtitle"]
    
    def on_volume_changed(self, scale):
        if self.player:
            volume = scale.get_value()
            self.player.volume = volume
    
    def on_progress_press(self, widget, event):
        self.updating_progress = False
    
    def on_progress_release(self, widget, event):
        if not self.player:
            self.updating_progress = True
            return
        
        try:
            if self.player.duration:
                target = (self.progress_scale.get_value() / 100) * self.player.duration
                self.player.seek(target, reference="absolute")
        except:
            pass
        finally:
            self.updating_progress = True
    
    def seek_relative(self, seconds):
        if self.player:
            try:
                self.player.seek(seconds, reference="relative")
            except:
                pass
    
    def update_progress(self):
        try:
            if self.player and self.player.duration and self.updating_progress:
                pos = self.player.time_pos or 0
                dur = self.player.duration or 1
                progress = (pos / dur) * 100
                self.progress_scale.set_value(progress)
                
             
                pos_str = self.format_time(pos)
                dur_str = self.format_time(dur)
                self.lbl_time.set_text(f"{pos_str} / {dur_str}")
        except:
            pass
        
        return True
    
    def format_time(self, seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        else:
            return f"{m:02d}:{s:02d}"
    
    def on_fullscreen(self, button):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.fullscreen()
        else:
            self.unfullscreen()
    
    def play_file(self, filepath):
        if self.player and os.path.isfile(filepath):
            self.player.play(filepath)
            filename = os.path.basename(filepath)
            self.headerbar.props.subtitle = f"{self.text['playing']}: {filename}"
    
    def on_destroy(self, widget):
        if self.player:
            try:
                self.player.terminate()
            except:
                pass
        Gtk.main_quit()

def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = OplyVideoPlayer(initial_file)
    Gtk.main()

if __name__ == "__main__":
    main()
