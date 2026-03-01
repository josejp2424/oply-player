#!/usr/bin/env python3
# Oply Radio - GNOME-style Internet Radio Player (GTK3 + mpv)
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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, AyatanaAppIndicator3 as AppIndicator3
    APPINDICATOR_AVAILABLE = True
except (ValueError, ImportError):
    from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
    APPINDICATOR_AVAILABLE = False

import os
import sys
import json
import time
import socket
import subprocess
import pwd
from urllib import request, parse
from pathlib import Path


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
LANG_FILE = os.path.join(CONFIG_DIR, "language.json")
RADIO_DIR = os.path.join(CONFIG_DIR, "radio")
FAVORITES_FILE = os.path.join(RADIO_DIR, "favorites.json")
ICON_APP = "/usr/local/Oply/icons/radio.svg"


# Locales / Countries

RADIO_LOCALES = [
    ("es_AR", "Argentina", "AR"),
    ("es_ES", "España", "ES"),
    ("es_MX", "México", "MX"),
    ("es_CL", "Chile", "CL"),
    ("es_VE", "Venezuela", "VE"),
    ("es_CO", "Colombia", "CO"),
    ("es_BO", "Bolivia", "BO"),
    ("es_PY", "Paraguay", "PY"),
    ("es_UY", "Uruguay", "UY"),
    ("es_SV", "El Salvador", "SV"),
    ("en_US", "United States", "US"),
    ("en_GB", "United Kingdom", "GB"),
]


# Translations

