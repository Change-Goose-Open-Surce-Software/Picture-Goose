#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Picture Goose - Settings
Programmeinstellungen verwalten (Ohne Pygame, Korrigierte Logik)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os
import platform
import subprocess

class SettingsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Picture Goose - Settings")
        
        # Pfade
        self.home = Path.home()
        self.base_path = self.home / ".picture-goose"
        self.safes_path = self.base_path / "safes"
        self.materials_path = self.base_path / "materials"
        self.colors_path = self.safes_path / "colors"
        
        # Einstellungen und Farben laden
        self.load_all_settings()
        self.load_colors()
        
        # Fenster-Modus setzen
        self.set_window_mode()
        
        # GUI aufbauen und Farben anwenden
        self.setup_gui()
        self.apply_initial_colors()

    def get_hex_color(self, color_name, kontrast):
        """Konvertiert Farbnamen zu Hex-Werten"""
        color_map = {
            "schwarz": {"dunkel": "#000000", "hell": "#404040"},
            "weiß": {"dunkel": "#c0c0c0", "hell": "#ffffff"},
            "blau": {"dunkel": "#000080", "hell": "#0000ff"},
            "lila": {"dunkel": "#4b0082", "hell": "#9370db"},
            "pink": {"dunkel": "#c71585", "hell": "#ff69b4"},
            "rot": {"dunkel": "#8b0000", "hell": "#ff0000"},
            "grau": {"dunkel": "#404040", "hell": "#808080"},
            "gelb": {"dunkel": "#808000", "hell": "#ffff00"},
            "green": {"dunkel": "#006400", "hell": "#00ff00"}
        }
        return color_map.get(color_name.lower(), {}).get(kontrast, "#2a2a2a")

    def load_colors(self):
        """Korrigiert: Lädt Hintergrund- und Schriftfarbe aus den Textdateien."""
        self.bg_color = "#2a2a2a"
        self.text_color = "#00ff00"
        
        for color_type in ["background", "writing"]:
            filepath = self.colors_path / f"{color_type}.txt"
            if not filepath.exists():
                continue
                
            try:
                with open(filepath, 'r') as f:
                    lines = [l.strip().lower() for l in f.readlines() if l.strip()]
                
                i = 0
                while i < len(lines):
                    if lines[i] == "color" and i + 1 < len(lines):
                        color_name = lines[i + 1]
                        kontrast = "dunkel" if color_type == "background" else "hell"
                        
                        if i + 3 < len(lines) and lines[i + 2] == "kontrast":
                            kontrast = lines[i + 3]
                            i += 4
                        else:
                            i += 2
                            
                        hex_color = self.get_hex_color(color_name, kontrast)
                        
                        if color_type == "background":
                            self.bg_color = hex_color
                        else:
                            self.text_color = hex_color
                        break 
                    else:
                        i += 1
            except Exception as e:
                print(f"Fehler beim Laden der Farbe aus {filepath}: {e}")

    def apply_initial_colors(self):
        """Wendet die geladenen Farben auf alle Widgets an."""
        self.root.configure(bg=self.bg_color)
        
        def apply_recursively(widget):
            try:
                widget.config(bg=self.bg_color, fg=self.text_color)
            except tk.TclError:
                pass 
            
            for child in widget.winfo_children():
                apply_recursively(child)
        
        apply_recursively(self.root)

    def load_all_settings(self):
        """Läd alle Einstellungen (Originaler Inhalt)"""
        # Sprache
        lang_file = self.safes_path / "language.txt"
        self.language = "English"
        if lang_file.exists():
            with open(lang_file, 'r') as f:
                self.language = f.read().strip()
        
        # Fenster-Modi
        self.window_modes = {"main.py": "fenster", "keyboard.py": "fenster", "settings.py": "fenster"}
        window_file = self.safes_path / "window.txt"
        if window_file.exists():
            with open(window_file, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    parts = line.strip().split(':')
                    if len(parts) == 2:
                        self.window_modes[parts[0].strip()] = parts[1].strip()

    def set_window_mode(self):
        """Setzt den Fenstermodus für settings.py"""
        mode = self.window_modes.get("settings.py", "fenster")
        if mode == "vollbild":
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry("800x600")

    def setup_gui(self):
        """Erstellt die GUI (Originaler Inhalt)"""
        self.root.configure(bg=self.bg_color)
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sprache
        lang_frame = tk.Frame(main_frame, bg=self.bg_color)
        lang_frame.pack(pady=10, fill='x')
        
        tk.Label(lang_frame, text="Sprache:", font=("Courier", 12), bg=self.bg_color, fg=self.text_color).pack(side="left", padx=10)
        
        self.language_var = tk.StringVar(value=self.language)
        
        lang_options = ["Deutsch", "English"]
        lang_menu = ttk.Combobox(lang_frame, textvariable=self.language_var, values=lang_options, state="readonly")
        lang_menu.pack(side="left", padx=10)
        lang_menu.bind("<<ComboboxSelected>>", self.save_language)
        
        # Fenster-Modi
        mode_frame = tk.Frame(main_frame, bg=self.bg_color)
        mode_frame.pack(pady=10, fill='x')
        
        tk.Label(mode_frame, text="Fenstermodus:", font=("Courier", 12), bg=self.bg_color, fg=self.text_color).pack(side="left", padx=10)
        
        self.mode_vars = {}
        modes = ["fenster", "vollbild"]
        
        for name in ["main.py", "keyboard.py", "settings.py"]:
            frame = tk.Frame(mode_frame, bg=self.bg_color)
            frame.pack(side="left", padx=15)
            
            tk.Label(frame, text=name, bg=self.bg_color, fg=self.text_color).pack(side="left")
            
            self.mode_vars[name] = tk.StringVar(value=self.window_modes.get(name, "fenster"))
            
            for mode in modes:
                tk.Radiobutton(
                    frame,
                    text=mode,
                    variable=self.mode_vars[name],
                    value=mode,
                    command=lambda n=name: self.save_window_mode(n),
                    bg=self.bg_color,
                    fg=self.text_color,
                    selectcolor=self.bg_color
                ).pack(side="left")

    def save_language(self, event=None):
        """Speichert die gewählte Sprache."""
        self.language = self.language_var.get()
        lang_file = self.safes_path / "language.txt"
        with open(lang_file, 'w') as f:
            f.write(self.language)

    def save_window_mode(self, name):
        """Speichert den gewählten Fenstermodus."""
        self.window_modes[name] = self.mode_vars[name].get()
        window_file = self.safes_path / "window.txt"
        
        # Schreibe alle Modi neu
        with open(window_file, 'w') as f:
            for n, mode in self.window_modes.items():
                f.write(f"{n}: {mode}\n")

    def play_sound(self, sound_file):
        """Sound-Funktion ist jetzt nur ein Platzhalter."""
        pass # Stumme Funktion, da Pygame entfernt wurde

if __name__ == "__main__":
    root = tk.Tk()
    app = SettingsWindow(root)
    root.mainloop()
