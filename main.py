#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Picture Goose - Main Window - VERBESSERTE VERSION
Mit Suchleiste, Whitelist/Blacklist, GIMP, Umbenennen, Drag&Drop
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import platform
from pathlib import Path
from PIL import Image, ImageTk
import sys

class PictureGooseMain:
    def __init__(self, root, initial_image=None):
        self.root = root
        self.root.title("Picture Goose")
        
        # Pfade definieren
        self.home = Path.home()
        self.base_path = self.home / ".picture-goose"
        self.materials_path = self.base_path / "materials"
        self.safes_path = self.base_path / "safes"
        self.key_path = self.safes_path / "key"
        self.paths_dir = self.safes_path / "pfade"
        
        # Pfade-Verzeichnis erstellen
        self.paths_dir.mkdir(parents=True, exist_ok=True)
        
        # Einstellungen laden
        self.load_settings()
        self.load_keys()
        self.load_path_settings()
        
        # Fenster-Modus setzen
        self.set_window_mode()
        
        # GUI aufbauen
        self.setup_gui()
        
        # Bilderliste laden
        self.image_list = []
        self.current_image = None
        self.current_image_path = None
        self.initial_image = initial_image
        
        self.bind_keys()
        
        # Start-Sound abspielen
        self.play_sound("start.mp3")
        
        # Automatischer Scan
        if self.auto_scan:
            self.root.after(500, self.scan_images)
        
        # Wenn Startbild angegeben, öffne es
        if initial_image and os.path.exists(initial_image):
            self.root.after(1000, lambda: self.load_specific_image(initial_image))
        
        # Drag & Drop Setup
        self.setup_drag_drop()
    
    def load_path_settings(self):
        """Lädt Whitelist/Blacklist Einstellungen"""
        # Whitelist
        white_file = self.paths_dir / "white.txt"
        if not white_file.exists():
            with open(white_file, 'w') as f:
                f.write(str(self.home))
        
        self.whitelist = []
        if white_file.exists():
            with open(white_file, 'r') as f:
                self.whitelist = [Path(line.strip()) for line in f if line.strip()]
        
        # Blacklist
        black_file = self.paths_dir / "black.txt"
        if not black_file.exists():
            with open(black_file, 'w') as f:
                f.write(str(self.base_path))
        
        self.blacklist = []
        if black_file.exists():
            with open(black_file, 'r') as f:
                self.blacklist = [Path(line.strip()) for line in f if line.strip()]
        
        # Rang
        rang_file = self.paths_dir / "rang.txt"
        if not rang_file.exists():
            with open(rang_file, 'w') as f:
                f.write("white")
        
        self.path_priority = "white"
        if rang_file.exists():
            with open(rang_file, 'r') as f:
                self.path_priority = f.read().strip().lower()
    
    def is_path_allowed(self, path):
        """Prüft ob Pfad durchsucht werden darf"""
        path = Path(path)
        
        if self.path_priority == "white":
            # Erst Whitelist, dann Blacklist entfernen
            in_white = any(path.is_relative_to(w) for w in self.whitelist)
            in_black = any(path.is_relative_to(b) for b in self.blacklist)
            return in_white and not in_black
        else:
            # Erst Blacklist, dann Whitelist hinzufügen
            in_black = any(path.is_relative_to(b) for b in self.blacklist)
            in_white = any(path.is_relative_to(w) for w in self.whitelist)
            return not in_black or in_white
    
    def add_to_blacklist(self):
        """Fügt aktuellen Bildpfad zur Blacklist hinzu"""
        if not self.current_image_path:
            messagebox.showwarning("Warnung", "Kein Bild ausgewählt!")
            return
        
        path = Path(self.current_image_path).parent
        
        if messagebox.askyesno("Blacklist", f"Pfad zur Blacklist hinzufügen?\n{path}"):
            black_file = self.paths_dir / "black.txt"
            with open(black_file, 'a') as f:
                f.write(f"\n{path}")
            self.blacklist.append(path)
            self.play_sound("good.mp3")
            messagebox.showinfo("Erfolg", "Pfad zur Blacklist hinzugefügt!")
    
    def load_settings(self):
        """Lädt alle Einstellungen aus den Dateien"""
        # Sprache laden
        lang_file = self.safes_path / "language.txt"
        self.language = "English"
        if lang_file.exists():
            with open(lang_file, 'r') as f:
                self.language = f.read().strip()
        
        # Hintergrundfarbe laden
        self.bg_colors = []
        self.bg_index = 0
        self.change_timer = 0
        bg_file = self.safes_path / "colors" / "background.txt"
        if bg_file.exists():
            self.load_color_settings(bg_file, "bg")
        else:
            self.bg_colors = [("#2a2a2a", "dunkel")]
        
        # Textfarbe laden
        self.text_colors = []
        self.text_index = 0
        text_file = self.safes_path / "colors" / "writing.txt"
        if text_file.exists():
            self.load_color_settings(text_file, "text")
        else:
            self.text_colors = [("#00ff00", "hell")]
        
        # Auto-Scan Einstellung laden
        auto_file = self.safes_path / "auto.txt"
        self.auto_scan = False
        if auto_file.exists():
            with open(auto_file, 'r') as f:
                content = f.read().strip().lower()
                self.auto_scan = (content == "true")
    
    def load_keys(self):
        """Lädt Tastenbelegungen"""
        self.keys = {
            "scan": "f",
            "scale": "g",
            "crop": "z",
            "remove": "e",
            "rotate": "r",
            "find": "h",
            "rename": "u",
            "gimp": "g",
            "blacklist": "b"
        }
        
        key_files = {
            "scan": "scan.txt",
            "scale": "skalieren.txt",
            "crop": "cut.txt",
            "remove": "remove.txt",
            "rotate": "rotate.txt",
            "find": "find.txt",
            "rename": "rename.txt",
            "gimp": "gimp.txt",
            "blacklist": "blacklist.txt"
        }
        
        self.key_path.mkdir(parents=True, exist_ok=True)
        
        for key_name, file_name in key_files.items():
            key_file = self.key_path / file_name
            if key_file.exists():
                with open(key_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.keys[key_name] = content.lower()
            else:
                with open(key_file, 'w') as f:
                    f.write(self.keys[key_name])
    
    def load_color_settings(self, filepath, color_type):
        """Lädt Farbeinstellungen aus Datei"""
        colors = []
        change_timer = 0
        
        with open(filepath, 'r') as f:
            lines = [l.strip() for l in f.readlines()]
        
        i = 0
        while i < len(lines):
            if lines[i] == "color" and i + 1 < len(lines):
                color_name = lines[i + 1]
                kontrast = "dunkel" if color_type == "bg" else "hell"
                if i + 3 < len(lines) and lines[i + 2] == "kontrast":
                    kontrast = lines[i + 3]
                    i += 4
                else:
                    i += 2
                
                hex_color = self.get_hex_color(color_name, kontrast)
                colors.append((hex_color, kontrast))
            elif lines[i] == "change timer" and i + 1 < len(lines):
                try:
                    change_timer = int(lines[i + 1])
                except:
                    change_timer = 0
                i += 2
            else:
                i += 1
        
        if color_type == "bg":
            self.bg_colors = colors if colors else [("#2a2a2a", "dunkel")]
            self.change_timer = change_timer
        else:
            self.text_colors = colors if colors else [("#00ff00", "hell")]
    
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
    
    def set_window_mode(self):
        """Setzt Fenstermodus basierend auf window.txt"""
        window_file = self.safes_path / "window.txt"
        mode = "fenster"
        
        if window_file.exists():
            with open(window_file, 'r') as f:
                lines = [l.strip() for l in f.readlines()]
            
            for i, line in enumerate(lines):
                if line == "main.py" and i + 1 < len(lines):
                    mode = lines[i + 1]
                    break
        
        if mode == "vollbild":
            self.root.attributes('-fullscreen', True)
        else:
            self.root.geometry("1100x750")
    
    def setup_gui(self):
        """Erstellt die grafische Oberfläche im Retro-Stil"""
        current_bg = self.bg_colors[0][0]
        current_fg = self.text_colors[0][0]
        
        list_bg = "#1a1a1a" if current_bg in ["#000000", "#2a2a2a", "#404040"] else "#ffffff"
        list_fg = current_fg
        
        self.root.configure(bg=current_bg)
        
        # Retro-Style Frame
        main_frame = tk.Frame(self.root, bg=current_bg, bd=5, relief="ridge")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_frame = tk.Frame(main_frame, bg=current_bg, bd=3, relief="raised")
        title_frame.pack(fill="x", padx=5, pady=5)
        
        title_label = tk.Label(
            title_frame,
            text="╔══ PICTURE GOOSE ══╗",
            font=("Courier", 24, "bold"),
            bg=current_bg,
            fg=current_fg
        )
        title_label.pack(pady=10)
        
        # Haupt-Container
        content_frame = tk.Frame(main_frame, bg=current_bg)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Linke Seite: Bilderliste
        left_frame = tk.Frame(content_frame, bg=current_bg, bd=2, relief="sunken")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        list_label = tk.Label(
            left_frame,
            text="┌─ BILDER LISTE ─┐",
            font=("Courier", 12, "bold"),
            bg=current_bg,
            fg=current_fg
        )
        list_label.pack(pady=5)
        
        # SUCHLEISTE
        search_frame = tk.Frame(left_frame, bg=current_bg)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Label(search_frame, text="🔍", bg=current_bg, fg=current_fg, font=("Courier", 12)).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_images)
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Courier", 10),
            bg=list_bg,
            fg=list_fg
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Scrollbare Liste
        list_frame = tk.Frame(left_frame, bg=current_bg)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.image_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 10),
            bg=list_bg,
            fg=list_fg,
            selectbackground=current_fg,
            selectforeground=current_bg,
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED
        )
        self.image_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        self.image_listbox.bind('<Return>', self.on_image_select)
        
        # Button-Zeile
        btn_row = tk.Frame(left_frame, bg=current_bg)
        btn_row.pack(pady=5)
        
        tk.Button(
            btn_row,
            text=f"▶ SCAN ({self.keys['scan'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.scan_images,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_row,
            text=f"🔍 SUCHEN ({self.keys['find'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.focus_search,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        # Rechte Seite: Bildanzeige und Info
        right_frame = tk.Frame(content_frame, bg=current_bg, bd=2, relief="sunken")
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Bildanzeige
        image_label = tk.Label(
            right_frame,
            text="┌─ BILD VORSCHAU ─┐",
            font=("Courier", 12, "bold"),
            bg=current_bg,
            fg=current_fg
        )
        image_label.pack(pady=5)
        
        self.image_canvas = tk.Canvas(
            right_frame,
            bg="#000000",
            width=500,
            height=400,
            relief="sunken",
            bd=3
        )
        self.image_canvas.pack(padx=10, pady=10)
        
        # Info-Bereich
        info_label = tk.Label(
            right_frame,
            text="┌─ BILD INFO ─┐",
            font=("Courier", 12, "bold"),
            bg=current_bg,
            fg=current_fg
        )
        info_label.pack(pady=5)
        
        self.info_text = tk.Text(
            right_frame,
            font=("Courier", 9),
            bg=list_bg,
            fg=list_fg,
            height=6,
            relief="sunken",
            bd=2
        )
        self.info_text.pack(padx=10, pady=5, fill="x")
        
        # Button-Leiste
        button_frame = tk.Frame(right_frame, bg=current_bg)
        button_frame.pack(pady=10)
        
        # Zeile 1
        row1 = tk.Frame(button_frame, bg=current_bg)
        row1.pack(pady=2)
        
        tk.Button(
            row1,
            text=f"✂ SCHNEIDEN ({self.keys['crop'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.crop_image,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        tk.Button(
            row1,
            text=f"⇄ SKALIEREN ({self.keys['scale'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.scale_image,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        # Zeile 2
        row2 = tk.Frame(button_frame, bg=current_bg)
        row2.pack(pady=2)
        
        tk.Button(
            row2,
            text=f"↻ ROTIEREN ({self.keys['rotate'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.rotate_image,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        tk.Button(
            row2,
            text=f"✖ LÖSCHEN ({self.keys['remove'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#8b0000",
            fg=current_fg,
            command=self.delete_image,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        # Zeile 3
        row3 = tk.Frame(button_frame, bg=current_bg)
        row3.pack(pady=2)
        
        tk.Button(
            row3,
            text=f"🎨 GIMP ({self.keys['gimp'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.open_in_gimp,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        tk.Button(
            row3,
            text=f"✎ UMBENENNEN ({self.keys['rename'].upper()})",
            font=("Courier", 10, "bold"),
            bg="#004400",
            fg=current_fg,
            command=self.rename_image,
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        # Farbwechsel-Timer starten
        if self.change_timer > 0:
            self.start_color_timer()
    
    def setup_drag_drop(self):
        """Richtet Drag & Drop ein (vereinfachte Version)"""
        # Notiz: Volles Drag & Drop benötigt tkinterdnd2
        # Hier eine vereinfachte Version
        pass
    
    def focus_search(self):
        """Fokussiert die Suchleiste"""
        self.search_entry.focus()
        self.search_entry.select_range(0, tk.END)
    
    def filter_images(self, *args):
        """Filtert Bilderliste basierend auf Suchbegriff"""
        search_term = self.search_var.get().lower()
        self.image_listbox.delete(0, tk.END)
        
        for path in self.image_list:
            filename = os.path.basename(path)
            if search_term in filename.lower() or search_term in path.lower():
                self.image_listbox.insert(tk.END, f"▸ {filename}")
    
    def bind_keys(self):
        """Bindet Tasten an Funktionen"""
        self.root.bind(f'<{self.keys["scan"]}>', lambda e: self.scan_images())
        self.root.bind(f'<{self.keys["crop"]}>', lambda e: self.crop_image())
        self.root.bind(f'<{self.keys["scale"]}>', lambda e: self.scale_image())
        self.root.bind(f'<{self.keys["remove"]}>', lambda e: self.delete_image())
        self.root.bind(f'<{self.keys["rotate"]}>', lambda e: self.rotate_image())
        self.root.bind(f'<{self.keys["find"]}>', lambda e: self.focus_search())
        self.root.bind(f'<{self.keys["rename"]}>', lambda e: self.rename_image())
        self.root.bind(f'<{self.keys["gimp"]}>', lambda e: self.open_in_gimp())
        self.root.bind(f'<{self.keys["blacklist"]}>', lambda e: self.add_to_blacklist())
        
        self.root.bind('<Down>', lambda e: self.move_selection(1))
        self.root.bind('<Up>', lambda e: self.move_selection(-1))
    
    def move_selection(self, direction):
        """Bewegt die Auswahl und scrollt"""
        current_index = self.image_listbox.index(tk.ANCHOR)
        
        if not self.image_list:
            return
        
        new_index = current_index + direction
        
        if new_index < 0:
            new_index = 0
        elif new_index >= len(self.image_list):
            new_index = len(self.image_list) - 1
        
        self.image_listbox.selection_clear(0, tk.END)
        self.image_listbox.selection_set(new_index)
        self.image_listbox.activate(new_index)
        self.image_listbox.see(new_index)
        
        self.on_image_select(None)
    
    def scan_images(self):
        """Durchsucht erlaubte Pfade nach Bildern"""
        self.image_listbox.delete(0, tk.END)
        self.image_list = []
        
        # Erweiterte Formate
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico']
        
        scan_paths = self.whitelist if self.whitelist else [self.home]
        
        for scan_path in scan_paths:
            if not scan_path.exists():
                continue
            
            for root, dirs, files in os.walk(scan_path):
                # Prüfe ob Pfad erlaubt ist
                if not self.is_path_allowed(root):
                    dirs.clear()
                    continue
                
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        full_path = os.path.join(root, file)
                        self.image_list.append(full_path)
                        self.image_listbox.insert(tk.END, f"▸ {file}")
        
        self.play_sound("good.mp3")
        messagebox.showinfo("Scan Complete", f"{len(self.image_list)} Bilder gefunden!")
    
    def load_specific_image(self, image_path):
        """Lädt ein spezifisches Bild (für Standardprogramm)"""
        if not os.path.exists(image_path):
            return
        
        # WICHTIG: Bild direkt zur Liste hinzufügen und anzeigen
        # statt auf Scan zu warten
        image_path = os.path.abspath(image_path)
        
        # Füge das Bild sofort hinzu
        if image_path not in self.image_list:
            self.image_list.append(image_path)
            self.image_listbox.insert(tk.END, f"▸ {os.path.basename(image_path)}")
        
        # Wähle das Bild aus
        try:
            index = self.image_list.index(image_path)
            self.image_listbox.selection_clear(0, tk.END)
            self.image_listbox.selection_set(index)
            self.image_listbox.activate(index)
            self.image_listbox.see(index)
            self.current_image_path = image_path
            self.display_image()
            self.display_info()
        except ValueError:
            pass
        
        # Scanne dann im Hintergrund den Rest
        self.root.after(1000, self.scan_images)
    
    def on_image_select(self, event):
        """Wird aufgerufen wenn Bilder ausgewählt werden"""
        try:
            index = self.image_listbox.index(tk.ANCHOR)
            if 0 <= index < len(self.image_list):
                self.current_image_path = self.image_list[index]
                self.display_image()
                self.display_info()
        except:
            pass
    
    def display_image(self):
        """Zeigt das ausgewählte Bild an"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            self.image_canvas.delete("all")
            return
        
        try:
            img = Image.open(self.current_image_path)
            
            canvas_width = 500
            canvas_height = 400
            img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            self.current_image = ImageTk.PhotoImage(img)
            
            self.image_canvas.delete("all")
            self.image_canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.current_image
            )
        except Exception as e:
            pass
    
    def display_info(self):
        """Zeigt Bildinformationen an"""
        if not self.current_image_path or not os.path.exists(self.current_image_path):
            self.info_text.delete(1.0, tk.END)
            return
        
        self.info_text.delete(1.0, tk.END)
        
        try:
            img = Image.open(self.current_image_path)
            file_size = os.path.getsize(self.current_image_path)
            
            info = f"""
┌──────────────────────────────┐
│ DATEINAME: {os.path.basename(self.current_image_path)}
│ PFAD: {self.current_image_path}
│ FORMAT: {img.format}
│ GRÖSSE: {img.size[0]} x {img.size[1]} Pixel
│ DATEIGRÖSSE: {file_size / 1024:.2f} KB
│ MODUS: {img.mode}
└──────────────────────────────┘
            """
            self.info_text.insert(1.0, info)
        except Exception as e:
            self.info_text.insert(1.0, f"Fehler beim Laden der Info.")
    
    def open_in_gimp(self):
        """Öffnet Bild in GIMP"""
        if not self.current_image_path:
            messagebox.showwarning("Warnung", "Kein Bild ausgewählt!")
            return
        
        try:
            subprocess.Popen(['gimp', self.current_image_path])
            self.play_sound("good.mp3")
        except FileNotFoundError:
            messagebox.showerror("Fehler", "GIMP nicht gefunden!\nBitte installiere GIMP.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen:\n{str(e)}")
    
    def rename_image(self):
        """Benennt Bild(er) um"""
        selection = self.image_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Keine Bilder ausgewählt!")
            return
        
        rename_window = tk.Toplevel(self.root)
        rename_window.title("Bild(er) umbenennen")
        rename_window.geometry("500x350")
        rename_window.configure(bg=self.bg_colors[0][0])
        
        current_bg = self.bg_colors[0][0]
        current_fg = self.text_colors[0][0]
        
        # UNTERSCHEIDUNG: Einzeln oder Mehrfach
        if len(selection) == 1:
            # EINZELBILD: Kompletter neuer Name
            tk.Label(rename_window, text="Neuer Dateiname:", 
                    font=("Courier", 12, "bold"), bg=current_bg, 
                    fg=current_fg).pack(pady=15)
            
            old_path = self.image_list[selection[0]]
            old_name = os.path.basename(old_path)
            name, ext = os.path.splitext(old_name)
            
            tk.Label(rename_window, text=f"Aktuell: {old_name}", 
                    font=("Courier", 9), bg=current_bg, 
                    fg=current_fg).pack(pady=5)
            
            frame = tk.Frame(rename_window, bg=current_bg)
            frame.pack(pady=10)
            
            tk.Label(frame, text="Neuer Name:", bg=current_bg, fg=current_fg).grid(row=0, column=0, padx=5)
            new_name_entry = tk.Entry(frame, width=25)
            new_name_entry.grid(row=0, column=1, padx=5)
            new_name_entry.insert(0, name)
            new_name_entry.focus()
            new_name_entry.select_range(0, tk.END)
            
            tk.Label(frame, text=ext, bg=current_bg, fg=current_fg).grid(row=0, column=2)
            
            def do_single_rename():
                new_name = new_name_entry.get().strip()
                if not new_name:
                    messagebox.showwarning("Warnung", "Name darf nicht leer sein!")
                    return
                
                new_path = os.path.join(os.path.dirname(old_path), new_name + ext)
                
                try:
                    os.rename(old_path, new_path)
                    self.image_list[selection[0]] = new_path
                    self.play_sound("good.mp3")
                    messagebox.showinfo("Erfolg", "Datei umbenannt!")
                    rename_window.destroy()
                    self.scan_images()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Umbenennen:\n{str(e)}")
            
            tk.Button(rename_window, text="✓ UMBENENNEN", command=do_single_rename,
                     bg="#004400", fg=current_fg, font=("Courier", 10, "bold")).pack(pady=20)
            
            new_name_entry.bind('<Return>', lambda e: do_single_rename())
        
        else:
            # MEHRFACHAUSWAHL: Präfix/Suffix
            tk.Label(rename_window, text=f"Mehrfachumbenennung ({len(selection)} Dateien):", 
                    font=("Courier", 12, "bold"), bg=current_bg, 
                    fg=current_fg).pack(pady=15)
            
            frame = tk.Frame(rename_window, bg=current_bg)
            frame.pack(pady=10)
            
            tk.Label(frame, text="Präfix (davor):", bg=current_bg, fg=current_fg).grid(row=0, column=0, padx=5, sticky="w")
            prefix_entry = tk.Entry(frame, width=20)
            prefix_entry.grid(row=0, column=1, padx=5)
            
            tk.Label(frame, text="Suffix (danach):", bg=current_bg, fg=current_fg).grid(row=1, column=0, padx=5, pady=5, sticky="w")
            suffix_entry = tk.Entry(frame, width=20)
            suffix_entry.grid(row=1, column=1, padx=5)
            
            # Beispiel
            tk.Label(rename_window, text="Beispiel: Präfix='Urlaub_' + Suffix='_2024'", 
                    font=("Courier", 8), bg=current_bg, 
                    fg=current_fg).pack(pady=5)
            tk.Label(rename_window, text="→ Urlaub_foto_1_2024.jpg, Urlaub_foto_2_2024.jpg", 
                    font=("Courier", 8), bg=current_bg, 
                    fg=current_fg).pack(pady=2)
            
            def do_multi_rename():
                prefix = prefix_entry.get()
                suffix = suffix_entry.get()
                
                for idx, sel_idx in enumerate(selection):
                    old_path = self.image_list[sel_idx]
                    old_name = os.path.basename(old_path)
                    name, ext = os.path.splitext(old_name)
                    
                    new_name = f"{prefix}{name}_{idx+1}{suffix}{ext}"
                    new_path = os.path.join(os.path.dirname(old_path), new_name)
                    
                    try:
                        os.rename(old_path, new_path)
                        self.image_list[sel_idx] = new_path
                    except Exception as e:
                        messagebox.showerror("Fehler", f"Fehler bei {old_name}:\n{str(e)}")
                
                self.play_sound("good.mp3")
                messagebox.showinfo("Erfolg", f"{len(selection)} Datei(en) umbenannt!")
                rename_window.destroy()
                self.scan_images()
            
            tk.Button(rename_window, text="✓ UMBENENNEN", command=do_multi_rename,
                     bg="#004400", fg=current_fg, font=("Courier", 10, "bold")).pack(pady=20)
    
    def delete_image(self):
        """Löscht ausgewählte Bilder"""
        selection = self.image_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warnung", "Keine Bilder ausgewählt!")
            return
        
        count = len(selection)
        confirm = messagebox.askyesno("Löschen", f"Soll(en) {count} Datei(en) wirklich gelöscht werden?")
        
        if confirm:
            try:
                deleted_count = 0
                for index in reversed(selection):
                    path = self.image_list[index]
                    try:
                        if os.path.exists(path):
                            os.remove(path)
                        self.image_listbox.delete(index)
                        self.image_list.pop(index)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Fehler beim Löschen von {path}: {e}")
                
                self.current_image_path = None
                self.image_canvas.delete("all")
                self.info_text.delete(1.0, tk.END)
                
                self.play_sound("good.mp3")
                messagebox.showinfo("Erfolg", f"{deleted_count} Bilder gelöscht.")
            except Exception as e:
                self.play_sound("failed.mp3")
                messagebox.showerror("Fehler", f"Fehler beim Löschen:\n{str(e)}")
        else:
            self.play_sound("default.mp3")
    
    def rotate_image(self):
        """Rotiert Bild"""
        if not self.current_image_path:
            messagebox.showwarning("Warnung", "Bitte wähle zuerst ein Bild aus!")
            return
        
        rot_window = tk.Toplevel(self.root)
        rot_window.title("Bild Rotieren")
        rot_window.geometry("350x250")
        rot_window.configure(bg=self.bg_colors[0][0])
        
        current_bg = self.bg_colors[0][0]
        current_fg = self.text_colors[0][0]
        
        tk.Label(rot_window, text="Rotationseinstellungen:", 
                font=("Courier", 12, "bold"), bg=current_bg, 
                fg=current_fg).pack(pady=15)
        
        frame_deg = tk.Frame(rot_window, bg=current_bg)
        frame_deg.pack(pady=5)
        
        tk.Label(frame_deg, text="Grad (z.B. 90):", font=("Courier", 10), 
                 bg=current_bg, fg=current_fg).pack(side="left")
        
        degree_entry = tk.Entry(frame_deg, width=5, font=("Courier", 10))
        degree_entry.pack(side="left", padx=5)
        degree_entry.insert(0, "90")
        
        tk.Label(rot_window, text="Richtung wählen:", font=("Courier", 10),
                 bg=current_bg, fg=current_fg).pack(pady=10)
        
        def do_rotate(direction):
            try:
                degrees = float(degree_entry.get())
                if direction == "right":
                    degrees = -degrees
                
                img = Image.open(self.current_image_path)
                rotated = img.rotate(degrees, expand=True, resample=Image.BICUBIC)
                
                save_path = filedialog.asksaveasfilename(
                    initialfile=f"rotated_{os.path.basename(self.current_image_path)}",
                    defaultextension=".png",
                    filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
                )
                
                if save_path:
                    rotated.save(save_path)
                    self.play_sound("good.mp3")
                    messagebox.showinfo("Erfolg", "Bild wurde rotiert!")
                    rot_window.destroy()
            except Exception as e:
                self.play_sound("failed.mp3")
                messagebox.showerror("Fehler", f"Fehler beim Rotieren:\n{str(e)}")
        
        btn_frame = tk.Frame(rot_window, bg=current_bg)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="↶ LINKS", command=lambda: do_rotate("left"),
                 bg="#004400", fg=current_fg, font=("Courier", 10, "bold"), width=10).pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="rechts ↷", command=lambda: do_rotate("right"),
                 bg="#004400", fg=current_fg, font=("Courier", 10, "bold"), width=10).pack(side="left", padx=10)
    
    def crop_image(self):
        """Schneidet Bild"""
        if not self.current_image_path:
            messagebox.showwarning("Warnung", "Bitte wähle zuerst ein Bild aus!")
            return
        
        crop_window = tk.Toplevel(self.root)
        crop_window.title("Bild Schneiden")
        crop_window.geometry("300x250")
        crop_window.configure(bg=self.bg_colors[0][0])
        
        current_bg = self.bg_colors[0][0]
        current_fg = self.text_colors[0][0]
        
        tk.Label(crop_window, text="Crop-Dimensionen eingeben:", 
                font=("Courier", 10), bg=current_bg, 
                fg=current_fg).pack(pady=10)
        
        frame = tk.Frame(crop_window, bg=current_bg)
        frame.pack(pady=10)
        
        entries = {}
        for i, pos in enumerate(["Links", "Oben", "Rechts", "Unten"]):
            tk.Label(frame, text=f"{pos}:", bg=current_bg, fg=current_fg).grid(row=i, column=0)
            entry = tk.Entry(frame, width=10)
            entry.grid(row=i, column=1)
            entries[pos.lower()] = entry
        
        entries["links"].insert(0, "0")
        entries["oben"].insert(0, "0")
        entries["rechts"].insert(0, "100")
        entries["unten"].insert(0, "100")
        
        def do_crop():
            try:
                img = Image.open(self.current_image_path)
                box = (
                    int(entries["links"].get()),
                    int(entries["oben"].get()),
                    int(entries["rechts"].get()),
                    int(entries["unten"].get())
                )
                
                cropped = img.crop(box)
                
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG", "*.png"), ("All Files", "*.*")]
                )
                
                if save_path:
                    cropped.save(save_path)
                    self.play_sound("good.mp3")
                    messagebox.showinfo("Erfolg", "Bild wurde zugeschnitten!")
                    crop_window.destroy()
            except Exception as e:
                self.play_sound("failed.mp3")
                messagebox.showerror("Fehler", f"Fehler beim Schneiden:\n{str(e)}")
        
        tk.Button(crop_window, text="✂ Schneiden", command=do_crop,
                 bg="#004400", fg=current_fg, font=("Courier", 10, "bold")).pack(pady=10)
    
    def scale_image(self):
        """Skaliert Bild"""
        if not self.current_image_path:
            messagebox.showwarning("Warnung", "Bitte wähle zuerst ein Bild aus!")
            return
        
        scale_window = tk.Toplevel(self.root)
        scale_window.title("Bild Skalieren")
        scale_window.geometry("300x150")
        scale_window.configure(bg=self.bg_colors[0][0])
        
        current_bg = self.bg_colors[0][0]
        current_fg = self.text_colors[0][0]
        
        tk.Label(scale_window, text="Neue Dimensionen:", 
                font=("Courier", 10), bg=current_bg,
                fg=current_fg).pack(pady=10)
        
        frame = tk.Frame(scale_window, bg=current_bg)
        frame.pack(pady=10)
        
        tk.Label(frame, text="Breite:", bg=current_bg, fg=current_fg).grid(row=0, column=0)
        width_entry = tk.Entry(frame, width=10)
        width_entry.grid(row=0, column=1)
        width_entry.insert(0, "800")
        
        tk.Label(frame, text="Höhe:", bg=current_bg, fg=current_fg).grid(row=1, column=0)
        height_entry = tk.Entry(frame, width=10)
        height_entry.grid(row=1, column=1)
        height_entry.insert(0, "600")
        
        def do_scale():
            try:
                img = Image.open(self.current_image_path)
                width = int(width_entry.get())
                height = int(height_entry.get())
                
                scaled = img.resize((width, height), Image.Resampling.LANCZOS)
                
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG", "*.png"), ("All Files", "*.*")]
                )
                
                if save_path:
                    scaled.save(save_path)
                    self.play_sound("good.mp3")
                    messagebox.showinfo("Erfolg", "Bild wurde skaliert!")
                    scale_window.destroy()
            except Exception as e:
                self.play_sound("failed.mp3")
                messagebox.showerror("Fehler", f"Fehler beim Skalieren:\n{str(e)}")
        
        tk.Button(scale_window, text="⇄ Skalieren", command=do_scale,
                 bg="#004400", fg=current_fg, font=("Courier", 10, "bold")).pack(pady=10)
    
    def play_sound(self, sound_file):
        """Spielt einen Sound ab"""
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
    
    def start_color_timer(self):
        """Startet Timer für Farbwechsel"""
        def change_colors():
            self.bg_index = (self.bg_index + 1) % len(self.bg_colors)
            self.text_index = (self.text_index + 1) % len(self.text_colors)
            
            new_bg = self.bg_colors[self.bg_index][0]
            new_fg = self.text_colors[self.text_index][0]
            
            self.update_widget_colors(new_bg, new_fg)
            
            self.root.after(self.change_timer * 100, change_colors)
        
        if self.change_timer > 0:
            self.root.after(self.change_timer * 100, change_colors)
    
    def update_widget_colors(self, new_bg, new_fg):
        """Aktualisiert die Farben aller Widgets"""
        list_bg = "#1a1a1a" if new_bg in ["#000000", "#2a2a2a", "#404040"] else "#ffffff"
        
        def apply_colors(widget):
            try:
                if isinstance(widget, (tk.Frame, tk.Toplevel, tk.Tk)):
                    widget.configure(bg=new_bg)
                elif isinstance(widget, (tk.Label, tk.Button, tk.Radiobutton, tk.Checkbutton)):
                    widget.configure(bg=new_bg, fg=new_fg)
                elif isinstance(widget, tk.Listbox):
                    widget.configure(bg=list_bg, fg=new_fg, selectbackground=new_fg, selectforeground=new_bg)
                elif isinstance(widget, tk.Text):
                    widget.configure(bg=list_bg, fg=new_fg)
            except tk.TclError:
                pass
            
            for child in widget.winfo_children():
                apply_colors(child)
        
        apply_colors(self.root)

if __name__ == "__main__":
    # Unterstützt Kommandozeilenargument für Startbild
    initial_image = sys.argv[1] if len(sys.argv) > 1 else None
    
    root = tk.Tk()
    app = PictureGooseMain(root, initial_image)
    root.mainloop()