TXT = {
    "en": {
        "title": "Oply Radio",
        "subtitle": "Select a station",
        "country": "Country",
        "search": "Search…",
        "refresh": "Refresh list",
        "add": "Add station",
        "stop": "Stop",
        "volume": "Volume",
        "connecting": "Connecting…",
        "connecting_to": "Connecting to:",
        "loading": "Loading stations…",
        "no_stations": "No stations yet. Press Refresh.",
        "err_fetch": "Could not fetch stations (offline?). Using cache.",
        "err_open": "Could not open Oply Radio.",
        "name": "Name",
        "url": "URL",
        "save": "Save",
        "cancel": "Cancel",
        "favorites": "Favorites",
        "add_fav": "Add to favorites",
        "remove_fav": "Remove from favorites",
        "no_fav": "No favorites yet",
        "fav_open": "Open favorites file",
        "fav_added": "Added to favorites",
        "fav_removed": "Removed from favorites",
        "restore": "Show Window",
        "exit": "Exit",
        "tray_country": "Country",
        "close_dialog_title": "Close Oply Radio?",
        "close_dialog_message": "What do you want to do?",
        "minimize_to_tray": "Minimize to Tray",
        "quit_app": "Quit Application",
        "tray_favorites": "Favorites",
    },
    "es": {
        "title": "Oply Radio",
        "subtitle": "Elegí una estación",
        "country": "País",
        "search": "Buscar…",
        "refresh": "Actualizar lista",
        "add": "Agregar estación",
        "stop": "Detener",
        "volume": "Volumen",
        "connecting": "Conectando…",
        "connecting_to": "Conectando a:",
        "loading": "Cargando estaciones…",
        "no_stations": "Sin estaciones. Tocá Actualizar.",
        "err_fetch": "No pude descargar estaciones (¿sin internet?). Uso caché.",
        "err_open": "No se pudo abrir Oply Radio.",
        "name": "Nombre",
        "url": "URL",
        "save": "Guardar",
        "cancel": "Cancelar",
        "favorites": "Favoritos",
        "add_fav": "Agregar a favoritos",
        "remove_fav": "Quitar de favoritos",
        "no_fav": "Sin favoritos todavía",
        "fav_open": "Abrir archivo de favoritos",
        "fav_added": "Agregado a favoritos",
        "fav_removed": "Quitado de favoritos",
        "restore": "Mostrar Ventana",
        "exit": "Salir",
        "tray_country": "País",
        "close_dialog_title": "¿Cerrar Oply Radio?",
        "close_dialog_message": "¿Qué deseas hacer?",
        "minimize_to_tray": "Minimizar a Bandeja",
        "quit_app": "Salir de la Aplicación",
        "tray_favorites": "Favoritos",
    },
    "fr": {
        "title": "Oply Radio",
        "subtitle": "Choisissez une station",
        "country": "Pays",
        "search": "Rechercher…",
        "refresh": "Actualiser la liste",
        "add": "Ajouter une station",
        "stop": "Arrêter",
        "volume": "Volume",
        "connecting": "Connexion…",
        "connecting_to": "Connexion à :",
        "loading": "Chargement des stations…",
        "no_stations": "Aucune station. Appuyez sur Actualiser.",
        "err_fetch": "Impossible de récupérer les stations. Cache utilisé.",
        "err_open": "Impossible d'ouvrir Oply Radio.",
        "name": "Nom",
        "url": "URL",
        "save": "Enregistrer",
        "cancel": "Annuler",
        "favorites": "Favoris",
        "add_fav": "Ajouter aux favoris",
        "remove_fav": "Retirer des favoris",
        "no_fav": "Aucun favori",
        "fav_open": "Ouvrir le fichier des favoris",
        "fav_added": "Ajouté aux favoris",
        "fav_removed": "Retiré des favoris",
        "restore": "Afficher la Fenêtre",
        "exit": "Quitter",
        "tray_country": "Pays",
        "close_dialog_title": "Fermer Oply Radio ?",
        "close_dialog_message": "Que voulez-vous faire ?",
        "minimize_to_tray": "Réduire dans la Barre",
        "quit_app": "Quitter l'Application",
        "tray_favorites": "Favoris",
    },
    "it": {
        "title": "Oply Radio",
        "subtitle": "Seleziona una stazione",
        "country": "Paese",
        "search": "Cerca…",
        "refresh": "Aggiorna elenco",
        "add": "Aggiungi stazione",
        "stop": "Stop",
        "volume": "Volume",
        "connecting": "Connessione…",
        "connecting_to": "Connessione a:",
        "loading": "Caricamento stazioni…",
        "no_stations": "Nessuna stazione. Premi Aggiorna.",
        "err_fetch": "Impossibile recuperare le stazioni. Uso cache.",
        "err_open": "Impossibile aprire Oply Radio.",
        "name": "Nome",
        "url": "URL",
        "save": "Salva",
        "cancel": "Annulla",
        "favorites": "Preferiti",
        "add_fav": "Aggiungi ai preferiti",
        "remove_fav": "Rimuovi dai preferiti",
        "no_fav": "Nessun preferito",
        "fav_open": "Apri file preferiti",
        "fav_added": "Aggiunto ai preferiti",
        "fav_removed": "Rimosso dai preferiti",
        "restore": "Mostra Finestra",
        "exit": "Esci",
        "tray_country": "Paese",
        "close_dialog_title": "Chiudere Oply Radio?",
        "close_dialog_message": "Cosa vuoi fare?",
        "minimize_to_tray": "Riduci a Icona",
        "quit_app": "Chiudi Applicazione",
        "tray_favorites": "Preferiti",
    },
    "pt": {
        "title": "Oply Radio",
        "subtitle": "Escolha uma estação",
        "country": "País",
        "search": "Buscar…",
        "refresh": "Atualizar lista",
        "add": "Adicionar estação",
        "stop": "Parar",
        "volume": "Volume",
        "connecting": "Conectando…",
        "connecting_to": "Conectando a:",
        "loading": "Carregando estações…",
        "no_stations": "Sem estações. Clique em Atualizar.",
        "err_fetch": "Não foi possível buscar estações. Usando cache.",
        "err_open": "Não foi possível abrir Oply Radio.",
        "name": "Nome",
        "url": "URL",
        "save": "Salvar",
        "cancel": "Cancelar",
        "favorites": "Favoritos",
        "add_fav": "Adicionar aos favoritos",
        "remove_fav": "Remover dos favoritos",
        "no_fav": "Sem favoritos",
        "fav_open": "Abrir arquivo de favoritos",
        "fav_added": "Adicionado aos favoritos",
        "fav_removed": "Removido dos favoritos",
        "restore": "Mostrar Janela",
        "exit": "Sair",
        "tray_country": "País",
        "close_dialog_title": "Fechar Oply Radio?",
        "close_dialog_message": "O que você deseja fazer?",
        "minimize_to_tray": "Minimizar para Bandeja",
        "quit_app": "Sair da Aplicação",
        "tray_favorites": "Favoritos",
    },
    "ru": {
        "title": "Oply Radio",
        "subtitle": "Выберите станцию",
        "country": "Страна",
        "search": "Поиск…",
        "refresh": "Обновить список",
        "add": "Добавить станцию",
        "stop": "Стоп",
        "volume": "Громкость",
        "connecting": "Подключение…",
        "connecting_to": "Подключение к:",
        "loading": "Загрузка станций…",
        "no_stations": "Станций нет. Нажмите Обновить.",
        "err_fetch": "Не удалось получить станции. Использую кэш.",
        "err_open": "Не удалось открыть Oply Radio.",
        "name": "Название",
        "url": "URL",
        "save": "Сохранить",
        "cancel": "Отмена",
        "favorites": "Избранное",
        "add_fav": "Добавить в избранное",
        "remove_fav": "Удалить из избранного",
        "no_fav": "Нет избранного",
        "fav_open": "Открыть файл избранного",
        "fav_added": "Добавлено в избранное",
        "fav_removed": "Удалено из избранного",
        "restore": "Показать Окно",
        "exit": "Выход",
        "tray_country": "Страна",
        "close_dialog_title": "Закрыть Oply Radio?",
        "close_dialog_message": "Что вы хотите сделать?",
        "minimize_to_tray": "Свернуть в Трей",
        "quit_app": "Выйти из Приложения",
        "tray_favorites": "Избранное",
    },
    "ja": {
        "title": "Oply Radio",
        "subtitle": "局を選択してください",
        "country": "国",
        "search": "検索…",
        "refresh": "一覧を更新",
        "add": "局を追加",
        "stop": "停止",
        "volume": "音量",
        "connecting": "接続中…",
        "connecting_to": "接続先:",
        "loading": "局を読み込み中…",
        "no_stations": "局がありません。更新を押してください。",
        "err_fetch": "局を取得できません。キャッシュを使用します。",
        "err_open": "Oply Radio を開けませんでした。",
        "name": "名前",
        "url": "URL",
        "save": "保存",
        "cancel": "キャンセル",
        "favorites": "お気に入り",
        "add_fav": "お気に入りに追加",
        "remove_fav": "お気に入りから削除",
        "no_fav": "お気に入りなし",
        "fav_open": "お気に入りファイルを開く",
        "fav_added": "お気に入りに追加しました",
        "fav_removed": "お気に入りから削除しました",
        "restore": "ウィンドウを表示",
        "exit": "終了",
        "tray_country": "国",
        "close_dialog_title": "Oply Radio を閉じますか？",
        "close_dialog_message": "何をしますか？",
        "minimize_to_tray": "トレイに最小化",
        "quit_app": "アプリケーションを終了",
        "tray_favorites": "お気に入り",
    },
    "zh": {
        "title": "Oply Radio",
        "subtitle": "请选择电台",
        "country": "国家",
        "search": "搜索…",
        "refresh": "刷新列表",
        "add": "添加电台",
        "stop": "停止",
        "volume": "音量",
        "connecting": "正在连接…",
        "connecting_to": "正在连接到：",
        "loading": "正在加载电台…",
        "no_stations": "没有电台。请点击刷新。",
        "err_fetch": "无法获取电台。使用缓存。",
        "err_open": "无法打开 Oply Radio。",
        "name": "名称",
        "url": "URL",
        "save": "保存",
        "cancel": "取消",
        "favorites": "收藏",
        "add_fav": "加入收藏",
        "remove_fav": "移出收藏",
        "no_fav": "暂无收藏",
        "fav_open": "打开收藏文件",
        "fav_added": "已加入收藏",
        "fav_removed": "已移出收藏",
        "restore": "显示窗口",
        "exit": "退出",
        "tray_country": "国家",
        "close_dialog_title": "关闭 Oply Radio？",
        "close_dialog_message": "您想做什么？",
        "minimize_to_tray": "最小化到托盘",
        "quit_app": "退出应用程序",
        "tray_favorites": "收藏",
    },
    "ar": {
        "title": "Oply Radio",
        "subtitle": "اختر محطة",
        "country": "البلد",
        "search": "بحث…",
        "refresh": "تحديث القائمة",
        "add": "إضافة محطة",
        "stop": "إيقاف",
        "volume": "الصوت",
        "connecting": "جارٍ الاتصال…",
        "connecting_to": "جارٍ الاتصال بـ:",
        "loading": "جارٍ تحميل المحطات…",
        "no_stations": "لا توجد محطات. اضغط تحديث.",
        "err_fetch": "تعذر جلب المحطات. استخدام التخزين المؤقت.",
        "err_open": "تعذر فتح Oply Radio.",
        "name": "الاسم",
        "url": "الرابط",
        "save": "حفظ",
        "cancel": "إلغاء",
        "favorites": "المفضلة",
        "add_fav": "إضافة إلى المفضلة",
        "remove_fav": "إزالة من المفضلة",
        "no_fav": "لا توجد مفضلة بعد",
        "fav_open": "فتح ملف المفضلة",
        "fav_added": "تمت الإضافة إلى المفضلة",
        "fav_removed": "تمت الإزالة من المفضلة",
        "restore": "إظهار النافذة",
        "exit": "خروج",
        "tray_country": "البلد",
        "close_dialog_title": "إغلاق Oply Radio؟",
        "close_dialog_message": "ماذا تريد أن تفعل؟",
        "minimize_to_tray": "تصغير إلى الدرج",
        "quit_app": "إنهاء التطبيق",
        "tray_favorites": "المفضلة",
    },
    "ca": {
        "title": "Oply Radio",
        "subtitle": "Tria una emissora",
        "country": "País",
        "search": "Cerca…",
        "refresh": "Actualitza la llista",
        "add": "Afegeix emissora",
        "stop": "Atura",
        "volume": "Volum",
        "connecting": "Connectant…",
        "connecting_to": "Connectant a:",
        "loading": "Carregant emissores…",
        "no_stations": "Sense emissores. Prem Actualitza.",
        "err_fetch": "No puc obtenir emissores. Ús de memòria cau.",
        "err_open": "No s'ha pogut obrir Oply Radio.",
        "name": "Nom",
        "url": "URL",
        "save": "Desa",
        "cancel": "Cancel·la",
        "favorites": "Preferits",
        "add_fav": "Afegeix a preferits",
        "remove_fav": "Treu de preferits",
        "no_fav": "Sense preferits",
        "fav_open": "Obre el fitxer de preferits",
        "fav_added": "Afegit a preferits",
        "fav_removed": "Eliminat de preferits",

    }
}

