#!/usr/bin/env python3
# Oply - Advanced Audio Player Estilo GNOME
# Author: josejp2424
# Version: 2.1 (GTK3) - Con soporte para ConkySwitcher
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
try:
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio, AyatanaAppIndicator3 as AppIndicator3
    APPINDICATOR_AVAILABLE = True
except (ValueError, ImportError):
    from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Gio
    APPINDICATOR_AVAILABLE = False
    print("Warning: AyatanaAppIndicator3 not available. Systray will not work.")
    print("Install with: sudo apt install gir1.2-ayatanaappindicator3-0.1")

import subprocess
import os
import glob
import sys
import socket
import threading
import json
import time
import math
import random
from pathlib import Path

# Configuración
SOCKET_PATH = "/tmp/oply_socket"
CONFIG_DIR = os.path.expanduser("~/.config/oply")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
PLAYLISTS_DIR = os.path.join(CONFIG_DIR, "playlists")
LANG_FILE = os.path.join(CONFIG_DIR, "language.json")
ICON_PATH = "/usr/local/Oply/icons/oply.svg"
SUPPORTED_FORMATS = ['*.mp3', '*.wav', '*.ogg', '*.flac', '*.m4a', '*.aac', '*.mp4', '*.m4v', '*.webm']

# ============================================================================
# SOPORTE PARA CONKY - Exportar estado de reproducción
# Agregado por josejp2424 para integración con ConkySwitcher
# ============================================================================
STATE_FILE = os.path.join(CONFIG_DIR, "now_playing.json")

