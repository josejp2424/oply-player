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
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio, Pango
from mpv import MPV
import json
import os
import pwd
import locale
import sys
from pathlib import Path


TV_SIDEBAR_WIDTH = 280

_oply_bin = "/usr/local/Oply/bin"
if os.path.isdir(_oply_bin):
    os.environ["PATH"] = _oply_bin + ":" + os.environ.get("PATH", "")

def get_real_home():
    """Evita escribir en /root cuando se ejecuta vía sudo/pkexec."""
    try:
        if os.geteuid() == 0:
            sudo_user = os.environ.get("SUDO_USER")
            if sudo_user:
                return pwd.getpwnam(sudo_user).pw_dir
            pkuid = os.environ.get("PKEXEC_UID")
            if pkuid and pkuid.isdigit():
                return pwd.getpwuid(int(pkuid)).pw_dir
    except Exception:
        pass
    return os.path.expanduser("~")

REAL_HOME = get_real_home()

CONFIG_DIR = os.path.join(REAL_HOME, ".config", "oply")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LANG_FILE = os.path.join(CONFIG_DIR, "language.json")
ICON_PATH = "/usr/local/Oply/icons/oply-video.svg"

TV_INDEX_FILE = os.path.join(CONFIG_DIR, "tv_index.json")
TV_CHANNELS_FILE = os.path.join(CONFIG_DIR, "tv_channels.json")

OPLY_DIR = "/usr/local/Oply"
ICONS_DIR = os.path.join(OPLY_DIR, "icons")
TV_ICONS_DIR = os.path.join(ICONS_DIR, "tv")
TV_FLAGS_DIR = os.path.join(TV_ICONS_DIR, "flags")
TV_INDEXER = os.path.join(OPLY_DIR, "oply-tv-indexer.py")


TV_CHANNELS = [
    {
        "id": "cgtn_news",
        "name": "CGTN News",
        "url": "https://www.youtube.com/watch?v=_6dRRfnYJws",
        "icon": "cgtn_news.png",
    },
    {
        "id": "fox_news",
        "name": "FOX News",
        "url": "https://www.youtube.com/watch?v=ZvdiJUYGBis",
        "icon": "fox_news.png",
    },
    {
        "id": "cbsn_news",
        "name": "CBSN News",
        "url": "https://cbsn-us.cbsnstream.cbsnews.com/out/v1/55a8648e8f134e82a470f83d562deeca/master.m3u8",
        "icon": "cbsn_news.png",
    },
    {
        "id": "cna_news",
        "name": "CNA (Singapore)",
        "url": "https://www.youtube.com/watch?v=XWq5kBlakcQ",
        "icon": "cna_news.png",
    },
    {
        "id": "sky_newsuk",
        "name": "Sky News (UK)",
        "url": "https://www.youtube.com/watch?v=YDvsBbKfLPA",
        "icon": "sky_news.png",
    },
    {
        "id": "aljazeera_hd",
        "name": "Al Jazeera English",
        "url": "https://www.youtube.com/watch?v=gCNeDWCI0vo",
        "icon": "aljazeera_hd.png",
    },
    {
        "id": "france24_news",
        "name": "France 24 (English)",
        "url": "https://www.youtube.com/watch?v=Ap-UM1O9RBU",
        "icon": "france24_news.png",
    },
    {
        "id": "abc_news_live",
        "name": "ABC News Live (AU)",
        "url": "https://www.youtube.com/watch?v=vOTiJkg1voo",
        "icon": "abc_news_live.png",
    },
    {
        "id": "dw_news",
        "name": "DW News",
        "url": "https://www.youtube.com/watch?v=LuKwFajn37U",
        "icon": "dw_news.png",
    },
    {
        "id": "euro_news",
        "name": "Euronews",
        "url": "https://www.youtube.com/watch?v=pykpO5kQJ98",
        "icon": "euro_news.png",
    },
]