def load_lang_code():
    try:
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                lang = (cfg.get("language") or "").strip()
                if lang:
                    return lang
    except Exception:
        pass

    lang_env = os.environ.get("LANG", "")
    if lang_env and lang_env not in ("C", "POSIX"):
        return lang_env.split("_")[0].lower()
    return "en"

def tr():
    code = load_lang_code()
    return TXT.get(code, TXT["en"])


# Radio Browser helpers

def get_radio_browser_base():
    """
    Radio-Browser tiene varios servidores.
    Probamos 'all' para lista de servidores y elegimos el primero.
    """
    try:
        with request.urlopen("https://all.api.radio-browser.info/json/servers", timeout=5) as r:
            servers = json.loads(r.read().decode("utf-8"))
            if isinstance(servers, list) and servers:
                
                host = servers[0].get("name") or servers[0].get("ip") or servers[0].get("host")
                
                if host and "." in host:
                    return f"https://{host}"
    except Exception:
        pass
    return "https://de1.api.radio-browser.info"

def fetch_stations_by_country(cc, limit=200):
    base = get_radio_browser_base()
    url = f"{base}/json/stations/bycountrycodeexact/{parse.quote(cc)}?hidebroken=true&order=clickcount&reverse=true&limit={int(limit)}"
    with request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read().decode("utf-8"))
    stations = []
    if isinstance(data, list):
        for it in data:
            name = (it.get("name") or "").strip()
            url_res = (it.get("url_resolved") or it.get("url") or "").strip()
            if not name or not url_res:
                continue
            stations.append({
                "name": name,
                "url": url_res,
                "favicon": (it.get("favicon") or "").strip()
            })
    return stations


# Oply Radio App  # favorites # icon # mpv