def update_now_playing(title, artist="", is_playing=True):
    """Actualiza el archivo de estado para Conky"""
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        data = {
            'title': title,
            'artist': artist,
            'is_playing': is_playing,
            'player': 'Oply'
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error updating now playing: {e}")

def clear_now_playing():
    """Limpia el estado de reproducción"""
    try:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    except:
        pass
# ============================================================================

LANGUAGES = {
    "en": {
        "title": "Oply Audio Player",
        "add_files": "Add Files",
        "add_folder": "Add Folder",
        "save_playlist": "Save Playlist",
        "load_playlist": "Load Playlist",
        "clear": "Clear Playlist",
        "subtitle": "No audio loaded",
        "playing": "Playing",
        "play_pause": "Play/Pause",
        "next": "Next",
        "previous": "Previous",
        "restore": "Show Window",
        "exit": "Exit",
        "volume": "Volume",
        "close_dialog_title": "Close Oply?",
        "close_dialog_message": "What do you want to do?",
        "minimize_to_tray": "Minimize to Tray",
        "quit_app": "Quit Application",
        "youtube_download": "Download music or video from YouTube",
        "about_audio_desc": "Advanced audio player with album art,\nplaylist management and systray support",
        "about_video_desc": "Lightweight video player with\nfullscreen and subtitle support",
        "about_convert_desc": "YouTube video downloader and\naudio/video format converter",
        "about_created": "Created by:",
        "about_license": "License:",
        "about_close": "Close"
    },
    "es": {
        "title": "Oply Reproductor de Audio",
        "add_files": "Añadir Archivos",
        "add_folder": "Añadir Carpeta",
        "save_playlist": "Guardar Lista",
        "load_playlist": "Cargar Lista",
        "clear": "Limpiar Lista",
        "subtitle": "Sin audio cargado",
        "playing": "Reproduciendo",
        "play_pause": "Reproducir/Pausa",
        "next": "Siguiente",
        "previous": "Anterior",
        "restore": "Mostrar Ventana",
        "exit": "Salir",
        "volume": "Volumen",
        "close_dialog_title": "¿Cerrar Oply?",
        "close_dialog_message": "¿Qué deseas hacer?",
        "minimize_to_tray": "Minimizar a Bandeja",
        "quit_app": "Salir de la Aplicación",
        "youtube_download": "Descargar música o video desde YouTube",
        "about_audio_desc": "Reproductor de audio avanzado con carátulas,\ngestión de listas de reproducción y soporte de bandeja",
        "about_video_desc": "Reproductor de video ligero con\nsoporte de pantalla completa y subtítulos",
        "about_convert_desc": "Descargador de videos de YouTube y\nconversor de formatos de audio/video",
        "about_created": "Creado por:",
        "about_license": "Licencia:",
        "about_close": "Cerrar"
    },
    "ca": {
        "title": "Oply Reproductor d'Àudio",
        "add_files": "Afegir Arxius",
        "add_folder": "Afegir Carpeta",
        "save_playlist": "Guardar Llista",
        "load_playlist": "Carregar Llista",
        "clear": "Netejar Llista",
        "subtitle": "Sense àudio carregat",
        "playing": "Reproduint",
        "play_pause": "Reproduir/Pausa",
        "next": "Següent",
        "previous": "Anterior",
        "restore": "Mostrar Finestra",
        "exit": "Sortir",
        "volume": "Volum",
        "close_dialog_title": "Tancar Oply?",
        "close_dialog_message": "Què vols fer?",
        "minimize_to_tray": "Minimitzar a la Safata",
        "quit_app": "Sortir de l'Aplicació",
        "youtube_download": "Descarregar música o vídeo des de YouTube",
        "about_audio_desc": "Reproductor d'àudio avançat amb caràtules,\ngestió de llistes de reproducció i suport de safata",
        "about_video_desc": "Reproductor de vídeo lleuger amb\nsuport de pantalla completa i subtítols",
        "about_convert_desc": "Descarregador de vídeos de YouTube i\nconversor de formats d'àudio/vídeo",
        "about_created": "Creat per:",
        "about_license": "Llicència:",
        "about_close": "Tancar"
    },
    "fr": {
        "title": "Oply Lecteur Audio",
        "add_files": "Ajouter des Fichiers",
        "add_folder": "Ajouter un Dossier",
        "save_playlist": "Enregistrer la Liste",
        "load_playlist": "Charger la Liste",
        "clear": "Effacer la Liste",
        "subtitle": "Aucun audio chargé",
        "playing": "Lecture en cours",
        "play_pause": "Lecture/Pause",
        "next": "Suivant",
        "previous": "Précédent",
        "restore": "Afficher la Fenêtre",
        "exit": "Quitter",
        "volume": "Volume",
        "close_dialog_title": "Fermer Oply?",
        "close_dialog_message": "Que voulez-vous faire?",
        "minimize_to_tray": "Réduire dans la Barre",
        "quit_app": "Quitter l'Application",
        "youtube_download": "Télécharger de la musique ou des vidéos depuis YouTube",
        "about_audio_desc": "Lecteur audio avancé avec pochettes d'album,\ngestion de listes de lecture et support de barre d'état",
        "about_video_desc": "Lecteur vidéo léger avec\nsupport plein écran et sous-titres",
        "about_convert_desc": "Téléchargeur de vidéos YouTube et\nconvertisseur de formats audio/vidéo",
        "about_created": "Créé par:",
        "about_license": "Licence:",
        "about_close": "Fermer"
    },
    "de": {
        "title": "Oply Audio-Player",
        "add_files": "Dateien Hinzufügen",
        "add_folder": "Ordner Hinzufügen",
        "save_playlist": "Playlist Speichern",
        "load_playlist": "Playlist Laden",
        "clear": "Playlist Leeren",
        "subtitle": "Kein Audio geladen",
        "playing": "Wird Abgespielt",
        "play_pause": "Wiedergabe/Pause",
        "next": "Nächster",
        "previous": "Vorheriger",
        "restore": "Fenster Anzeigen",
        "exit": "Beenden",
        "volume": "Lautstärke",
        "close_dialog_title": "Oply Schließen?",
        "close_dialog_message": "Was möchten Sie tun?",
        "minimize_to_tray": "In Taskleiste Minimieren",
        "quit_app": "Anwendung Beenden",
        "youtube_download": "Musik oder Video von YouTube herunterladen",
        "about_audio_desc": "Erweiterter Audio-Player mit Album-Cover,\nWiedergabelistenverwaltung und Taskleistenunterstützung",
        "about_video_desc": "Leichter Video-Player mit\nVollbildmodus und Untertitelunterstützung",
        "about_convert_desc": "YouTube-Video-Downloader und\nAudio/Video-Format-Konverter",
        "about_created": "Erstellt von:",
        "about_license": "Lizenz:",
        "about_close": "Schließen"
    },
    "it": {
        "title": "Oply Lettore Audio",
        "add_files": "Aggiungi File",
        "add_folder": "Aggiungi Cartella",
        "save_playlist": "Salva Playlist",
        "load_playlist": "Carica Playlist",
        "clear": "Cancella Playlist",
        "subtitle": "Nessun audio caricato",
        "playing": "In Riproduzione",
        "play_pause": "Riproduci/Pausa",
        "next": "Successivo",
        "previous": "Precedente",
        "restore": "Mostra Finestra",
        "exit": "Esci",
        "volume": "Volume",
        "close_dialog_title": "Chiudere Oply?",
        "close_dialog_message": "Cosa vuoi fare?",
        "minimize_to_tray": "Riduci a Icona",
        "quit_app": "Chiudi Applicazione",
        "youtube_download": "Scarica musica o video da YouTube",
        "about_audio_desc": "Lettore audio avanzato con copertine,\ngestione playlist e supporto barra di sistema",
        "about_video_desc": "Lettore video leggero con\nsupporto schermo intero e sottotitoli",
        "about_convert_desc": "Scaricatore video YouTube e\nconvertitore formati audio/video",
        "about_created": "Creato da:",
        "about_license": "Licenza:",
        "about_close": "Chiudi"
    },
    "pt": {
        "title": "Oply Reprodutor de Áudio",
        "add_files": "Adicionar Arquivos",
        "add_folder": "Adicionar Pasta",
        "save_playlist": "Salvar Lista",
        "load_playlist": "Carregar Lista",
        "clear": "Limpar Lista",
        "subtitle": "Nenhum áudio carregado",
        "playing": "Reproduzindo",
        "play_pause": "Reproduzir/Pausar",
        "next": "Próximo",
        "previous": "Anterior",
        "restore": "Mostrar Janela",
        "exit": "Sair",
        "volume": "Volume",
        "close_dialog_title": "Fechar Oply?",
        "close_dialog_message": "O que você deseja fazer?",
        "minimize_to_tray": "Minimizar para Bandeja",
        "quit_app": "Sair da Aplicação",
        "youtube_download": "Baixar música ou vídeo do YouTube",
        "about_audio_desc": "Reprodutor de áudio avançado com capas,\ngerenciamento de listas e suporte de bandeja",
        "about_video_desc": "Reprodutor de vídeo leve com\nsuporte de tela cheia e legendas",
        "about_convert_desc": "Baixador de vídeos do YouTube e\nconversor de formatos de áudio/vídeo",
        "about_created": "Criado por:",
        "about_license": "Licença:",
        "about_close": "Fechar"
    },
    "ru": {
        "title": "Oply Аудиоплеер",
        "add_files": "Добавить Файлы",
        "add_folder": "Добавить Папку",
        "save_playlist": "Сохранить Плейлист",
        "load_playlist": "Загрузить Плейлист",
        "clear": "Очистить Плейлист",
        "subtitle": "Аудио не загружено",
        "playing": "Воспроизведение",
        "play_pause": "Воспроизведение/Пауза",
        "next": "Следующий",
        "previous": "Предыдущий",
        "restore": "Показать Окно",
        "exit": "Выход",
        "volume": "Громкость",
        "close_dialog_title": "Закрыть Oply?",
        "close_dialog_message": "Что вы хотите сделать?",
        "minimize_to_tray": "Свернуть в Трей",
        "quit_app": "Выйти из Приложения",
        "youtube_download": "Скачать музыку или видео с YouTube",
        "about_audio_desc": "Расширенный аудиоплеер с обложками,\nуправлением плейлистами и поддержкой трея",
        "about_video_desc": "Легкий видеоплеер с поддержкой\nполноэкранного режима и субтитров",
        "about_convert_desc": "Загрузчик видео с YouTube и\nконвертер аудио/видео форматов",
        "about_created": "Создано:",
        "about_license": "Лицензия:",
        "about_close": "Закрыть"
    },
    "ja": {
        "title": "Oply オーディオプレーヤー",
        "add_files": "ファイルを追加",
        "add_folder": "フォルダを追加",
        "save_playlist": "プレイリストを保存",
        "load_playlist": "プレイリストを読み込む",
        "clear": "プレイリストをクリア",
        "subtitle": "オーディオが読み込まれていません",
        "playing": "再生中",
        "play_pause": "再生/一時停止",
        "next": "次へ",
        "previous": "前へ",
        "restore": "ウィンドウを表示",
        "exit": "終了",
        "volume": "音量",
        "close_dialog_title": "Oplyを閉じますか？",
        "close_dialog_message": "何をしますか？",
        "minimize_to_tray": "トレイに最小化",
        "quit_app": "アプリケーションを終了",
        "youtube_download": "YouTubeから音楽または動画をダウンロード",
        "about_audio_desc": "アルバムアート付き高度なオーディオプレーヤー、\nプレイリスト管理とトレイサポート",
        "about_video_desc": "フルスクリーンと\n字幕サポート付き軽量ビデオプレーヤー",
        "about_convert_desc": "YouTubeビデオダウンローダーと\nオーディオ/ビデオフォーマットコンバーター",
        "about_created": "作成者:",
        "about_license": "ライセンス:",
        "about_close": "閉じる"
    },
    "zh": {
        "title": "Oply 音频播放器",
        "add_files": "添加文件",
        "add_folder": "添加文件夹",
        "save_playlist": "保存播放列表",
        "load_playlist": "加载播放列表",
        "clear": "清空播放列表",
        "subtitle": "未加载音频",
        "playing": "正在播放",
        "play_pause": "播放/暂停",
        "next": "下一首",
        "previous": "上一首",
        "restore": "显示窗口",
        "exit": "退出",
        "volume": "音量",
        "close_dialog_title": "关闭 Oply？",
        "close_dialog_message": "您想做什么？",
        "minimize_to_tray": "最小化到托盘",
        "quit_app": "退出应用程序",
        "youtube_download": "从YouTube下载音乐或视频",
        "about_audio_desc": "高级音频播放器，带专辑封面、\n播放列表管理和托盘支持",
        "about_video_desc": "轻量级视频播放器，\n支持全屏和字幕",
        "about_convert_desc": "YouTube视频下载器和\n音频/视频格式转换器",
        "about_created": "创建者：",
        "about_license": "许可证：",
        "about_close": "关闭"
    },
    "ar": {
        "title": "Oply مشغل الصوت",
        "add_files": "إضافة ملفات",
        "add_folder": "إضافة مجلد",
        "save_playlist": "حفظ قائمة التشغيل",
        "load_playlist": "تحميل قائمة التشغيل",
        "clear": "مسح قائمة التشغيل",
        "subtitle": "لم يتم تحميل صوت",
        "playing": "قيد التشغيل",
        "play_pause": "تشغيل/إيقاف مؤقت",
        "next": "التالي",
        "previous": "السابق",
        "restore": "إظهار النافذة",
        "exit": "خروج",
        "volume": "مستوى الصوت",
        "close_dialog_title": "إغلاق Oply؟",
        "close_dialog_message": "ماذا تريد أن تفعل؟",
        "minimize_to_tray": "تصغير إلى الدرج",
        "quit_app": "إنهاء التطبيق",
        "youtube_download": "تحميل موسيقى أو فيديو من يوتيوب",
        "about_audio_desc": "مشغل صوت متقدم مع أغلفة الألبومات،\nإدارة قوائم التشغيل ودعم الدرج",
        "about_video_desc": "مشغل فيديو خفيف مع\nدعم وضع ملء الشاشة والترجمات",
        "about_convert_desc": "محمل فيديو يوتيوب ومحول\nتنسيقات الصوت/الفيديو",
        "about_created": "صنع بواسطة:",
        "about_license": "الترخيص:",
        "about_close": "إغلاق"
    },
    "ko": {
        "title": "Oply 오디오 플레이어",
        "add_files": "파일 추가",
        "add_folder": "폴더 추가",
        "save_playlist": "재생목록 저장",
        "load_playlist": "재생목록 불러오기",
        "clear": "재생목록 지우기",
        "subtitle": "오디오가 로드되지 않음",
        "playing": "재생 중",
        "play_pause": "재생/일시정지",
        "next": "다음",
        "previous": "이전",
        "restore": "창 표시",
        "exit": "종료",
        "volume": "볼륨",
        "close_dialog_title": "Oply를 닫으시겠습니까?",
        "close_dialog_message": "무엇을 하시겠습니까?",
        "minimize_to_tray": "트레이로 최소화",
        "quit_app": "애플리케이션 종료",
        "youtube_download": "YouTube에서 음악 또는 비디오 다운로드",
        "about_audio_desc": "앨범 아트, 재생목록 관리 및\n트레이 지원이 있는 고급 오디오 플레이어",
        "about_video_desc": "전체화면 및 자막을\n지원하는 경량 비디오 플레이어",
        "about_convert_desc": "YouTube 비디오 다운로더 및\n오디오/비디오 형식 변환기",
        "about_created": "제작자:",
        "about_license": "라이선스:",
        "about_close": "닫기"
    },
    "pl": {
        "title": "Oply Odtwarzacz Audio",
        "add_files": "Dodaj Pliki",
        "add_folder": "Dodaj Folder",
        "save_playlist": "Zapisz Playlistę",
        "load_playlist": "Załaduj Playlistę",
        "clear": "Wyczyść Playlistę",
        "subtitle": "Nie załadowano audio",
        "playing": "Odtwarzanie",
        "play_pause": "Odtwarzanie/Pauza",
        "next": "Następny",
        "previous": "Poprzedni",
        "restore": "Pokaż Okno",
        "exit": "Wyjście",
        "volume": "Głośność",
        "close_dialog_title": "Zamknąć Oply?",
        "close_dialog_message": "Co chcesz zrobić?",
        "minimize_to_tray": "Minimalizuj do Zasobnika",
        "quit_app": "Zakończ Aplikację",
        "youtube_download": "Pobierz muzykę lub wideo z YouTube",
        "about_audio_desc": "Zaawansowany odtwarzacz audio z okładkami,\nzarządzaniem playlistami i wsparciem zasobnika",
        "about_video_desc": "Lekki odtwarzacz wideo z\nwsparciem pełnego ekranu i napisów",
        "about_convert_desc": "Pobieracz wideo YouTube i\nkonwerter formatów audio/wideo",
        "about_created": "Stworzony przez:",
        "about_license": "Licencja:",
        "about_close": "Zamknij"
    }
}

def load_language():
    """Detecta el idioma del sistema automáticamente"""

    try:
        if os.path.exists(LANG_FILE):
            with open(LANG_FILE, 'r') as f:
                config = json.load(f)
                lang = config.get("language", "")
                if lang and lang in LANGUAGES:
                    return LANGUAGES[lang]
    except:
        pass
    

    lang_env = os.environ.get('LANG', '')
    
    if lang_env and lang_env != 'C' and lang_env != 'POSIX':
        lang_code = lang_env.split('_')[0].lower()
        if lang_code in LANGUAGES:
            return LANGUAGES[lang_code]
    

    return LANGUAGES["en"]

def save_language(lang_code):
    """Guarda el idioma seleccionado manualmente"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(LANG_FILE, 'w') as f:
            json.dump({"language": lang_code}, f)
    except Exception as e:
        print(f"Error saving language: {e}")

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"last_playlist": ""}

def save_config(last_playlist=""):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"last_playlist": last_playlist}, f)
    except Exception as e:
        print(f"Error saving config: {e}")

def format_duration(seconds):
    seconds = int(seconds)
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

def get_metadata(filepath):
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        dur_res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = float(dur_res.stdout.strip()) if dur_res.returncode == 0 else 0

        cmd_title = [
            "ffprobe", "-v", "error",
            "-show_entries", "format_tags=title",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        title_res = subprocess.run(cmd_title, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        title = title_res.stdout.strip() if title_res.returncode == 0 and title_res.stdout.strip() else os.path.basename(filepath)


        cmd_artist = [
            "ffprobe", "-v", "error",
            "-show_entries", "format_tags=artist",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        artist_res = subprocess.run(cmd_artist, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        artist = artist_res.stdout.strip() if artist_res.returncode == 0 else ""

        cmd_album = [
            "ffprobe", "-v", "error",
            "-show_entries", "format_tags=album",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        album_res = subprocess.run(cmd_album, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        album = album_res.stdout.strip() if album_res.returncode == 0 else ""


        if not artist and not album:
            filename = os.path.basename(filepath)
            name_without_ext = os.path.splitext(filename)[0]


            if ' - ' in name_without_ext:
                parts = name_without_ext.split(' - ')
                if len(parts) >= 2:
                    artist = parts[0].strip()
                   
                    if len(parts) >= 3:
                        album = parts[1].strip()

        return {"title": title, "duration": duration, "artist": artist, "album": album}
    except:
        return {"title": os.path.basename(filepath), "duration": 0, "artist": "", "album": ""}


def detect_embedded_cover_ext(filepath):
    """Devuelve 'jpg' o 'png' si hay carátula embebida (stream v:0); si no, None."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
        codec = (res.stdout or "").strip().lower()
        if not codec:
            return None
        if "png" in codec:
            return "png"

        return "jpg"
    except:
        return None

def extract_cover_art(filepath, out_base_no_ext):
    """
    Extrae carátula embebida del audio.
    Retorna (True, output_path) si pudo; si no, (False, None)
    """
    try:
        ext = detect_embedded_cover_ext(filepath)
        if not ext:
            return (False, None)


        for e in ("jpg", "png"):
            p = f"{out_base_no_ext}.{e}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

        output_path = f"{out_base_no_ext}.{ext}"


        cmd = [
            "ffmpeg", "-y", "-i", filepath,
            "-map", "0:v:0",
            "-frames:v", "1",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return (True, output_path)

        return (False, None)
    except:
        return (False, None)


class AudioVisualizer(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.set_size_request(280, 80)
        self.bars = [0] * 32  
        self.animation_id = None
        self.is_playing = False
        

        self.set_property("height-request", 80)
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        

        self.connect("draw", self.on_draw)
        
    def start_animation(self):
        """Iniciar animación del ecualizador"""
        if self.animation_id is None:
            self.is_playing = True
            self.animation_id = GLib.timeout_add(100, self.update_bars)
            
    def stop_animation(self):
        """Detener animación"""
        self.is_playing = False
        if self.animation_id:
            GLib.source_remove(self.animation_id)
            self.animation_id = None
        self.bars = [0] * 32
        self.queue_draw()
    
    def update_bars(self):
        """Actualizar valores de las barras (simulando ritmo de música)"""
        if not self.is_playing:
            return False
            

        for i in range(len(self.bars)):

            self.bars[i] = max(0, self.bars[i] - random.uniform(0.02, 0.05))
            
           
            if random.random() < 0.3:  
                if self.is_playing:
                    
                    frequency_factor = 1.0
                    if i < 8: 
                        frequency_factor = 0.7 if random.random() < 0.2 else 0.3
                    elif i < 24: 
                        frequency_factor = 1.0
                    else: 
                        frequency_factor = 0.8 if random.random() < 0.4 else 0.4
                    
                    self.bars[i] = min(1.0, self.bars[i] + random.uniform(0.1, 0.3) * frequency_factor)
        
        self.queue_draw()
        return True
    
    def on_draw(self, widget, cr):
        """Dibujar el ecualizador"""
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        

        cr.set_source_rgba(0.1, 0.1, 0.1, 0.3)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        

        bar_count = len(self.bars)
        bar_width = (width - 20) / bar_count
        spacing = 2
        
        for i, bar_height in enumerate(self.bars):
            x = 10 + i * (bar_width + spacing)
            bar_h = bar_height * (height - 20)
            

            if i < 8: 
                r, g, b = 0.2, 0.4, 0.8
            elif i < 24: 
                r, g, b = 0.4, 0.8, 0.2
            else:  
                r, g, b = 0.8, 0.6, 0.2
            
   
            import cairo
            gradient = cairo.LinearGradient(x, height - bar_h, x, height)
            gradient.add_color_stop_rgba(0, r, g, b, 0.9)
            gradient.add_color_stop_rgba(0.7, r * 0.7, g * 0.7, b * 0.7, 0.7)
            gradient.add_color_stop_rgba(1, r * 0.4, g * 0.4, b * 0.4, 0.5)
            
            cr.set_source(gradient)
            cr.rectangle(x, height - bar_h, bar_width, bar_h)
            cr.fill()
            

            cr.set_source_rgba(1, 1, 1, 0.3)
            cr.rectangle(x, height - bar_h, bar_width, 2)
            cr.fill()
        

        cr.set_source_rgba(0.5, 0.5, 0.5, 0.2)
        cr.set_line_width(1)
        cr.rectangle(0.5, 0.5, width - 1, height - 1)
        cr.stroke()
        
        return False

class OplyPlayer(Gtk.Window):
    def __init__(self):
        super().__init__(title="Oply Audio Player")

        self.TEXT = load_language()
        config = load_config()
        self.last_playlist = config.get("last_playlist", "")

        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)


        if os.path.exists(ICON_PATH):
            try:
                self.set_icon_from_file(ICON_PATH)
            except:
                pass


        self.audio_files = []
        self.current_index = 0
        self.is_paused = False
        self.duration = 0
        self.updating_progress = True


        self.mpv_socket = os.path.join(CONFIG_DIR, f"mpv_socket_{os.getpid()}")
        if os.path.exists(self.mpv_socket):
            try:
                os.remove(self.mpv_socket)
            except:
                pass


        self.setup_mpv()


        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = self.TEXT["title"]
        hb.props.subtitle = self.TEXT["subtitle"]
        self.set_titlebar(hb)
        self.headerbar = hb


        btn_add = Gtk.Button()
        btn_add.add(Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON))
        btn_add.set_tooltip_text(self.TEXT["add_files"])
        btn_add.connect("clicked", self.on_add_files)
        hb.pack_start(btn_add)


        btn_folder = Gtk.Button()
        btn_folder.add(Gtk.Image.new_from_icon_name("folder-new-symbolic", Gtk.IconSize.BUTTON))
        btn_folder.set_tooltip_text(self.TEXT["add_folder"])
        btn_folder.connect("clicked", self.on_add_folder)
        hb.pack_start(btn_folder)


        btn_youtube = Gtk.Button()
        btn_youtube.add(Gtk.Image.new_from_icon_name("emblem-downloads-symbolic", Gtk.IconSize.BUTTON))
        btn_youtube.set_tooltip_text(self.TEXT["youtube_download"])
        btn_youtube.connect("clicked", self.on_youtube_convert)
        hb.pack_start(btn_youtube)


        self.menu_button = Gtk.MenuButton()
        self.menu_button.add(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.BUTTON))
        self.create_menu()
        hb.pack_end(self.menu_button)


        self.setup_drag_drop()


        self.setup_ui()


        self.setup_socket_server()


        self.setup_systray()


        GLib.timeout_add(1000, self.update_progress)
        GLib.timeout_add(200, self.update_playback_info)


        self.connect("delete-event", self.on_window_delete)
        self.connect("destroy", self.on_destroy)
        self.show_all()

    def setup_mpv(self):
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
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(0.8)  

    def send_mpv_command(self, command):
        if not hasattr(self, 'mpv') or not os.path.exists(self.mpv_socket):
            return False

        max_retries = 3
        for attempt in range(max_retries):
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(2.0)
                    s.connect(self.mpv_socket)
                    s.sendall(json.dumps(command).encode() + b"\n")
                    return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.2)
                else:
                    print(f"MPV command error after {max_retries} attempts: {e}")
                    return False

        return False

    def setup_systray(self):
        """Configurar systray con AyatanaAppIndicator3"""
        if not APPINDICATOR_AVAILABLE:
            print("Systray not available - AyatanaAppIndicator3 not installed")
            self.indicator = None
            return

        try:
     
            self.indicator = AppIndicator3.Indicator.new(
                "oply-audio-player",
                ICON_PATH if os.path.exists(ICON_PATH) else "audio-x-generic",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.indicator.set_title(self.TEXT["title"])

       
            self.create_systray_menu()
        except Exception as e:
            print(f"Error setting up systray: {e}")
            self.indicator = None

    def create_systray_menu(self):
        """Crear menú del systray"""
        menu = Gtk.Menu()

    
        item_play = Gtk.MenuItem(label=self.TEXT["play_pause"])
        item_play.connect("activate", lambda x: self.toggle_play_pause())
        menu.append(item_play)

     
        item_prev = Gtk.MenuItem(label=self.TEXT["previous"])
        item_prev.connect("activate", lambda x: self.play_previous())
        menu.append(item_prev)

    
        item_next = Gtk.MenuItem(label=self.TEXT["next"])
        item_next.connect("activate", lambda x: self.play_next())
        menu.append(item_next)

        menu.append(Gtk.SeparatorMenuItem())

    
        item_vol = Gtk.MenuItem(label=self.TEXT["volume"] if "volume" in self.TEXT else "Volume")
        vol_submenu = Gtk.Menu()

     
        vol_item = Gtk.MenuItem()
        vol_scale_menu = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        vol_scale_menu.set_value(self.vol_scale.get_value())
        vol_scale_menu.set_size_request(150, -1)
        vol_scale_menu.connect("value-changed", lambda s: self.vol_scale.set_value(s.get_value()))
        vol_item.add(vol_scale_menu)
        vol_submenu.append(vol_item)

        item_vol.set_submenu(vol_submenu)
        menu.append(item_vol)

        menu.append(Gtk.SeparatorMenuItem())

   
        item_show = Gtk.MenuItem(label=self.TEXT["restore"])
        item_show.connect("activate", lambda x: self.restore_window())
        menu.append(item_show)

    
        item_quit = Gtk.MenuItem(label=self.TEXT["exit"])
        item_quit.connect("activate", lambda x: self.quit_application())
        menu.append(item_quit)

        menu.show_all()

        if self.indicator:
            self.indicator.set_menu(menu)

    def on_window_delete(self, widget, event):
        """Manejar cierre de ventana - mostrar diálogo"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text=self.TEXT["close_dialog_title"]
        )
        dialog.format_secondary_text(self.TEXT["close_dialog_message"])

        dialog.add_button(self.TEXT["minimize_to_tray"], Gtk.ResponseType.NO)
        dialog.add_button(self.TEXT["quit_app"], Gtk.ResponseType.YES)

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.NO:
        
            self.hide()
            return True 
        elif response == Gtk.ResponseType.YES:
        
            self.quit_application()
            return False
        else:
        
            return True

    def restore_window(self):
        """Restaurar ventana desde el systray"""
        self.show_all()
        self.present()

    def minimize_to_tray(self):
        """Minimizar a systray"""
        self.hide()

    def quit_application(self):
        """Salir completamente de la aplicación"""
        self.on_destroy(None)

    def setup_drag_drop(self):
        targets = [
            Gtk.TargetEntry.new("text/uri-list", 0, 0),
            Gtk.TargetEntry.new("text/plain", 0, 1)
        ]
        self.drag_dest_set(
            Gtk.DestDefaults.ALL,
            targets,
            Gdk.DragAction.COPY
        )
        self.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uris = data.get_uris()
        if uris:
            for uri in uris:
                path = uri.replace("file://", "")
                import urllib.parse
                path = urllib.parse.unquote(path)

                if os.path.isfile(path):
                    self.audio_files.append(path)
                elif os.path.isdir(path):
                    for fmt in SUPPORTED_FORMATS:
                        self.audio_files.extend(glob.glob(os.path.join(path, fmt)))

            self.refresh_listbox()
            if self.audio_files and not self.is_paused:
                self.play_audio()

    def create_menu(self):
        menu = Gio.Menu()
        menu.append(self.TEXT["save_playlist"], "win.save")
        menu.append(self.TEXT["load_playlist"], "win.load")
        menu.append(self.TEXT["clear"], "win.clear")
        menu.append("About Oply", "win.about")

        self.menu_button.set_menu_model(menu)

    
        action_group = Gio.SimpleActionGroup()

      
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", lambda a, p: self.on_save_playlist(None))
        action_group.add_action(save_action)

        load_action = Gio.SimpleAction.new("load", None)
        load_action.connect("activate", lambda a, p: self.on_load_playlist(None))
        action_group.add_action(load_action)

        clear_action = Gio.SimpleAction.new("clear", None)
        clear_action.connect("activate", lambda a, p: self.on_clear(None))
        action_group.add_action(clear_action)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", lambda a, p: self.show_about())
        action_group.add_action(about_action)

        self.insert_action_group("win", action_group)

    def setup_ui(self):
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

     
        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        content_box.set_margin_start(15)
        content_box.set_margin_end(15)
        content_box.set_margin_top(15)
        main_vbox.pack_start(content_box, True, True, 0)

     
        left_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        left_panel.set_size_request(300, -1)
        content_box.pack_start(left_panel, False, False, 0)

    
        cover_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        cover_box.set_halign(Gtk.Align.CENTER)

        cover_frame = Gtk.Frame()
        cover_frame.set_shadow_type(Gtk.ShadowType.IN)

        self.cover_image = Gtk.Image()
        self.cover_image.set_size_request(280, 280)

      
        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_PATH, 280, 280, True)
                self.cover_image.set_from_pixbuf(pixbuf)
            except:
                self.cover_image.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)
        else:
            self.cover_image.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)

        cover_frame.add(self.cover_image)
        cover_box.pack_start(cover_frame, False, False, 0)
        left_panel.pack_start(cover_box, False, False, 0)

    
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        info_box.set_margin_top(10)

        self.lbl_title = Gtk.Label()
        self.lbl_title.set_markup("<b>Sin reproducción</b>")
        self.lbl_title.set_line_wrap(True)
        self.lbl_title.set_max_width_chars(30)
        self.lbl_title.set_halign(Gtk.Align.CENTER)
        info_box.pack_start(self.lbl_title, False, False, 0)

        self.lbl_artist = Gtk.Label(label="")
        self.lbl_artist.set_halign(Gtk.Align.CENTER)
        self.lbl_artist.get_style_context().add_class("dim-label")
        info_box.pack_start(self.lbl_artist, False, False, 0)

        self.lbl_album = Gtk.Label(label="")
        self.lbl_album.set_halign(Gtk.Align.CENTER)
        self.lbl_album.get_style_context().add_class("dim-label")
        info_box.pack_start(self.lbl_album, False, False, 0)

        left_panel.pack_start(info_box, False, False, 0)

     
        ecualizador_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        ecualizador_box.set_margin_top(15)
        ecualizador_box.set_margin_bottom(15)
        
     
        lbl_eq = Gtk.Label()
        lbl_eq.set_markup("<small>Audio Visualizer</small>")
        lbl_eq.set_halign(Gtk.Align.CENTER)
        lbl_eq.get_style_context().add_class("dim-label")
        ecualizador_box.pack_start(lbl_eq, False, False, 0)
        
      
        self.visualizer = AudioVisualizer()
        ecualizador_box.pack_start(self.visualizer, False, False, 0)
        
        left_panel.pack_start(ecualizador_box, False, False, 0)

    
        left_panel.pack_start(Gtk.Box(), True, True, 0)

  
        credits_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        credits_box.set_margin_bottom(5)

        lbl_credits = Gtk.Label()
        lbl_credits.set_markup("<small>Oply by josejp2424</small>")
        lbl_credits.set_halign(Gtk.Align.CENTER)
        credits_box.pack_start(lbl_credits, False, False, 0)

        lbl_license = Gtk.Label()
        lbl_license.set_markup("<small>License: GPL-3.0</small>")
        lbl_license.set_halign(Gtk.Align.CENTER)
        lbl_license.get_style_context().add_class("dim-label")
        credits_box.pack_start(lbl_license, False, False, 0)

        left_panel.pack_end(credits_box, False, False, 0)

     
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.treeview.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Archivo", renderer, text=0)
        self.treeview.append_column(column)

        self.treeview.connect("row-activated", self.on_row_activated)

        scrolled.add(self.treeview)
        content_box.pack_start(scrolled, True, True, 0)

      
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

      
        btn_prev = Gtk.Button.new_from_icon_name("media-skip-backward-symbolic", Gtk.IconSize.BUTTON)
        btn_prev.connect("clicked", lambda x: self.play_previous())
        controls_hbox.pack_start(btn_prev, False, False, 0)

     
        self.btn_play = Gtk.Button()
        self.btn_play.add(Gtk.Image.new_from_icon_name("media-playback-start-symbolic", Gtk.IconSize.BUTTON))
        self.btn_play.get_style_context().add_class("circular")
        self.btn_play.connect("clicked", lambda x: self.toggle_play_pause())
        controls_hbox.pack_start(self.btn_play, False, False, 0)

       
        btn_next = Gtk.Button.new_from_icon_name("media-skip-forward-symbolic", Gtk.IconSize.BUTTON)
        btn_next.connect("clicked", lambda x: self.play_next())
        controls_hbox.pack_start(btn_next, False, False, 0)

      
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

        self.btn_vol = Gtk.Button()
        self.vol_icon = Gtk.Image.new_from_icon_name("audio-volume-high-symbolic", Gtk.IconSize.BUTTON)
        self.btn_vol.add(self.vol_icon)
        self.btn_vol.connect("clicked", self.toggle_mute)
        right_box.pack_start(self.btn_vol, False, False, 0)

        self.vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.vol_scale.set_value(50)
        self.vol_scale.set_size_request(120, -1)
        self.vol_scale.set_draw_value(False)
        self.vol_scale.connect("value-changed", self.on_volume_changed)
        right_box.pack_start(self.vol_scale, False, False, 0)

       
        self.btn_viz = Gtk.ToggleButton()
        self.btn_viz.add(Gtk.Image.new_from_icon_name("audio-speakers-symbolic", Gtk.IconSize.BUTTON))
        self.btn_viz.set_tooltip_text("Show/Hide Visualizer")
        self.btn_viz.set_active(True)  
        self.btn_viz.connect("toggled", self.toggle_visualizer)
        right_box.pack_start(self.btn_viz, False, False, 5)

    
        self.is_muted = False
        self.volume_before_mute = 50

    def toggle_visualizer(self, button):
        """Mostrar u ocultar el visualizador"""
        if button.get_active():
            self.visualizer.show()
            if not self.is_paused and self.audio_files:
                self.visualizer.start_animation()
        else:
            self.visualizer.hide()
            self.visualizer.stop_animation()

    def show_about(self):
        """Mostrar diálogo About"""
        dialog = Gtk.Dialog(
            title="About Oply",
            transient_for=self,
            modal=True
        )
        dialog.set_default_size(450, 400)

        content = dialog.get_content_area()
        content.set_spacing(15)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(20)
        content.set_margin_end(20)

     
        logo_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        logo_box.set_halign(Gtk.Align.CENTER)

        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_PATH, 128, 128, True)
                logo_image = Gtk.Image.new_from_pixbuf(pixbuf)
            except:
                logo_image = Gtk.Image.new_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)
        else:
            logo_image = Gtk.Image.new_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)

        logo_box.pack_start(logo_image, False, False, 0)
        content.pack_start(logo_box, False, False, 0)

        # Título
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large'><b>Oply Suite</b></span>")
        title_label.set_halign(Gtk.Align.CENTER)
        content.pack_start(title_label, False, False, 0)

        # Versión
        version_label = Gtk.Label()
        version_label.set_markup("<span size='small'>Version 2.1 GTK3</span>")
        version_label.set_halign(Gtk.Align.CENTER)
        version_label.get_style_context().add_class("dim-label")
        content.pack_start(version_label, False, False, 0)

        # Separador
        sep1 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content.pack_start(sep1, False, False, 10)

        # Descripción
        desc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        desc1 = Gtk.Label()
        desc1.set_markup(f"<b>📀 Oply Audio Player</b>\n{self.TEXT['about_audio_desc']}")
        desc1.set_justify(Gtk.Justification.CENTER)
        desc_box.pack_start(desc1, False, False, 0)

        desc2 = Gtk.Label()
        desc2.set_markup(f"<b>🎬 Oply Video Player</b>\n{self.TEXT['about_video_desc']}")
        desc2.set_justify(Gtk.Justification.CENTER)
        desc_box.pack_start(desc2, False, False, 0)

        desc3 = Gtk.Label()
        desc3.set_markup(f"<b>⬇️ Oply Convert</b>\n{self.TEXT['about_convert_desc']}")
        desc3.set_justify(Gtk.Justification.CENTER)
        desc_box.pack_start(desc3, False, False, 0)

        content.pack_start(desc_box, False, False, 0)

        # Separador
        sep2 = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content.pack_start(sep2, False, False, 10)

        # Autor y licencia
        author_label = Gtk.Label()
        author_label.set_markup(f"<b>{self.TEXT['about_created']}</b> josejp2424")
        author_label.set_halign(Gtk.Align.CENTER)
        content.pack_start(author_label, False, False, 0)

        license_label = Gtk.Label()
        license_label.set_markup(f"<b>{self.TEXT['about_license']}</b> GNU General Public License v3.0")
        license_label.set_halign(Gtk.Align.CENTER)
        content.pack_start(license_label, False, False, 0)

        # Copyright
        copyright_label = Gtk.Label()
        copyright_label.set_markup("<small>Copyright © 2024 josejp2424\nAll rights reserved</small>")
        copyright_label.set_halign(Gtk.Align.CENTER)
        copyright_label.get_style_context().add_class("dim-label")
        content.pack_start(copyright_label, False, False, 0)


        dialog.add_button(self.TEXT["about_close"], Gtk.ResponseType.CLOSE)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def refresh_listbox(self):
        self.liststore.clear()
        for filepath in self.audio_files:
            self.liststore.append([os.path.basename(filepath)])

    def on_add_files(self, button):
        dialog = Gtk.FileChooserDialog(
            title=self.TEXT["add_files"],
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        dialog.set_select_multiple(True)

        filter_audio = Gtk.FileFilter()
        filter_audio.set_name("Audio")
        filter_audio.add_mime_type("audio/*")
        dialog.add_filter(filter_audio)


        def on_file_activated(widget):
            dialog.response(Gtk.ResponseType.OK)

        dialog.connect("file-activated", on_file_activated)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()
            was_empty = len(self.audio_files) == 0
            self.audio_files.extend(filenames)
            self.refresh_listbox()

    
            if was_empty and self.audio_files:
                GLib.timeout_add(100, lambda: (self.play_audio(), False))

        dialog.destroy()

    def on_add_folder(self, button):
        dialog = Gtk.FileChooserDialog(
            title=self.TEXT["add_folder"],
            parent=self,
            action=Gtk.FileChooserAction.OPEN  
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        dialog.set_select_multiple(True)  

 
        filter_audio = Gtk.FileFilter()
        filter_audio.set_name("Audio y Carpetas")
        filter_audio.add_mime_type("audio/*")
        filter_audio.add_mime_type("inode/directory")
        dialog.add_filter(filter_audio)

     
        def on_file_activated(widget):
           
            filename = dialog.get_filename()
            if filename and os.path.isfile(filename):
               
                was_empty = len(self.audio_files) == 0
                self.audio_files.append(filename)
                self.refresh_listbox()
                dialog.destroy()

          
                if was_empty:
                    self.current_index = 0
                else:
                    self.current_index = len(self.audio_files) - 1

                GLib.timeout_add(100, lambda: (self.play_audio(), False))
                return
            else:
              
                dialog.response(Gtk.ResponseType.OK)

        dialog.connect("file-activated", on_file_activated)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filenames = dialog.get_filenames()
            was_empty = len(self.audio_files) == 0
            files_added = 0

            for filename in filenames:
                if os.path.isfile(filename):
          
                    self.audio_files.append(filename)
                    files_added += 1
                elif os.path.isdir(filename):
                
                    for fmt in SUPPORTED_FORMATS:
                        found_files = glob.glob(os.path.join(filename, fmt))
                        self.audio_files.extend(found_files)
                        files_added += len(found_files)

            self.refresh_listbox()

        
            if was_empty and files_added > 0:
                GLib.timeout_add(100, lambda: (self.play_audio(), False))

        dialog.destroy()

    def on_youtube_convert(self, button):
        """Abrir Oply-Convert para descargar música/video de YouTube"""
        try:
         
            subprocess.Popen(["/usr/local/Oply/Oply-Convert"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        except Exception as e:
      
            dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error al abrir Oply-Convert"
            )
            dialog.format_secondary_text(f"No se pudo abrir Oply-Convert: {str(e)}")
            dialog.run()
            dialog.destroy()

    def on_save_playlist(self, button):
        if not self.audio_files:
            return

        os.makedirs(PLAYLISTS_DIR, exist_ok=True)

        dialog = Gtk.FileChooserDialog(
            title=self.TEXT["save_playlist"],
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_current_folder(PLAYLISTS_DIR)
        dialog.set_current_name("playlist.opl")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                with open(filename, 'w') as f:
                    json.dump({
                        "files": self.audio_files,
                        "current_index": self.current_index
                    }, f)
                self.last_playlist = filename
                save_config(self.last_playlist)
            except Exception as e:
                print(f"Error saving playlist: {e}")

        dialog.destroy()

    def on_load_playlist(self, button):
        dialog = Gtk.FileChooserDialog(
            title=self.TEXT["load_playlist"],
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        dialog.set_current_folder(PLAYLISTS_DIR)

        filter_opl = Gtk.FileFilter()
        filter_opl.set_name("Oply Playlists")
        filter_opl.add_pattern("*.opl")
        dialog.add_filter(filter_opl)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)

                self.audio_files = [f for f in data.get("files", []) if os.path.exists(f)]
                self.current_index = data.get("current_index", 0)
                self.last_playlist = filename
                save_config(self.last_playlist)

                self.refresh_listbox()

                if self.audio_files:
                    self.play_audio()
            except Exception as e:
                print(f"Error loading playlist: {e}")

        dialog.destroy()

    def on_clear(self, button):
        if not self.audio_files:
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.TEXT["clear"]
        )
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.stop_audio()
            self.audio_files = []
            self.current_index = 0
            self.refresh_listbox()

    def on_row_activated(self, treeview, path, column):
        index = path.get_indices()[0]
        self.current_index = index
        self.play_audio()

    def on_progress_press(self, widget, event):
        self.updating_progress = False

    def on_progress_release(self, widget, event):
        try:
            value = self.progress_scale.get_value()
            if self.duration:
                target = (value / 100) * self.duration
                self.send_mpv_command({"command": ["seek", str(target), "absolute"]})
        except:
            pass
        finally:
            self.updating_progress = True

    def seek_relative(self, seconds):
        try:
            self.send_mpv_command({"command": ["seek", str(seconds), "relative"]})
        except:
            pass

    def on_volume_changed(self, scale):
        volume = scale.get_value()
        self.send_mpv_command({"command": ["set_property", "volume", volume]})

      
        if volume == 0:
            icon_name = "audio-volume-muted-symbolic"
            self.is_muted = True
        elif volume < 33:
            icon_name = "audio-volume-low-symbolic"
            self.is_muted = False
        elif volume < 66:
            icon_name = "audio-volume-medium-symbolic"
            self.is_muted = False
        else:
            icon_name = "audio-volume-high-symbolic"
            self.is_muted = False

        self.vol_icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)


        if self.indicator:
            tooltip = f"{self.TEXT['title']} - Volume: {int(volume)}%"
            if hasattr(self, 'headerbar') and self.headerbar.props.subtitle:
                tooltip = f"{self.headerbar.props.subtitle} - Vol: {int(volume)}%"

    def toggle_mute(self, button):
        """Alternar mute/unmute"""
        if self.is_muted:
        
            self.vol_scale.set_value(self.volume_before_mute)
            self.is_muted = False
        else:
          
            self.volume_before_mute = self.vol_scale.get_value()
            self.vol_scale.set_value(0)
            self.is_muted = True

    def update_cover_art(self, filepath):
        """Actualizar carátula del álbum"""
        os.makedirs(CONFIG_DIR, exist_ok=True)

        cover_base = os.path.join(CONFIG_DIR, "current_cover")

     
        for ext in ("jpg", "png"):
            p = f"{cover_base}.{ext}"
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass


        print(f"Extrayendo carátula de: {filepath}")
        ok, cover_path = extract_cover_art(filepath, cover_base)
        if ok and cover_path:
            print(f"Carátula extraída: {cover_path}")
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(cover_path, 280, 280, True)
                self.cover_image.set_from_pixbuf(pixbuf)
                print("Carátula mostrada correctamente")
                return
            except Exception as e:
                print(f"Error mostrando carátula: {e}")

      
        folder = os.path.dirname(filepath)
        candidates = [
            "cover.jpg", "folder.jpg", "front.jpg", "album.jpg",
            "Cover.jpg", "Folder.jpg", "Front.jpg", "Album.jpg",
            "cover.png", "folder.png", "front.png", "album.png",
            "Cover.png", "Folder.png", "Front.png", "Album.png",
        ]
        for name in candidates:
            p = os.path.join(folder, name)
            if os.path.exists(p) and os.path.getsize(p) > 0:
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(p, 280, 280, True)
                    self.cover_image.set_from_pixbuf(pixbuf)
                    print(f"Carátula tomada de carpeta: {p}")
                    return
                except:
                    pass

      
        metadata = get_metadata(filepath)
        if metadata["artist"] and metadata["album"]:
            print(f"Buscando online: {metadata['artist']} - {metadata['album']}")
            threading.Thread(
                target=self.search_cover_online,
                args=(metadata["artist"], metadata["album"]),
                daemon=True
            ).start()
        else:
            print("Sin metadata de artista/álbum, mostrando logo por defecto")
            self.show_default_cover()

    def search_cover_online(self, artist, album):
        """Buscar carátula en internet usando iTunes API"""
        try:
            import urllib.request
            import urllib.parse

          
            query = urllib.parse.quote(f"{artist} {album}")
            url = f"https://itunes.apple.com/search?term={query}&media=music&entity=album&limit=1"

            print(f"Buscando en iTunes API: {url}")

            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())

                if data.get("resultCount", 0) > 0:
                    artwork_url = data["results"][0].get("artworkUrl100", "").replace("100x100", "600x600")

                    if artwork_url:
                        print(f"Carátula encontrada: {artwork_url}")
                        cover_path = os.path.join(CONFIG_DIR, "current_cover.jpg")
                        urllib.request.urlretrieve(artwork_url, cover_path)

                   
                        GLib.idle_add(self.load_cover_from_file, cover_path)
                        return
                else:
                    print("No se encontraron resultados en iTunes")
        except Exception as e:
            print(f"Error buscando online: {e}")


        print("Mostrando logo por defecto")
        GLib.idle_add(self.show_default_cover)

    def load_cover_from_file(self, filepath):
        """Cargar carátula desde archivo"""
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filepath, 280, 280, True)
            self.cover_image.set_from_pixbuf(pixbuf)
        except:
            self.show_default_cover()
        return False

    def show_default_cover(self):
        """Mostrar logo de Oply por defecto"""
        if os.path.exists(ICON_PATH):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(ICON_PATH, 280, 280, True)
                self.cover_image.set_from_pixbuf(pixbuf)
            except:
                self.cover_image.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)
        else:
            self.cover_image.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)
        return False

    def play_audio(self):
        if not self.audio_files or self.current_index >= len(self.audio_files):
            return

        filepath = self.audio_files[self.current_index]

    
        metadata = get_metadata(filepath)
        self.duration = metadata["duration"]

    
        self.update_cover_art(filepath)

    
        title = metadata["title"] if metadata["title"] else os.path.basename(filepath)
        self.lbl_title.set_markup(f"<b>{title}</b>")

        if metadata["artist"]:
            self.lbl_artist.set_text(metadata["artist"])
            self.lbl_artist.show()
        else:
            self.lbl_artist.hide()

        if metadata["album"]:
            self.lbl_album.set_text(metadata["album"])
            self.lbl_album.show()
        else:
            self.lbl_album.hide()

    
        self.send_mpv_command({"command": ["loadfile", filepath]})

     
        GLib.timeout_add(200, self.ensure_playback)

        self.is_paused = False

    
        if hasattr(self, 'visualizer'):
            self.visualizer.start_animation()

   
        subtitle_text = f"{self.TEXT['playing']}: {title}"
        if metadata["artist"]:
            subtitle_text = f"{metadata['artist']} - {title}"
        self.headerbar.props.subtitle = subtitle_text
        
      
        update_now_playing(
            title=title,
            artist=metadata.get("artist", ""),
            is_playing=True
        )

    def ensure_playback(self):
        """Asegurar que la reproducción inicie"""
        self.send_mpv_command({"command": ["set_property", "pause", False]})
        return False

    def stop_audio(self):
        self.send_mpv_command({"command": ["stop"]})
        self.is_paused = False
        self.duration = 0
        self.headerbar.props.subtitle = self.TEXT["subtitle"]
        
    
        if hasattr(self, 'visualizer'):
            self.visualizer.stop_animation()
        
      
        clear_now_playing()

    def toggle_play_pause(self):
        self.send_mpv_command({"command": ["cycle", "pause"]})
        self.is_paused = not self.is_paused
        
      
        if hasattr(self, 'visualizer'):
            if self.is_paused:
                self.visualizer.stop_animation()
            else:
                self.visualizer.start_animation()
        

        if self.audio_files and self.current_index < len(self.audio_files):
            filepath = self.audio_files[self.current_index]
            metadata = get_metadata(filepath)
            title = metadata["title"] if metadata["title"] else os.path.basename(filepath)
            update_now_playing(
                title=title,
                artist=metadata.get("artist", ""),
                is_playing=not self.is_paused
            )

    def play_next(self):
        if not self.audio_files:
            return
        self.current_index = (self.current_index + 1) % len(self.audio_files)
        self.play_audio()

    def play_previous(self):
        if not self.audio_files:
            return
        self.current_index = (self.current_index - 1) % len(self.audio_files)
        self.play_audio()

    def update_progress(self):
        try:
            if self.duration and self.updating_progress:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.settimeout(0.5)
                    s.connect(self.mpv_socket)

                    s.sendall(b'{ "command": ["get_property", "time-pos"] }\n')
                    pos_resp = s.recv(1024).decode()
                    pos_data = json.loads(pos_resp)
                    position = pos_data.get('data', 0) or 0

                    progress = (position / self.duration) * 100 if self.duration else 0
                    self.progress_scale.set_value(progress)

                    elapsed_str = format_duration(position)
                    total_str = format_duration(self.duration)
                    self.lbl_time.set_text(f"{elapsed_str} / {total_str}")
        except:
            pass

        return True

    def update_playback_info(self):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect(self.mpv_socket)

                s.sendall(b'{ "command": ["get_property", "time-pos"] }\n')
                pos_resp = s.recv(1024).decode()
                pos_data = json.loads(pos_resp)
                position = pos_data.get('data', 0) or 0

                s.sendall(b'{ "command": ["get_property", "duration"] }\n')
                dur_resp = s.recv(1024).decode()
                dur_data = json.loads(dur_resp)
                duration = dur_data.get('data', 1) or 1

           
                if position and duration and position >= duration - 0.5:
                    self.play_next()
        except:
            pass

        return True

    def setup_socket_server(self):
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except:
                pass

        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.bind(SOCKET_PATH)
            self.sock.listen(1)
            threading.Thread(target=self.listen_socket, daemon=True).start()
        except Exception as e:
            print(f"Socket server error: {e}")

    def listen_socket(self):
        while True:
            try:
                conn, _ = self.sock.accept()
                data = conn.recv(1024)
                if data:
                    command = data.decode().strip()
                    if command.startswith("PLAY:"):
                        filepath = command[5:]
                        if os.path.exists(filepath):
                            GLib.idle_add(self.play_external_file, filepath)
                    elif command.startswith("ADD:"):
                        filepath = command[4:]
                        if os.path.exists(filepath):
                            GLib.idle_add(self.add_to_playlist, filepath)
                conn.close()
            except:
                break

    def play_external_file(self, filepath):
        self.audio_files = [filepath]
        self.current_index = 0
        self.refresh_listbox()
        GLib.timeout_add(100, lambda: (self.play_audio(), False))

    def add_to_playlist(self, filepath):
        self.audio_files.append(filepath)
        self.refresh_listbox()

    def on_destroy(self, widget):
      
        if hasattr(self, 'mpv') and self.mpv:
            self.mpv.terminate()
            try:
                self.mpv.wait(timeout=1)
            except:
                self.mpv.kill()

   
        if hasattr(self, 'visualizer'):
            self.visualizer.stop_animation()

    
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except:
                pass

        if hasattr(self, 'mpv_socket') and os.path.exists(self.mpv_socket):
            try:
                os.remove(self.mpv_socket)
            except:
                pass

     
        if hasattr(self, 'indicator') and self.indicator and APPINDICATOR_AVAILABLE:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
        
      
        clear_now_playing()

        Gtk.main_quit()

def send_to_socket(filepath, action="PLAY"):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(SOCKET_PATH)
        s.send(f"{action}:{filepath}".encode())
        s.close()
        return True
    except:
        return False

def main():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(PLAYLISTS_DIR, exist_ok=True)

    play_on_start = None
    add_on_start = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "--add" and len(sys.argv) > 2:
            if send_to_socket(sys.argv[2], "ADD"):
                sys.exit(0)
            else:
                add_on_start = os.path.abspath(sys.argv[2])
        else:
            if send_to_socket(sys.argv[1], "PLAY"):
                sys.exit(0)
            else:
                play_on_start = os.path.abspath(sys.argv[1])

    app = OplyPlayer()

    if play_on_start:
        app.play_external_file(play_on_start)
    elif add_on_start:
        app.add_to_playlist(add_on_start)

    Gtk.main()

if __name__ == "__main__":
    main()
