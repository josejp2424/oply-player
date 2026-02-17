#!/usr/bin/env python3
"""
Script auxiliar para Oply - Exporta el estado actual para Conky
Uso: python3 oply_status.py
Salida: Información de reproducción actual o vacío si no hay nada
"""

import json
import os
import sys

# Archivo donde Oply 
STATE_FILE = os.path.expanduser("~/.config/oply/now_playing.json")

def get_oply_status():
    """Lee el estado actual de Oply"""
    try:
        if not os.path.exists(STATE_FILE):
            return None
            
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not data.get('is_playing', False):
            return None
            
        return data
    except Exception as e:
        return None

def format_for_conky(data):
    """Formatea la información para mostrar en Conky"""
    if not data:
        return ""
    
    title = data.get('title', 'Desconocido')
    artist = data.get('artist', '')
    
    # Limitar longitud para que quepa en Conky
    if len(title) > 35:
        title = title[:32] + "..."
    if len(artist) > 35:
        artist = artist[:32] + "..."
    
    output = "${voffset 5}${font Roboto:size=10,weight=bold}${color2}♪ OPLY${color}${font}${hr 2}\n"
    output += f"${{voffset 5}}${{color1}}Reproduciendo:${{color}}\n"
    output += f"${{offset 10}}${{font Roboto Condensed:size=10}}{title}${{font}}\n"
    
    if artist:
        output += f"${{offset 10}}${{font Roboto Condensed:size=8}}${{color2}}{artist}${{color}}${{font}}\n"
    
    return output

if __name__ == "__main__":
    data = get_oply_status()
    output = format_for_conky(data)
    print(output, end='')