class OplyRadio(Gtk.Window):
    def __init__(self):
        super().__init__(title="Oply Radio")
        self.TEXT = tr()

       
        self.favorites = self.load_favorites()

        os.makedirs(RADIO_DIR, exist_ok=True)

        self.set_default_size(760, 520)
        self.set_position(Gtk.WindowPosition.CENTER)

        
        try:
            if os.path.exists(ICON_APP):
                self.set_icon_from_file(ICON_APP)
        except Exception:
            pass

        
        self.mpv_socket = os.path.join(RADIO_DIR, f"mpv_radio_{os.getpid()}.sock")
        try:
            if os.path.exists(self.mpv_socket):
                os.remove(self.mpv_socket)
        except Exception:
            pass
        self._start_mpv()

        # state
        self.current_station = None
        self._connecting_started = 0.0
        self._connect_timeout_ms = 15000

        # headerbar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = self.TEXT["title"]
        hb.props.subtitle = self.TEXT["subtitle"]
        self.set_titlebar(hb)
        self.hb = hb

        # refresh button
        btn_refresh = Gtk.Button()
        btn_refresh.add(Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON))
        btn_refresh.set_tooltip_text(self.TEXT["refresh"])
        btn_refresh.connect("clicked", self.on_refresh)
        hb.pack_start(btn_refresh)

        # add station button
        btn_add = Gtk.Button()
        btn_add.add(Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON))
        btn_add.set_tooltip_text(self.TEXT["add"])
        btn_add.connect("clicked", self.on_add_station)
        hb.pack_start(btn_add)


        # favorites (heart) - dropdown list
        self.fav_btn = Gtk.MenuButton()
        self.fav_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.fav_btn.add(Gtk.Image.new_from_icon_name("emblem-favorite-symbolic", Gtk.IconSize.BUTTON))
        self.fav_btn.set_tooltip_text(self.TEXT["favorites"])

        self.fav_popover = Gtk.Popover.new(self.fav_btn)
        self.fav_popover.set_border_width(6)

        fav_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.fav_listbox = Gtk.ListBox()
        self.fav_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.fav_listbox.connect("row-activated", self._on_fav_row_activated)

        fav_sc = Gtk.ScrolledWindow()
        fav_sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        fav_sc.set_size_request(420, 320)
        fav_sc.add(self.fav_listbox)
        fav_box.pack_start(fav_sc, True, True, 0)

        btn_open_fav = Gtk.Button(label=self.TEXT["fav_open"])
        btn_open_fav.connect("clicked", self._open_favorites_file)
        fav_box.pack_start(btn_open_fav, False, False, 0)

        self.fav_popover.add(fav_box)
        self.fav_btn.set_popover(self.fav_popover)
        self._rebuild_favorites_popover()
        hb.pack_end(self.fav_btn)
        # stop button
        btn_stop = Gtk.Button()
        btn_stop.add(Gtk.Image.new_from_icon_name("media-playback-stop-symbolic", Gtk.IconSize.BUTTON))
        btn_stop.set_tooltip_text(self.TEXT["stop"])
        btn_stop.connect("clicked", self.on_stop)
        hb.pack_end(btn_stop)

        # UI
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        root.set_margin_top(10)
        root.set_margin_bottom(10)
        root.set_margin_start(10)
        root.set_margin_end(10)
        self.add(root)

        # top controls (country + search + volume)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        root.pack_start(top, False, False, 0)

        lbl_country = Gtk.Label(label=self.TEXT["country"] + ":")
        lbl_country.set_halign(Gtk.Align.START)
        top.pack_start(lbl_country, False, False, 0)

        self.cmb = Gtk.ComboBoxText()
        self.cmb.append("FAV", f"★ {self.TEXT['favorites']}")
        for code, label, cc in RADIO_LOCALES:
            self.cmb.append(code, f"{code} — {label}")
        self.cmb.set_active(0 if self.favorites else 1)
        self.cmb.connect("changed", self.on_country_changed)
        top.pack_start(self.cmb, False, False, 0)

        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text(self.TEXT["search"])
        self.search.connect("search-changed", self.on_search_changed)
        top.pack_start(self.search, True, True, 0)

        # volume
        vol_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        top.pack_end(vol_box, False, False, 0)

        lbl_vol = Gtk.Label(label=self.TEXT["volume"])
        vol_box.pack_start(lbl_vol, False, False, 0)

        self.vol = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.vol.set_draw_value(False)
        self.vol.set_value(50)
        self.vol.set_size_request(140, -1)
        self.vol.connect("value-changed", self.on_volume_changed)
        vol_box.pack_start(self.vol, False, False, 0)

        # list + right area
        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        root.pack_start(body, True, True, 0)

        # station list
        self.store = Gtk.ListStore(str, str)  
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self._filter_func)

        self.tree = Gtk.TreeView(model=self.filter)
        self.tree.set_headers_visible(False)
        renderer = Gtk.CellRendererText()
        renderer.set_property("ellipsize", 3) 
        col = Gtk.TreeViewColumn("Station", renderer, text=0)
        self.tree.append_column(col)
        self.tree.connect("row-activated", self.on_station_activated)
        self.tree.connect("button-press-event", self.on_tree_button_press)

        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sc.set_size_request(320, -1)
        sc.add(self.tree)
        body.pack_start(sc, False, False, 0)

        # right panel with overlay (connecting)
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        body.pack_start(right, True, True, 0)

        self.now = Gtk.Label()
        self.now.set_markup("<b>—</b>")
        self.now.set_xalign(0)
        right.pack_start(self.now, False, False, 0)

        # overlay area
        self.overlay = Gtk.Overlay()
        self.overlay.set_hexpand(True)
        self.overlay.set_vexpand(True)
        right.pack_start(self.overlay, True, True, 0)

        # base content in overlay
        base = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        base.set_halign(Gtk.Align.CENTER)
        base.set_valign(Gtk.Align.CENTER)

        self.hint = Gtk.Label(label=self.TEXT["no_stations"])
        self.hint.set_justify(Gtk.Justification.CENTER)
        base.pack_start(self.hint, False, False, 0)

        self.overlay.add(base)

        # overlay connecting widget
        self.conn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.conn_box.set_halign(Gtk.Align.CENTER)
        self.conn_box.set_valign(Gtk.Align.CENTER)
        self.conn_box.set_margin_top(10)
        self.conn_box.set_margin_bottom(10)
        self.conn_box.set_margin_start(10)
        self.conn_box.set_margin_end(10)

        self.spinner = Gtk.Spinner()
        self.conn_label = Gtk.Label(label=self.TEXT["connecting"])
        self.conn_label.set_justify(Gtk.Justification.CENTER)

        self.conn_box.pack_start(self.spinner, False, False, 0)
        self.conn_box.pack_start(self.conn_label, False, False, 0)

        self.overlay.add_overlay(self.conn_box)
        self.conn_box.hide()

        # bottom-right app icon
        try:
            if os.path.exists(ICON_APP):
                self.brand_icon = Gtk.Image.new_from_file(ICON_APP)
                self.brand_icon.set_halign(Gtk.Align.END)
                self.brand_icon.set_valign(Gtk.Align.END)
                self.brand_icon.set_margin_end(10)
                self.brand_icon.set_margin_bottom(10)
                self.brand_icon.set_opacity(0.9)
                self.overlay.add_overlay(self.brand_icon)
        except Exception:
            self.brand_icon = None

        # load cache first
        self.load_cached()

        # systray
        self.indicator = None
        self.setup_systray()

        # close behavior
        self.connect("delete-event", self.on_window_delete)
        self.connect("destroy", self.on_destroy)
        self.show_all()

    # ---------- mpv ----------
    def _start_mpv(self):
        self.mpv = subprocess.Popen(
            [
                "mpv",
                "--idle=yes",
                "--no-video",
                f"--input-ipc-server={self.mpv_socket}",
                "--no-terminal",
                "--audio-display=no",
                "--volume=50",
                "--keep-open=no",
                "--pause=no"
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(0.4)

    def _mpv_send(self, command, request_id=1, want_reply=False):
        if not os.path.exists(self.mpv_socket):
            return None
        payload = {"command": command, "request_id": int(request_id)}
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(1.5)
                s.connect(self.mpv_socket)
                s.sendall((json.dumps(payload) + "\n").encode("utf-8"))
                if not want_reply:
                    return None
                data = b""
                while not data.endswith(b"\n"):
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                if not data:
                    return None
                resp = json.loads(data.decode("utf-8", errors="ignore").strip())
                if resp.get("error") == "success":
                    return resp.get("data")
                return None
        except Exception:
            return None

    def _mpv_get(self, prop):
        return self._mpv_send(["get_property", prop], request_id=7, want_reply=True)

    def _mpv_set(self, prop, value):
        self._mpv_send(["set_property", prop, value], request_id=8, want_reply=False)

    # ---------- cache ----------
    def _selected_locale(self):
        """Devuelve (code,label,cc) o None si está en Favoritos."""
        try:
            active_id = self.cmb.get_active_id()
        except Exception:
            active_id = None

        if not active_id or active_id == "FAV":
            return None

        for code, label, cc in RADIO_LOCALES:
            if code == active_id:
                return (code, label, cc)

        return RADIO_LOCALES[0]


    def _cache_file(self, locale_code):
        return os.path.join(RADIO_DIR, f"stations_{locale_code}.json")

    def load_cached(self):
        self.store.clear()

        active_id = None
        try:
            active_id = self.cmb.get_active_id()
        except Exception:
            active_id = None

        if active_id == "FAV":
            self._load_favorites_into_store()
            self._update_hint()
            return

        sel = self._selected_locale()
        if not sel:
            self._update_hint()
            return

        code, label, cc = sel
        p = self._cache_file(code)

        stations = []
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    stations = json.load(f)
        except Exception:
            stations = []

        if isinstance(stations, list):
            for it in stations:
                name = (it.get("name") or "").strip()
                url = (it.get("url") or "").strip()
                if name and url:
                    self.store.append([name, url])

        self._update_hint()

    def save_cached(self, locale_code, stations):

        p = self._cache_file(locale_code)
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(stations, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

 
    def _filter_func(self, model, it, data=None):
        q = (self.search.get_text() or "").strip().lower()
        if not q:
            return True
        name = (model[it][0] or "").lower()
        return q in name

    def on_search_changed(self, entry):
        self.filter.refilter()

    def _update_hint(self):

        if len(self.store) == 0:
            self.hint.set_text(self.TEXT["no_stations"])
            self.hint.show()
        else:
            self.hint.hide()

    
    # ---------- systray (minimize to tray) ----------
    def setup_systray(self):
        """Configurar systray con AyatanaAppIndicator3 (si está disponible)."""
        if not APPINDICATOR_AVAILABLE:
            self.indicator = None
            return

        try:
            icon = ICON_APP if os.path.exists(ICON_APP) else "audio-x-generic"
            self.indicator = AppIndicator3.Indicator.new(
                "oply-radio",
                icon,
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_title(self.TEXT.get("title", "Oply Radio"))
            self.create_systray_menu()
        except Exception:
            self.indicator = None

    def _tray_item(self, label, icon_name=None, icon_path=None):
        """Gtk.MenuItem con icono (mejor que MenuItem pelado)."""
        item = Gtk.MenuItem()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        img = None
        if icon_path and os.path.exists(icon_path):
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file(icon_path)
                pb = pb.scale_simple(16, 16, GdkPixbuf.InterpType.BILINEAR)
                img = Gtk.Image.new_from_pixbuf(pb)
            except Exception:
                img = None

        if img is None and icon_name:
            img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)

        if img is not None:
            box.pack_start(img, False, False, 0)

        lab = Gtk.Label(label=label)
        lab.set_xalign(0)
        box.pack_start(lab, True, True, 0)

        item.add(box)
        item.show_all()
        return item

    def _flag_path_for_locale(self, locale_code, cc=""):
        candidates = []
        if locale_code:
            candidates.append(os.path.join("/usr/local/Oply/icons/tv/flags", f"{locale_code}.png"))
            candidates.append(os.path.join("/usr/local/Oply/icons/radio/flags", f"{locale_code}.png"))
        if cc:
            candidates.append(os.path.join("/usr/local/Oply/icons/tv/flags", f"{cc}.png"))
            candidates.append(os.path.join("/usr/local/Oply/icons/radio/flags", f"{cc}.png"))
        for p in candidates:
            if os.path.exists(p):
                return p
        return None

    def _tray_select_country(self, locale_id):
        try:
            self.cmb.set_active_id(locale_id)
        except Exception:
            pass
        try:
            self.load_cached()
        except Exception:
            pass
        try:
           
            if locale_id != "FAV":
                self.on_refresh(None)
        except Exception:
            pass

    def _tray_play_favorite(self, fav):
        try:
            name = (fav.get("name") or "").strip()
            url = (fav.get("url") or "").strip()
            if not url:
                return
            self.play_station(name, url)
            self.restore_window()
        except Exception:
            pass

    def _systray_refresh(self):
        """Reconstruye menú (cuando cambian favoritos, idioma, etc.)."""
        if self.indicator:
            self.create_systray_menu()

    def create_systray_menu(self):
        if not self.indicator:
            return

        menu = Gtk.Menu()

        # Mostrar ventana
        item_show = self._tray_item(self.TEXT.get("restore", "Show Window"), icon_name="window-new-symbolic")
        item_show.connect("activate", lambda *_: self.restore_window())
        menu.append(item_show)

        # Stop
        item_stop = self._tray_item(self.TEXT.get("stop", "Stop"), icon_name="media-playback-stop-symbolic")
        item_stop.connect("activate", lambda *_: self.on_stop(None))
        menu.append(item_stop)

        menu.append(Gtk.SeparatorMenuItem())

        # Favoritos (submenu)
        fav_item = self._tray_item(self.TEXT.get("tray_favorites", self.TEXT.get("favorites", "Favorites")), icon_name="emblem-favorite-symbolic")
        fav_menu = Gtk.Menu()
        favs = self.load_favorites()
        if favs:
            for it in favs:
                cname = (it.get("country") or "").strip()
                cc = (it.get("cc") or "").strip()
                label = f"{cname} ({cc}) — {it.get('name','')}".strip(" —")
                fp = self._flag_path_for_locale(it.get("locale",""), cc)
                mi = self._tray_item(label, icon_name="audio-speakers-symbolic", icon_path=fp)
                mi.connect("activate", lambda *_ , fav=it: self._tray_play_favorite(fav))
                fav_menu.append(mi)
        else:
            mi = Gtk.MenuItem(label=self.TEXT.get("no_fav", "No favorites yet"))
            mi.set_sensitive(False)
            fav_menu.append(mi)
        fav_menu.show_all()
        fav_item.set_submenu(fav_menu)
        menu.append(fav_item)

        # País (submenu)
        country_item = self._tray_item(self.TEXT.get("tray_country", self.TEXT.get("country", "Country")), icon_name="emblem-web-symbolic")
        country_menu = Gtk.Menu()

        # Favoritos como opción rápida
        fav_quick = self._tray_item(f"★ {self.TEXT.get('favorites','Favorites')}", icon_name="emblem-favorite-symbolic")
        fav_quick.connect("activate", lambda *_: self._tray_select_country("FAV"))
        country_menu.append(fav_quick)

        for code, label, cc in RADIO_LOCALES:
            fp = self._flag_path_for_locale(code, cc)
            mi = self._tray_item(f"{code} — {label}", icon_name="flag-symbolic", icon_path=fp)
            mi.connect("activate", lambda *_ , c=code: self._tray_select_country(c))
            country_menu.append(mi)

        country_menu.show_all()
        country_item.set_submenu(country_menu)
        menu.append(country_item)

        menu.append(Gtk.SeparatorMenuItem())

        # Volumen (submenu)
        item_vol = Gtk.MenuItem(label=self.TEXT.get("volume", "Volume"))
        vol_sub = Gtk.Menu()
        vol_item = Gtk.MenuItem()
        vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        try:
            vol_scale.set_value(float(self.vol.get_value()))
        except Exception:
            vol_scale.set_value(50)
        vol_scale.set_size_request(150, -1)
        vol_scale.connect("value-changed", lambda s: self.vol.set_value(s.get_value()))
        vol_item.add(vol_scale)
        vol_sub.append(vol_item)
        item_vol.set_submenu(vol_sub)
        menu.append(item_vol)

        menu.append(Gtk.SeparatorMenuItem())

        # Salir
        item_quit = self._tray_item(self.TEXT.get("exit", "Exit"), icon_name="application-exit-symbolic")
        item_quit.connect("activate", lambda *_: self.quit_application())
        menu.append(item_quit)

        menu.show_all()
        self.indicator.set_menu(menu)

    def on_window_delete(self, widget, event):
        """Cerrar ventana: minimizar al tray o salir (como Oply)."""
        if not self.indicator:
            self.quit_application()
            return True

        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text=self.TEXT.get("close_dialog_title", "Close Oply Radio?")
        )
        dialog.format_secondary_text(self.TEXT.get("close_dialog_message", "What do you want to do?"))

        dialog.add_button(self.TEXT.get("minimize_to_tray", "Minimize to Tray"), Gtk.ResponseType.NO)
        dialog.add_button(self.TEXT.get("quit_app", "Quit Application"), Gtk.ResponseType.YES)

        resp = dialog.run()
        dialog.destroy()

        if resp == Gtk.ResponseType.NO:
            self.minimize_to_tray()
            return True
        elif resp == Gtk.ResponseType.YES:
            self.quit_application()
            return True
        return True

    def restore_window(self):
        self.show_all()
        self.present()

    def minimize_to_tray(self):
        self.hide()

    def quit_application(self):
        self.on_destroy()

#  UI actions 

    def on_country_changed(self, combo):
        try:
            self.search.set_text("")
        except Exception:
            pass
        self.load_cached()


    def on_volume_changed(self, scale):
        self._mpv_set("volume", float(scale.get_value()))

    def on_refresh(self, button):
        sel = self._selected_locale()
        if not sel:
            
            self._toast(self.TEXT["favorites"])
            return

        code, label, cc = sel
        self._show_loading(self.TEXT["loading"])

        def _worker():
            try:
                stations = fetch_stations_by_country(cc, limit=250)
                self.save_cached(code, stations)
                GLib.idle_add(self.load_cached)
            except Exception:
                GLib.idle_add(self._toast, self.TEXT["err_fetch"])
                GLib.idle_add(self.load_cached)
            finally:
                GLib.idle_add(self._hide_loading)

        
        import threading
        threading.Thread(target=_worker, daemon=True).start()

    def on_add_station(self, button):
        dlg = Gtk.Dialog(title=self.TEXT["add"], transient_for=self, flags=Gtk.DialogFlags.MODAL)
        dlg.add_button(self.TEXT["cancel"], Gtk.ResponseType.CANCEL)
        dlg.add_button(self.TEXT["save"], Gtk.ResponseType.OK)
        dlg.set_default_size(420, 120)

        box = dlg.get_content_area()
        grid = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        box.add(grid)

        e_name = Gtk.Entry()
        e_url = Gtk.Entry()
        e_url.set_placeholder_text("https://...")

        grid.attach(Gtk.Label(label=self.TEXT["name"] + ":"), 0, 0, 1, 1)
        grid.attach(e_name, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=self.TEXT["url"] + ":"), 0, 1, 1, 1)
        grid.attach(e_url, 1, 1, 1, 1)

        dlg.show_all()
        resp = dlg.run()
        if resp == Gtk.ResponseType.OK:
            name = (e_name.get_text() or "").strip()
            url = (e_url.get_text() or "").strip()
            if name and url:
                sel = self._selected_locale() or RADIO_LOCALES[0]
                code, label, cc = sel
                p = self._cache_file(code)
                stations = []
                try:
                    if os.path.exists(p):
                        with open(p, "r", encoding="utf-8") as f:
                            stations = json.load(f)
                except Exception:
                    stations = []
                if not isinstance(stations, list):
                    stations = []
                stations.insert(0, {"name": name, "url": url, "favicon": ""})
                self.save_cached(code, stations)
                self.load_cached()
        dlg.destroy()

    def on_station_activated(self, tree, path, col):
        it = self.filter.get_iter(path)
        name = self.filter.get_value(it, 0)
        url = self.filter.get_value(it, 1)
        self.play_station(name, url)

    def play_station(self, name, url):
        self.current_station = (name, url)
        self.now.set_markup(f"<b>{GLib.markup_escape_text(name)}</b>")
        self.hb.props.subtitle = name
        self._show_connecting(name)

        # mpv load
        self._mpv_send(["loadfile", url, "replace"], request_id=2, want_reply=False)
        self._mpv_set("pause", False)
        self._connecting_started = time.time()

        # wait until it starts (hide overlay)
        GLib.timeout_add(200, self._poll_playback_started)

    def _poll_playback_started(self):
        # timeout
        if (time.time() - self._connecting_started) * 1000 > self._connect_timeout_ms:
            self._hide_loading()
            self._hide_connecting()
            return False

        core_idle = self._mpv_get("core-idle")
        paused_for_cache = self._mpv_get("paused-for-cache")
        time_pos = self._mpv_get("time-pos")


        if core_idle is False and (paused_for_cache in (False, None)) and (time_pos is not None):
            self._hide_connecting()
            return False

        return True

    def on_stop(self, button):
        self._mpv_send(["stop"], request_id=3, want_reply=False)
        self.hb.props.subtitle = self.TEXT["subtitle"]
        self.now.set_markup("<b>—</b>")

    
    #favorites 
    def load_favorites(self):
        try:
            if os.path.exists(FAVORITES_FILE):
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        out = []
                        for it in data:
                            if not isinstance(it, dict):
                                continue
                            name = (it.get("name") or "").strip()
                            url = (it.get("url") or "").strip()
                            if not name or not url:
                                continue
                            out.append({
                                "name": name,
                                "url": url,
                                "locale": (it.get("locale") or "").strip(),
                                "country": (it.get("country") or "").strip(),
                                "cc": (it.get("cc") or "").strip(),
                                "added": (it.get("added") or "").strip(),
                            })
                        return out
        except Exception:
            pass
        return []

    def save_favorites(self):
        try:
            os.makedirs(RADIO_DIR, exist_ok=True)
            with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def is_favorite(self, url):
        u = (url or "").strip()
        return any((it.get("url") or "").strip() == u for it in self.favorites)

    def add_favorite(self, name, url):
        name = (name or "").strip()
        url = (url or "").strip()
        if not name or not url or self.is_favorite(url):
            return

        sel = self._selected_locale()
        locale_code, country_name, cc = ("", "", "")
        if sel:
            locale_code, country_name, cc = sel

        self.favorites = self.load_favorites()
        self.favorites.append({
            "name": name,
            "url": url,
            "locale": locale_code,
            "country": country_name,
            "cc": cc,
            "added": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        self.save_favorites()
        self._rebuild_favorites_popover()
        self._refresh_favorites_views()

    def remove_favorite(self, url):
        url = (url or "").strip()
        self.favorites = [it for it in self.load_favorites() if (it.get("url") or "").strip() != url]
        self.save_favorites()
        self._rebuild_favorites_popover()
        self._refresh_favorites_views()

    def _rebuild_favorites_popover(self):
        try:
            for ch in list(self.fav_listbox.get_children()):
                self.fav_listbox.remove(ch)
        except Exception:
            return

        self.favorites = self.load_favorites()
        if not self.favorites:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label=self.TEXT["no_fav"])
            lbl.set_xalign(0)
            row.add(lbl)
            self.fav_listbox.add(row)
            self.fav_listbox.show_all()
            return

        for it in list(self.favorites)[::-1]:
            name = (it.get("name") or "").strip()
            url = (it.get("url") or "").strip()
            country = (it.get("country") or "").strip()
            cc = (it.get("cc") or "").strip()
            display = f"{country} ({cc}) — {name}" if (country or cc) else name

            row = Gtk.ListBoxRow()
            row._fav_url = url
            row._fav_name = name
            lbl = Gtk.Label(label=display)
            lbl.set_xalign(0)
            lbl.set_ellipsize(3)
            row.add(lbl)
            self.fav_listbox.add(row)

        self.fav_listbox.show_all()

    def _on_fav_row_activated(self, listbox, row):
        if not row:
            return
        url = getattr(row, "_fav_url", "")
        name = getattr(row, "_fav_name", "")
        if url and name and name != self.TEXT["no_fav"]:
            self.play_station(name, url)

    def _open_favorites_file(self, *args):
        try:
            os.makedirs(RADIO_DIR, exist_ok=True)
            if not os.path.exists(FAVORITES_FILE):
                with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            subprocess.Popen(["xdg-open", FAVORITES_FILE])
        except Exception:
            pass

    def _load_favorites_into_store(self):
        self.favorites = self.load_favorites()
        if not self.favorites:
            return
        for it in self.favorites:
            name = (it.get("name") or "").strip()
            url = (it.get("url") or "").strip()
            country = (it.get("country") or "").strip()
            cc = (it.get("cc") or "").strip()
            if not name or not url:
                continue
            display = f"{country} ({cc}) — {name}" if (country or cc) else name
            self.store.append([display, url])

    def _refresh_favorites_views(self):

        try:
            active_id = self.cmb.get_active_id()
        except Exception:
            active_id = None
        if active_id == "FAV":
            self.load_cached()

        
        try:
            if self.favorites and self.cmb.get_active_id() is None:
                self.cmb.set_active_id("FAV")
        except Exception:
            pass
        try:
            self._systray_refresh()
        except Exception:
            pass


    def on_tree_button_press(self, tree, event):
        if event.button != 3:
            return False

        pathinfo = tree.get_path_at_pos(int(event.x), int(event.y))
        if not pathinfo:
            return False
        path, col, cellx, celly = pathinfo
        tree.grab_focus()
        tree.set_cursor(path, col, 0)

        it = self.filter.get_iter(path)
        name = self.filter.get_value(it, 0)
        url = self.filter.get_value(it, 1)

        menu = Gtk.Menu()
        if self.is_favorite(url):
            mi = Gtk.MenuItem(label=self.TEXT["remove_fav"])
            mi.connect("activate", lambda *_: self.remove_favorite(url))
            menu.append(mi)
        else:
            mi = Gtk.MenuItem(label=self.TEXT["add_fav"])
            mi.connect("activate", lambda *_: self.add_favorite(name, url))
            menu.append(mi)

        menu.show_all()
        menu.popup_at_pointer(event)
        return True

# overlays 
    def _show_loading(self, msg):
        self.conn_label.set_text(msg)
        self.spinner.start()
        self.conn_box.show()

    def _hide_loading(self):
        self.spinner.stop()
        self.conn_box.hide()

    def _show_connecting(self, station_name):
        self.conn_label.set_text(f"{self.TEXT['connecting_to']} {station_name}")
        self.spinner.start()
        self.conn_box.show()

    def _hide_connecting(self):
        self.spinner.stop()
        self.conn_box.hide()

    def _toast(self, message):
        
        md = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Oply Radio"
        )
        md.format_secondary_text(message)
        md.run()
        md.destroy()

    def on_destroy(self, *args):
        
        try:
            self._mpv_send(["quit"], request_id=99, want_reply=False)
        except Exception:
            pass

        try:
            if hasattr(self, "mpv") and self.mpv:
                try:
                    self.mpv.terminate()
                    self.mpv.wait(timeout=1.5)
                except Exception:
                    try:
                        self.mpv.kill()
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            if os.path.exists(self.mpv_socket):
                os.remove(self.mpv_socket)
        except Exception:
            pass

        try:
            Gtk.main_quit()
        except Exception:
            pass

def main():

    app = OplyRadio()
    Gtk.main()

if __name__ == "__main__":
    main()