def load_tv_channels():
    """Permite que el usuario reemplace/actualice URLs sin tocar el script.

    Archivo opcional: ~/.config/oply/tv_channels.json
    Formato: lista de objetos con keys: name, url, icon (opcional), id (opcional)
    """
    try:
        if os.path.exists(TV_CHANNELS_FILE):
            with open(TV_CHANNELS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                out = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    name = str(item.get("name", "")).strip()
                    url = str(item.get("url", "")).strip()
                    if not name or not url:
                        continue
                    out.append({
                        "id": str(item.get("id", name)).strip() or name,
                        "name": name,
                        "url": url,
                        "icon": str(item.get("icon", "")).strip() or None,
                    })
                if out:
                    return out
    except Exception:
        pass
    return TV_CHANNELS


def read_tv_index():
    try:
        if os.path.exists(TV_INDEX_FILE):
            with open(TV_INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None

def write_tv_index_active(locale_code: str):
    try:
        idx = read_tv_index()
        if not idx:
            return
        idx["active_locale"] = locale_code
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(TV_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(idx, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def channels_file_for_locale(locale_code: str) -> str:
    return os.path.join(CONFIG_DIR, f"tv_channels_{locale_code}.json")

def load_tv_channels_for_locale(locale_code: str):
    """Carga canales para un locale.

    - Si existe ~/.config/oply/tv_channels_<locale>.json, se usa.
    - Si no existe, se crea automáticamente (copiando la lista base) para que el usuario pueda editarla.
    """
    p = channels_file_for_locale(locale_code)

    def _sanitize(data):
        out = []
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                name = str(item.get("name","")).strip()
                url = str(item.get("url","")).strip()
                if not name or not url:
                    continue
                out.append({
                    "id": str(item.get("id", name)).strip() or name,
                    "name": name,
                    "url": url,
                    "icon": str(item.get("icon","")).strip() or None,
                })
        return out

    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            out = _sanitize(data)
            if out:
                return out
        except Exception:
            pass

    base = load_tv_channels()

    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(base, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return base
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
        "playing": "Playing",
        "iptv": "IP TV News",
        "toggle_iptv": "Show/Hide TV channels",
        "live": "Live",
        "make_tv_index": "Create TV index",
        "select_locales": "Select 1–3 languages/countries",
        "create_index": "Create",
        "cancel": "Cancel",
        "index_created": "TV index created"
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
        "playing": "Reproduciendo",
        "iptv": "IP TV Noticias",
        "toggle_iptv": "Mostrar/Ocultar canales",
        "live": "En vivo",
        "make_tv_index": "Crear index TV",
        "select_locales": "Elegí 1–3 idiomas/países",
        "create_index": "Crear",
        "cancel": "Cancelar",
        "index_created": "Index TV creado"
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
        "playing": "Lecture en cours",
        "iptv": "IP TV Infos",
        "toggle_iptv": "Afficher/Masquer les chaînes",
        "live": "En direct",
        "make_tv_index": "Créer l’index TV",
        "select_locales": "Choisissez 1–3 langues/pays",
        "create_index": "Créer",
        "cancel": "Annuler",
        "index_created": "Index TV créé"
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
        "playing": "Riproduzione",
        "iptv": "IP TV Notizie",
        "toggle_iptv": "Mostra/Nascondi canali",
        "live": "In diretta",
        "make_tv_index": "Crea indice TV",
        "select_locales": "Scegli 1–3 lingue/paesi",
        "create_index": "Crea",
        "cancel": "Annulla",
        "index_created": "Indice TV creato"
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
        "playing": "Reproduzindo",
        "iptv": "IP TV Notícias",
        "toggle_iptv": "Mostrar/Ocultar canais",
        "live": "Ao vivo",
        "make_tv_index": "Criar índice TV",
        "select_locales": "Escolha 1–3 idiomas/países",
        "create_index": "Criar",
        "cancel": "Cancelar",
        "index_created": "Índice TV criado"
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
        "playing": "Reproduint",
        "iptv": "IP TV Notícies",
        "toggle_iptv": "Mostrar/Ocultar canals",
        "live": "En directe",
        "make_tv_index": "Crear índex TV",
        "select_locales": "Tria 1–3 idiomes/països",
        "create_index": "Crear",
        "cancel": "Cancel·lar",
        "index_created": "Índex TV creat"
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

        self.tv_index = read_tv_index()
        self.active_locale = None
        if self.tv_index and self.tv_index.get("active_locale"):
            self.active_locale = self.tv_index.get("active_locale")
            self.tv_channels = load_tv_channels_for_locale(self.active_locale)
        else:
            self.tv_channels = load_tv_channels()
        
        self.set_default_size(900, 550)
        self.set_position(Gtk.WindowPosition.CENTER)


        self.screenshots_dir = os.path.join(REAL_HOME, ".local", "share", "oply", "tv_screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
   
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

        # Botón TV (panel estilo Global IP TV)
        btn_tv = Gtk.Button()
        btn_tv.add(Gtk.Image.new_from_icon_name("video-display-symbolic", Gtk.IconSize.BUTTON))
        btn_tv.set_tooltip_text(self.text.get("toggle_iptv", "IP TV"))
        btn_tv.connect("clicked", self.on_toggle_tv)
        hb.pack_start(btn_tv)
        
   
        self.menu_button = Gtk.MenuButton()
        self.menu_button.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        self.create_menu()
        hb.pack_end(self.menu_button)
        
  
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Zona superior: sidebar + video
        top_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main_vbox.pack_start(top_hbox, True, True, 0)

        self.tv_window = None
        self.tv_sidebar_widget = None

        # Video area
        self.video_area = Gtk.DrawingArea()
        self.video_area.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
        top_hbox.pack_start(self.video_area, True, True, 0)
        
 
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
        menu.append(self.text.get("iptv", "IP TV"), "win.toggle_tv")
        menu.append(self.text.get("make_tv_index", "Create TV index"), "win.make_tv_index")
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

        tv_action = Gio.SimpleAction.new("toggle_tv", None)
        tv_action.connect("activate", lambda a, p: self.on_toggle_tv(None))
        action_group.add_action(tv_action)

        idx_action = Gio.SimpleAction.new("make_tv_index", None)
        idx_action.connect("activate", lambda a, p: self.on_make_tv_index())
        action_group.add_action(idx_action)
        
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

            try:
                self.player["hwdec"] = "auto-safe"
            except Exception:
                pass
            try:
                self.player["screenshot-directory"] = self.screenshots_dir
            except Exception:
                pass
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

    def play_stream(self, name, url):
        if not self.player:
            return
        try:
            self.player.play(url)
            self.headerbar.props.subtitle = f"{self.text.get('live','Live')}: {name}"


            self.close_tv_window()
        except Exception as e:
            self.show_error_dialog(str(e))

    def tv_panel_set_visible(self, visible: bool):
        """Muestra/Oculta el panel TV SIN dejar espacio vacío.

        En GTK3, Gtk.Revealer puede mantener el ancho requisitado del hijo aun oculto.
        Para evitar la franja vacía, además de reveal_child=False hacemos hide()/show().
        """
        try:
            if not hasattr(self, "sidebar_revealer"):
                return

            if visible:
                self.sidebar_revealer.show()
                self.sidebar_revealer.set_visible(True)
                if hasattr(self, "tv_sidebar_frame") and self.tv_sidebar_frame:
                    self.tv_sidebar_frame.set_size_request(TV_SIDEBAR_WIDTH, -1)
                self.sidebar_revealer.set_size_request(TV_SIDEBAR_WIDTH, -1)
                self.sidebar_revealer.set_reveal_child(True)
            else:
                self.sidebar_revealer.set_reveal_child(False)
                if hasattr(self, "tv_sidebar_frame") and self.tv_sidebar_frame:
                    self.tv_sidebar_frame.set_size_request(1, -1)
                self.sidebar_revealer.set_size_request(1, -1)
                GLib.idle_add(self.sidebar_revealer.hide)

            self.queue_resize()
        except Exception:
            pass

    def _on_tv_window_delete(self, *_args):
        try:
            if self.tv_window:
                self.tv_window.hide()
        except Exception:
            pass
        return True  

    def open_tv_window(self):
        try:
            if getattr(self, "tv_window", None) and self.tv_window.get_visible():
                self.tv_window.present()
                return

            if not getattr(self, "tv_window", None):
                win = Gtk.Window(title=self.text.get("iptv", "IP TV"))
                win.set_transient_for(self)
                win.set_destroy_with_parent(True)
                win.set_default_size(380, 640)
                win.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
                win.connect("delete-event", self._on_tv_window_delete)


                self.tv_sidebar_widget = self.build_tv_sidebar()
                win.add(self.tv_sidebar_widget)

                self.tv_window = win


            try:
                self.refresh_tv_sidebar_ui()
            except Exception:
                pass

            self.tv_window.show_all()
            self.tv_window.present()
        except Exception as e:
            self.show_error_dialog(str(e))

    def close_tv_window(self):
        try:
            if getattr(self, "tv_window", None):
                self.tv_window.hide()
        except Exception:
            pass

    def on_toggle_tv(self, _btn):
        if getattr(self, "tv_window", None) and self.tv_window.get_visible():
            self.close_tv_window()
        else:
            self.open_tv_window()


    def build_tv_sidebar(self):
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.IN)
        self.tv_sidebar_frame = frame
        frame.set_size_request(TV_SIDEBAR_WIDTH, -1)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        outer.set_margin_top(8)
        outer.set_margin_bottom(8)
        outer.set_margin_start(8)
        outer.set_margin_end(8)
        frame.add(outer)

        # Selector de locale (solo aparece si existe tv_index.json)
        self._tv_combo_lock = False
        self.tv_combo_store = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf)
        self.tv_combo = Gtk.ComboBox.new_with_model(self.tv_combo_store)
        self.tv_combo.set_id_column(0)
        self.tv_combo.set_hexpand(True)

        rpb = Gtk.CellRendererPixbuf()
        rpb.set_property("xpad", 4)
        self.tv_combo.pack_start(rpb, False)
        self.tv_combo.add_attribute(rpb, "pixbuf", 2)

        rtx = Gtk.CellRendererText()
        rtx.set_property("ellipsize", Pango.EllipsizeMode.END)
        self.tv_combo.pack_start(rtx, True)
        self.tv_combo.add_attribute(rtx, "text", 1)

        self.tv_combo.connect("changed", self.on_tv_locale_changed)
        outer.pack_start(self.tv_combo, False, False, 0)

        # Scroll + grilla de botones
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        outer.pack_start(sc, True, True, 0)

        self.tv_flow = Gtk.FlowBox()
        self.tv_flow.set_valign(Gtk.Align.START)
        self.tv_flow.set_max_children_per_line(2)
        self.tv_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.tv_flow.set_column_spacing(6)
        self.tv_flow.set_row_spacing(6)
        sc.add(self.tv_flow)

        # Pintar UI según index (si existe)
        self.refresh_tv_sidebar_ui()

        return frame

    def refresh_tv_sidebar_ui(self):
        self.tv_index = read_tv_index()
        if self.tv_index and self.tv_index.get("items"):
            self.tv_combo.show()
            self.tv_combo.set_sensitive(True)
            self._tv_combo_lock = True
            try:
                self.tv_combo_store.clear()
                for it in self.tv_index.get("items", []):
                    code = it.get("locale") or ""
                    label = it.get("label") or code.upper()
                    if code:
                        self.tv_combo_store.append([code, label, self.load_flag_pixbuf(code)])

                active = self.tv_index.get("active_locale")
                if not active and self.tv_index.get("items"):
                    active = self.tv_index["items"][0].get("locale")
                if active:
                    self.tv_combo.set_active_id(active)
                    self.active_locale = active
                    self.tv_channels = load_tv_channels_for_locale(active)
                else:
                    self.tv_channels = load_tv_channels()
            finally:
                self._tv_combo_lock = False
        else:
            self.tv_combo.hide()
            self.active_locale = None
            self.tv_channels = load_tv_channels()

        self.refresh_tv_flow()

    def refresh_tv_flow(self):
        try:
            for child in list(self.tv_flow.get_children()):
                self.tv_flow.remove(child)
        except Exception:
            pass

        for ch in self.tv_channels:
            try:
                name = ch.get("name", "TV")
                url = ch.get("url")
                if not url:
                    continue

                btn = Gtk.Button()
                btn.set_relief(Gtk.ReliefStyle.NONE)
                btn.set_tooltip_text(name)

                vb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                vb.set_margin_top(2)
                vb.set_margin_bottom(2)
                vb.set_margin_start(2)
                vb.set_margin_end(2)

                img = self.load_tv_icon(ch.get("icon"))
                if img:
                    vb.pack_start(img, False, False, 0)

                lbl = Gtk.Label(label=name)
                lbl.set_max_width_chars(14)
                lbl.set_line_wrap(True)
                lbl.set_justify(Gtk.Justification.CENTER)
                vb.pack_start(lbl, False, False, 0)

                btn.add(vb)
                btn.connect("clicked", lambda _b, _ch=ch: self.play_stream(_ch.get("name","TV"), _ch["url"]))

                self.tv_flow.add(btn)
            except Exception:
                pass

        self.tv_flow.show_all()

    def on_tv_locale_changed(self, combo):
        if getattr(self, "_tv_combo_lock", False):
            return
        if not combo:
            return
        code = combo.get_active_id()
        if not code:
            return

        self.active_locale = code
        write_tv_index_active(code)
        self.tv_channels = load_tv_channels_for_locale(code)
        self.refresh_tv_flow()

    def load_tv_icon(self, filename):
        """Carga el icono del canal. Si falta, usa tv.png como fallback."""
        candidate = filename or "tv.png"
        p = os.path.join(TV_ICONS_DIR, candidate)
        if not os.path.exists(p):
            p = os.path.join(TV_ICONS_DIR, "tv.png")
            if not os.path.exists(p):
                return None
        try:
            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(p, 96, 96, True)
            return Gtk.Image.new_from_pixbuf(pb)
        except Exception:
            return None

    def load_flag_pixbuf(self, locale_code: str):
        """Carga una banderita (si existe) para el locale."""
        if not locale_code:
            return None
        p = os.path.join(TV_FLAGS_DIR, f"{locale_code}.png")
        if not os.path.exists(p):
            return None
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(p, 22, 14, True)
        except Exception:
            return None

    def on_make_tv_index(self):
        locales = self.get_available_locales()

        dlg = Gtk.Dialog(
            title=self.text.get("make_tv_index", "Create TV index"),
            parent=self,
            flags=0
        )
        dlg.add_buttons(
            self.text.get("cancel", "Cancel"), Gtk.ResponseType.CANCEL,
            self.text.get("create_index", "Create"), Gtk.ResponseType.OK
        )
        dlg.set_default_size(600, 520)

        box = dlg.get_content_area()
        info = Gtk.Label(label=self.text.get("select_locales", "Select 1–3 languages/countries"))
        info.set_halign(Gtk.Align.START)
        info.set_margin_bottom(8)
        box.add(info)

        store = Gtk.ListStore(bool, GdkPixbuf.Pixbuf, str, str)
        for item in locales:
            code = item.get("code")
            label = item.get("label")
            store.append([False, self.load_flag_pixbuf(code), code, label])

        tv = Gtk.TreeView(model=store)
        tv.set_headers_visible(True)

        # Checkbox
        rchk = Gtk.CellRendererToggle()
        rchk.set_activatable(True)

        def _count_checked():
            return sum(1 for row in store if row[0])

        def _on_toggled(renderer, path):
            it = store.get_iter(path)
            current = store.get_value(it, 0)

            if (not current) and _count_checked() >= 3:
                self.show_error_dialog("Podés seleccionar como máximo 3.")
                return

            store.set_value(it, 0, not current)

        rchk.connect("toggled", _on_toggled)
        col_chk = Gtk.TreeViewColumn("✓", rchk, active=0)
        col_chk.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_chk.set_fixed_width(40)
        tv.append_column(col_chk)

        # Bandera
        r0 = Gtk.CellRendererPixbuf()
        col0 = Gtk.TreeViewColumn("", r0, pixbuf=1)
        col0.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col0.set_fixed_width(28)
        tv.append_column(col0)

        # Código
        r1 = Gtk.CellRendererText()
        col1 = Gtk.TreeViewColumn("Code", r1, text=2)
        col1.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col1.set_fixed_width(90)
        tv.append_column(col1)

        # Nombre/Locale
        r2 = Gtk.CellRendererText()
        r2.set_property("wrap-mode", Pango.WrapMode.WORD_CHAR)
        r2.set_property("wrap-width", 360)
        col2 = Gtk.TreeViewColumn("Locale", r2, text=3)
        col2.set_expand(True)
        col2.set_resizable(True)
        tv.append_column(col2)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        try:
            sc.set_min_content_height(360)
        except Exception:
            pass
        try:
            sc.set_vexpand(True)
            tv.set_vexpand(True)
        except Exception:
            pass
        sc.add(tv)
        box.add(sc)

        dlg.show_all()
        resp = dlg.run()
        if resp != Gtk.ResponseType.OK:
            dlg.destroy()
            return

        chosen = [row[2] for row in store if row[0]]
        dlg.destroy()

        if not (1 <= len(chosen) <= 3):
            self.show_error_dialog("Elegí 1, 2 o 3 locales.")
            return

        ok, out = self.run_tv_indexer(chosen)
        if not ok:
            self.show_error_dialog(out or "Error creando el index.")
            return

        self.show_info_dialog(self.text.get("index_created", "TV index created"), out)

        try:
            self.refresh_tv_sidebar_ui()
        except Exception:
            pass


    def get_available_locales(self):
        try:
            if os.path.exists(TV_INDEXER):
                import subprocess
                res = subprocess.run([sys.executable, TV_INDEXER, "--list-locales"],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    data = json.loads(res.stdout.strip())
                    if isinstance(data, list) and data:
                        prefer = [
                            "ar_SA",
                            "ca_ES",
                            "en_US","en_GB",
                            "es_ES","es_AR","es_MX","es_CL","es_VE","es_CO","es_BO","es_PY","es_UY",
                            "es_SV",
                            "fr_FR",
                            "it_IT",
                            "pt_PT","pt_BR",
                            "hu_HU",
                            "ru_RU",
                            "ja_JP",
                            "zh_CN","zh_TW",
                        ]
                        ordered = []
                        seen = set()
                        for p in prefer:
                            for it in data:
                                if it.get("code") == p and p not in seen:
                                    ordered.append(it); seen.add(p)
                        for it in data:
                            c = it.get("code")
                            if c and c not in seen:
                                ordered.append(it); seen.add(c)
                        return ordered
        except Exception:
            pass

        # Fallback mínimo
        return [
            {"code":"ar_SA","label":"العربية (السعودية)"},
            {"code":"ca_ES","label":"Català (ES)"},
            {"code":"en_US","label":"English (United States)"},
            {"code":"en_GB","label":"English (United Kingdom)"},
            {"code":"es_ES","label":"Español (España)"},
            {"code":"es_AR","label":"Español (Argentina)"},
            {"code":"es_MX","label":"Español (México)"},
            {"code":"es_CL","label":"Español (Chile)"},
            {"code":"es_VE","label":"Español (Venezuela)"},
            {"code":"es_CO","label":"Español (Colombia)"},
            {"code":"es_BO","label":"Español (Bolivia)"},
            {"code":"es_PY","label":"Español (Paraguay)"},
            {"code":"es_UY","label":"Español (Uruguay)"},
            {"code":"es_SV","label":"Español (El Salvador)"},
            {"code":"fr_FR","label":"Français (France)"},
            {"code":"it_IT","label":"Italiano (Italia)"},
            {"code":"pt_PT","label":"Português (Portugal)"},
            {"code":"pt_BR","label":"Português (Brasil)"},
            {"code":"hu_HU","label":"Magyar (Magyarország)"},
            {"code":"ru_RU","label":"Русский (Россия)"},
            {"code":"ja_JP","label":"日本語 (日本)"},
            {"code":"zh_CN","label":"中文 (简体)"},
            {"code":"zh_TW","label":"中文 (繁體)"},
        ]

    def run_tv_indexer(self, locales_list):
        try:
            import subprocess
            cmd = [sys.executable, TV_INDEXER, "--locales", ",".join(locales_list)]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                return True, (res.stdout.strip() or "OK")
            return False, (res.stderr.strip() or res.stdout.strip() or "Error")
        except Exception as e:
            return False, str(e)

    def show_info_dialog(self, title, message):
        dlg = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title,
        )
        dlg.format_secondary_text(message)
        dlg.run()
        dlg.destroy()
    def show_error_dialog(self, message):
        dlg = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Oply Video",
        )
        dlg.format_secondary_text(message)
        dlg.run()
        dlg.destroy()
    
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
