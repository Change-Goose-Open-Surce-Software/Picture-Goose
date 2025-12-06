#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Picture Goose - Keyboard Settings
Tastenbelegung verwalten - VERBESSERTE VERSION
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess
import platform
import sys

class KeyboardSettings:
    def __init__(self, root):
        self.root = root
        self.root.title("Picture Goose - Keyboard")
        
        # Pfade
        self.home = Path.home()
        self.base_path = self.home / ".picture-goose"
        self.key_path = self.base_path / "safes" / "key"
        self.materials_path = self.base_path / "materials"
        self.safes_path = self.base_path / "safes"
        
        # Einstellungen laden
        self.load_settings()
        self.load_keys()
        
        # Fenster-Modus setzen
        self.set_window_mode()
        
        # GUI aufbauen
        self.setup_gui()
        
        # Tastenbindungen setzen
        self.bind_keys()
    
    def load_settings(self):
        """Lädt Farbeinstellungen"""
        bg_file = self.safes_path / "colors" / "background.txt"
        self.bg_color = "#2a2a2a"
        self.text_color = "#00ff00"
        
        if bg_file.exists():
            with open(bg_file, 'r') as f:
                lines = [l.strip() for l in f.readlines()]
            for i, line in enumerate(lines):
                if line == "color" and i + 1 < len(lines):
                    color_name = lines[i + 1]
                    kontrast = "dunkel"
                    if i + 3 < len(lines) and lines[i + 2] == "kontrast":
                        kontrast = lines[i + 3]
                    self.bg_color = self.get_hex_color(color_name, kontrast)
                    break
        
        text_file = self.safes_path / "colors" / "writing.txt"
        if text_file.exists():
            with open(text_file, 'r') as f:
                lines = [l.strip() for l in f.readlines()]
            for i, line in enumerate(lines):
                if line == "color" and i + 1 < len(lines):
                    color_name = lines[i + 1]
                    kontrast = "hell"
                    if i + 3 < len(lines) and lines[i + 2] == "kontrast":
                        kontrast = lines[i + 3]
                    self.text_color = self.get_hex_color(color_name, kontrast)
                    break
    
    def get_hex_color(self, color_name, kontrast):
        """Konvertiert Farbnamen zu Hex"""
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
    
    def load_keys(self):
        """Lädt ALLE Tastenbelegungen"""
        self.keys = {
            "keyboard": "k",
            "settings": "s",
            "main": "m",
            "close": "c",
            "accept": "a",
            "delete": "n",
            "update": "u",
            "info": "i",
            # main.py Funktionen
            "scan": "f",
            "crop": "z",
            "scale": "g",
            "rotate": "r",
            "remove": "e",
            "lots": "shift",
            "bit": "ctrl",
            # Neue Funktionen
            "find": "h",
            "rename": "u",
            "gimp": "g",
            "blacklist": "b"
        }
        
        key_files = {
            "keyboard": "keyboard.txt",
            "settings": "settings.txt",
            "main": "main.txt",
            "close": "close.txt",
            "accept": "accept.txt",
            "delete": "delite.txt",
            "update": "update.txt",
            "info": "info.txt",
            "scan": "scan.txt",
            "crop": "cut.txt",
            "scale": "skalieren.txt",
            "rotate": "rotate.txt",
            "remove": "remove.txt",
            "lots": "lots.txt",
            "bit": "bit.txt",
            "find": "find.txt",
            "rename": "rename.txt",
            "gimp": "gimp.txt",
            "blacklist": "blacklist.txt"
        }
        
        # Verzeichnis erstellen falls nicht vorhanden
        self.key_path.mkdir(parents=True, exist_ok=True)
        
        for key_name, file_name in key_files.items():
            key_file = self.key_path / file_name
            if key_file.exists():
                with open(key_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.keys[key_name] = content.lower()
            else:
                # Erstelle Standard-Datei
                with open(key_file, 'w') as f:
                    f.write(self.keys[key_name])
    
    def set_window_mode(self):
        """Setzt Fenstermodus"""
        window_file = self.safes_path / "window.txt"
        mode = "fenster"
        
        if window_file.exists():
            with open(window_file, 'r') as f:
                lines = [l.strip() for l in f.readlines()]
            
            for i, line in enumerate(lines):
                if line == "keyboard.py" and i + 1 < len(lines):
                    mode = lines[i + 1]
                    break
        
        if mode == "vollbild":
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry("900x700")
    
    def setup_gui(self):
        """Erstellt GUI im Retro-Stil"""
        self.root.configure(bg=self.bg_color)
        
        main_frame = tk.Frame(self.root, bg=self.bg_color, bd=5, relief="ridge")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_frame = tk.Frame(main_frame, bg=self.bg_color, bd=3, relief="raised")
        title_frame.pack(fill="x", padx=5, pady=5)
        
        title_label = tk.Label(
            title_frame,
            text="╔══ KEYBOARD SETTINGS ══╗",
            font=("Courier", 20, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack(pady=10)
        
        # Canvas mit Scrollbar
        canvas = tk.Canvas(main_frame, bg=self.bg_color)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5)
        scrollbar.pack(side="right", fill="y")
        
        # Kategorien
        self.create_category(scrollable_frame, "SYSTEM", [
            ("keyboard", "Keyboard Fenster öffnen"),
            ("settings", "Settings Fenster öffnen"),
            ("main", "Main Fenster öffnen"),
            ("close", "ALLE Programme beenden"),
            ("info", "README öffnen")
        ])
        
        self.create_category(scrollable_frame, "BILDBEARBEITUNG", [
            ("scan", "Bilder scannen"),
            ("crop", "Bild schneiden"),
            ("scale", "Bild skalieren"),
            ("rotate", "Bild rotieren"),
            ("remove", "Bild löschen"),
            ("gimp", "In GIMP öffnen")
        ])
        
        self.create_category(scrollable_frame, "VERWALTUNG", [
            ("find", "Bilder suchen"),
            ("rename", "Bild umbenennen"),
            ("blacklist", "Pfad auf Blacklist"),
            ("lots", "Mehrfachauswahl (Bereich)"),
            ("bit", "Mehrfachauswahl (einzeln)")
        ])
        
        # Status-Label
        self.status_label = tk.Label(
            main_frame,
            text="Drücke eine Taste für Aktionen...",
            font=("Courier", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.status_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="💾 SPEICHERN",
            font=("Courier", 12, "bold"),
            bg="#004400",
            fg=self.text_color,
            command=self.save_keys,
            relief="raised",
            bd=3
        ).pack(side="left", padx=10)
        
        tk.Button(
            button_frame,
            text="↻ ZURÜCKSETZEN",
            font=("Courier", 12, "bold"),
            bg="#8b0000",
            fg=self.text_color,
            command=self.reset_keys,
            relief="raised",
            bd=3
        ).pack(side="left", padx=10)
    
    def create_category(self, parent, title, keys):
        """Erstellt eine Kategorie mit Tasten"""
        category_frame = tk.Frame(parent, bg=self.bg_color, bd=2, relief="groove")
        category_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            category_frame,
            text=f"┌─ {title} ─┐",
            font=("Courier", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=5)
        
        if not hasattr(self, 'key_labels'):
            self.key_labels = {}
        
        for key_name, description in keys:
            row_frame = tk.Frame(category_frame, bg=self.bg_color)
            row_frame.pack(fill="x", padx=10, pady=5)
            
            desc_label = tk.Label(
                row_frame,
                text=f"{description}:",
                font=("Courier", 10),
                bg=self.bg_color,
                fg=self.text_color,
                width=30,
                anchor="w"
            )
            desc_label.pack(side="left")
            
            key_label = tk.Label(
                row_frame,
                text=f"[{self.keys[key_name].upper()}]",
                font=("Courier", 12, "bold"),
                bg="#004400",
                fg=self.text_color,
                width=8,
                relief="raised",
                bd=3
            )
            key_label.pack(side="left", padx=10)
            self.key_labels[key_name] = key_label
            
            edit_btn = tk.Button(
                row_frame,
                text="✎ ÄNDERN",
                font=("Courier", 9, "bold"),
                bg="#000080",
                fg=self.text_color,
                command=lambda k=key_name: self.edit_key(k),
                relief="raised",
                bd=2
            )
            edit_btn.pack(side="left", padx=5)
    
    def edit_key(self, key_name):
        """Öffnet Dialog zum Ändern einer Taste"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Taste ändern: {key_name}")
        edit_window.geometry("400x200")
        edit_window.configure(bg=self.bg_color)
        
        tk.Label(
            edit_window,
            text=f"Neue Taste für '{key_name}':",
            font=("Courier", 12),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=20)
        
        entry = tk.Entry(edit_window, font=("Courier", 14), width=10)
        entry.pack(pady=10)
        entry.insert(0, self.keys[key_name])
        entry.focus()
        
        def save_new_key():
            new_key = entry.get().strip().lower()
            if new_key:
                self.keys[key_name] = new_key
                self.key_labels[key_name].config(text=f"[{new_key.upper()}]")
                self.play_sound("good.mp3")
                edit_window.destroy()
        
        tk.Button(
            edit_window,
            text="✓ SPEICHERN",
            font=("Courier", 12, "bold"),
            bg="#004400",
            fg=self.text_color,
            command=save_new_key
        ).pack(pady=10)
        
        entry.bind('<Return>', lambda e: save_new_key())
    
    def save_keys(self):
        """Speichert ALLE Tastenbelegungen"""
        try:
            key_files = {
                "keyboard": "keyboard.txt",
                "settings": "settings.txt",
                "main": "main.txt",
                "close": "close.txt",
                "accept": "accept.txt",
                "delete": "delite.txt",
                "update": "update.txt",
                "info": "info.txt",
                "scan": "scan.txt",
                "crop": "cut.txt",
                "scale": "skalieren.txt",
                "rotate": "rotate.txt",
                "remove": "remove.txt",
                "lots": "lots.txt",
                "bit": "bit.txt",
                "find": "find.txt",
                "rename": "rename.txt",
                "gimp": "gimp.txt",
                "blacklist": "blacklist.txt"
            }
            
            for key_name, file_name in key_files.items():
                key_file = self.key_path / file_name
                with open(key_file, 'w') as f:
                    f.write(self.keys[key_name])
            
            self.play_sound("good.mp3")
            self.status_label.config(text="✓ Tastenbelegung gespeichert!")
        except Exception as e:
            self.play_sound("failed.mp3")
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen:\n{str(e)}")
    
    def reset_keys(self):
        """Setzt Tasten auf Standard zurück"""
        if messagebox.askyesno("Zurücksetzen", "Tastenbelegung auf Standard zurücksetzen?"):
            self.keys = {
                "keyboard": "k", "settings": "s", "main": "m",
                "close": "c", "accept": "a", "delete": "n",
                "update": "u", "info": "i", "scan": "f",
                "crop": "z", "scale": "g", "rotate": "r",
                "remove": "e", "lots": "shift", "bit": "ctrl",
                "find": "h", "rename": "u", "gimp": "g",
                "blacklist": "b"
            }
            
            for key_name, key_label in self.key_labels.items():
                key_label.config(text=f"[{self.keys[key_name].upper()}]")
            
            self.play_sound("default.mp3")
            self.status_label.config(text="↻ Standard-Tasten wiederhergestellt")
    
    def bind_keys(self):
        """Bindet Tasten an Funktionen"""
        for key_name, key in self.keys.items():
            # Spezialbehandlung für Shift und Ctrl
            if key in ["shift", "ctrl"]:
                continue
            self.root.bind(f'<{key}>', lambda e, kn=key_name: self.handle_keypress(kn))
    
    def handle_keypress(self, key_name):
        """Behandelt Tastendruck"""
        self.status_label.config(text=f"▶ Taste '{key_name}' gedrückt [{self.keys[key_name].upper()}]")
        
        if key_name == "close":
            self.close_all_programs()
        elif key_name == "info":
            self.open_readme()
        elif key_name in ["keyboard", "settings", "main"]:
            self.open_module(key_name)
    
    def open_module(self, module_name):
        """Öffnet ein neues Modul-Fenster"""
        try:
            module_path = self.base_path / f"{module_name}.py"
            if module_path.exists():
                subprocess.Popen([sys.executable, str(module_path)])
                self.status_label.config(text=f"▶ {module_name}.py geöffnet")
                self.play_sound("good.mp3")
            else:
                messagebox.showwarning("Fehler", f"{module_name}.py nicht gefunden!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen:\n{str(e)}")
    
    def open_readme(self):
        """Öffnet die README-Datei"""
        readme_path = self.base_path / "README-LINUX.md"
        
        if readme_path.exists():
            try:
                subprocess.Popen(['xdg-open', str(readme_path)])
                self.status_label.config(text="▶ README wird geöffnet...")
                self.play_sound("good.mp3")
            except:
                messagebox.showinfo("README", f"README-Datei:\n{readme_path}")
        else:
            self.play_sound("failed.mp3")
            messagebox.showwarning("Fehler", "README-LINUX.md nicht gefunden!")
    
    def close_all_programs(self):
        """Beendet ALLE Picture Goose Programme"""
        self.play_sound("end.mp3")
        if messagebox.askyesno("Beenden", "ALLE Picture Goose Fenster beenden?"):
            # Beende alle Python-Prozesse mit Picture Goose
            import psutil
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and 'picture-goose' in ' '.join(proc.info['cmdline']).lower():
                        if proc.info['pid'] != current_pid:
                            proc.terminate()
                except:
                    pass
            # Eigenes Fenster schließen
            self.root.quit()
        else:
            self.play_sound("default.mp3")
    
    def play_sound(self, sound_file):
        """Spielt Sound ab mit System-Tools"""
        try:
            sound_path = self.materials_path / "audio" / sound_file
            if sound_path.exists():
                system = platform.system()
                if system == "Linux":
                    for player in ['paplay', 'aplay', 'mpg123', 'ffplay']:
                        try:
                            subprocess.Popen([player, str(sound_path)], 
                                           stdout=subprocess.DEVNULL, 
                                           stderr=subprocess.DEVNULL)
                            break
                        except FileNotFoundError:
                            continue
                elif system == "Darwin":
                    subprocess.Popen(['afplay', str(sound_path)])
                elif system == "Windows":
                    import winsound
                    winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = KeyboardSettings(root)
    root.mainloop()

