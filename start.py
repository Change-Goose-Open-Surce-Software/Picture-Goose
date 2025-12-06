#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Picture Goose - Start Script
Startet die definierten Module
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Pfade definieren
    home = Path.home()
    base_path = home / ".picture-goose"
    safes_path = base_path / "safes"
    open_file = safes_path / "open.txt"
    window_file = safes_path / "window.txt"
    
    # NEU: Erfasse Kommandozeilen-Argumente (potenzieller Bildpfad)
    # Nur der erste unbenannte Pfad wird als initial_image_path behandelt
    initial_image_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else None

    # Standard-Module
    modules_to_open = ["main.py", "keyboard.py", "settings.py"]
    
    # open.txt lesen
    if open_file.exists():
        with open(open_file, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and line.strip().endswith('.py')]
            if lines:
                modules_to_open = lines
    
    print("═══════════════════════════════════")
    print("    PICTURE GOOSE - STARTING")
    print("═══════════════════════════════════")
    print(f"\nStarte Module: {', '.join(modules_to_open)}\n")
    
    # Module starten
    processes = []
    for module in modules_to_open:
        module_path = base_path / module
        if module_path.exists():
            try:
                cmd = [sys.executable, str(module_path)]
                
                # FÜGE PFAD ALS ARGUMENT HINZU, WENN ES MAIN.PY IST UND EIN PFAD VORHANDEN IST (Fix für Start/Nautilus Problem)
                if module == "main.py" and initial_image_path:
                    cmd.append(initial_image_path)
                
                # Starte Modul als separaten Prozess
                process = subprocess.Popen(cmd)
                processes.append(process)
                print(f"✓ {module} gestartet (PID: {process.pid})")
            except Exception as e:
                print(f"✗ Fehler beim Starten von {module}: {e}")
        else:
            print(f"✗ {module} nicht gefunden!")
    
    print("\n═══════════════════════════════════")
    print(f"   {len(processes)} Module aktiv")
    print("═══════════════════════════════════\n")
    
    # Warte auf alle Prozesse
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\nProgramme beendet.")

if __name__ == "__main__":
    main()
