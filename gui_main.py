"""
Bryder WWS Koppeling - GUI Application (Tkinter Version)
Simple, fast GUI for managing the housing data pipeline.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import pandas as pd
from pathlib import Path
from io import StringIO
import sys

from pipeline.gui_backend import get_backend, PipelineBackend
from pipeline.config import EENHEDEN_CSV, RUIMTEN_CSV, JSON_DIR


class PipelineGUI:
    """Main GUI Application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bryder WWS Koppeling")
        self.root.geometry("1100x750")
        
        self.backend = get_backend(self._log_callback)
        self.log_buffer = StringIO()
        self.current_dfs = {}
        
        # Setup UI
        self._setup_ui()
        self._update_status()
    
    def _log_callback(self, message: str):
        """Callback for backend logging."""
        self.log_buffer.write(message + "\n")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update()
    
    def _setup_ui(self):
        """Build the UI."""
        # Main notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Dashboard
        self.dashboard_tab = ttk.Frame(notebook)
        notebook.add(self.dashboard_tab, text="📦 Dashboard")
        self._build_dashboard()
        
        # Tab 2: Data Editor
        self.editor_tab = ttk.Frame(notebook)
        notebook.add(self.editor_tab, text="✎ Bewerk Gegevens")
        self._build_editor()
        
        # Tab 3: Results
        self.results_tab = ttk.Frame(notebook)
        notebook.add(self.results_tab, text="📊 Resultaten")
        self._build_results()
    
    def _build_dashboard(self):
        """Build the dashboard tab."""
        frame = ttk.Frame(self.dashboard_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(frame, text="Bryder WWS Koppeling", font=("Helvetica", 16, "bold"))
        title.pack(pady=(0, 10))
        
        subtitle = ttk.Label(frame, text="Project pipeline beheer", foreground="gray")
        subtitle.pack(pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        # Extract status
        extract_frame = ttk.Frame(status_frame)
        extract_frame.pack(fill=tk.X, pady=5)
        ttk.Label(extract_frame, text="📥 Extractie:").pack(side=tk.LEFT)
        self.extract_status = ttk.Label(extract_frame, text="⏳ Wacht...", foreground="blue")
        self.extract_status.pack(side=tk.LEFT, padx=20)
        
        # JSON status
        json_frame = ttk.Frame(status_frame)
        json_frame.pack(fill=tk.X, pady=5)
        ttk.Label(json_frame, text="📄 JSON Conversie:").pack(side=tk.LEFT)
        self.json_status = ttk.Label(json_frame, text="⏳ Wacht...", foreground="blue")
        self.json_status.pack(side=tk.LEFT, padx=20)
        
        # Action buttons
        button_frame = ttk.LabelFrame(frame, text="Acties", padding=10)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="▶ Start Extractie", command=self._start_extract).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="✎ Bewerk Gegevens", command=self._go_to_editor).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="📊 Genereer JSON & Scores", command=self._start_json).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="🤖 Auto-fill standaardwaarden", command=self._autofill).pack(fill=tk.X, pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(frame, text="Activiteitenlog", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=100, 
                                                   state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear button
        ttk.Button(frame, text="Wis log", command=self._clear_log).pack(pady=10)
    
    def _build_editor(self):
        """Build the data editor tab."""
        frame = ttk.Frame(self.editor_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="📥 Laad Eenheden", command=lambda: self._load_csv("eenheden", "tree_eenheden")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📥 Laad Ruimten", command=lambda: self._load_csv("ruimten", "tree_ruimten")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📥 Laad Koppelingen", command=lambda: self._load_csv("mapping", "tree_mapping")).pack(side=tk.LEFT, padx=5)
        
        # Notebook for different CSVs
        csv_notebook = ttk.Notebook(frame)
        csv_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Eenheden tab
        eenheden_frame = ttk.Frame(csv_notebook)
        csv_notebook.add(eenheden_frame, text="Eenheden (161 woningen)")
        self.tree_eenheden = self._build_tree_view(eenheden_frame)
        
        # Ruimten tab
        ruimten_frame = ttk.Frame(csv_notebook)
        csv_notebook.add(ruimten_frame, text="Ruimten (495 kamers)")
        self.tree_ruimten = self._build_tree_view(ruimten_frame)
        
        # Mapping tab
        mapping_frame = ttk.Frame(csv_notebook)
        csv_notebook.add(mapping_frame, text="Koppelingen (66)")
        self.tree_mapping = self._build_tree_view(mapping_frame)
    
    def _build_tree_view(self, parent):
        """Create and return a Treeview widget."""
        tree = ttk.Treeview(parent, height=25)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        return tree
    
    def _build_results(self):
        """Build the results tab."""
        frame = ttk.Frame(self.results_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="📥 Laad Scores", command=lambda: self._load_csv("eenheden", "tree_scores", wws_only=True)).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 Vernieuwen", command=self._refresh_json_preview).pack(side=tk.LEFT, padx=5)
        
        # Notebook
        results_notebook = ttk.Notebook(frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results table
        scores_frame = ttk.Frame(results_notebook)
        results_notebook.add(scores_frame, text="WWS Scores")
        self.tree_scores = self._build_tree_view(scores_frame)
        
        # JSON preview
        json_frame = ttk.Frame(results_notebook)
        results_notebook.add(json_frame, text="JSON Preview")
        
        json_control = ttk.Frame(json_frame)
        json_control.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(json_control, text="Selecteer eenheid:").pack(side=tk.LEFT)
        self.json_combo = ttk.Combobox(json_control, state="readonly", width=30)
        self.json_combo.pack(side=tk.LEFT, padx=5)
        self.json_combo.bind("<<ComboboxSelected>>", lambda e: self._display_json())
        
        self.json_preview = scrolledtext.ScrolledText(json_frame, height=20, width=100,
                                                       state=tk.DISABLED, font=("Courier", 8))
        self.json_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Stats
        stats_frame = ttk.Frame(results_notebook)
        results_notebook.add(stats_frame, text="Statistieken")
        self.stats_view = scrolledtext.ScrolledText(stats_frame, height=20, width=100,
                                                     state=tk.DISABLED, font=("Courier", 9))
        self.stats_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _update_status(self):
        """Update status indicators."""
        status = self.backend.get_status()
        
        extract_text = "✓ Klaar" if status["extract_done"] else "⏳ Nog niet uitgevoerd"
        extract_color = "green" if status["extract_done"] else "blue"
        self.extract_status.config(text=extract_text, foreground=extract_color)
        
        json_text = "✓ Klaar" if status["json_done"] else "⏳ Nog niet uitgevoerd"
        json_color = "green" if status["json_done"] else "blue"
        self.json_status.config(text=json_text, foreground=json_color)
    
    def _start_extract(self):
        """Start extraction in a thread."""
        def worker():
            result = self.backend.extract()
            if result["success"]:
                messagebox.showinfo("✓ Extractie Voltooid",
                    f"- {result['eenheden_count']} eenheden\n"
                    f"- {result['ruimten_count']} ruimten\n"
                    f"- {result['mapped_count']} koppelingen\n"
                    f"- B2: {result['b2_apartments']} appartementen\n"
                    f"- B3: {result['b3_apartments']} appartementen")
                self._update_status()
            else:
                messagebox.showerror("Extractie Mislukt", result.get("error", "Onbekende fout"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _start_json(self):
        """Start JSON generation in a thread."""
        def worker():
            result = self.backend.json_convert()
            if result["success"]:
                messagebox.showinfo("✓ JSON Conversie Voltooid",
                    f"{result['json_count']} eenheden naar JSON geconverteerd")
                self._update_status()
            else:
                messagebox.showerror("JSON Conversie Mislukt", result.get("error", "Onbekende fout"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _autofill(self):
        """Auto-fill with defaults."""
        def worker():
            result = self.backend.fill_defaults_eenheden()
            if result["success"]:
                messagebox.showinfo("✓ Auto-fill Voltooid", "Standaardwaarden ingevuld!")
            else:
                messagebox.showerror("Auto-fill Mislukt", result.get("error", "Onbekende fout"))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def _load_csv(self, csv_type: str, tree_attr: str, wws_only: bool = False):
        """Load and display CSV data."""
        try:
            df = self.backend.read_csv(csv_type)
            
            # Filter for WWS columns if requested
            if wws_only:
                cols_to_show = ["oge_nummer", "omschrijving"] + [c for c in df.columns if c.startswith("wws_")][:10]
                df = df[[c for c in cols_to_show if c in df.columns]]
            
            self._display_in_tree(getattr(self, tree_attr), df)
            self.current_dfs[tree_attr] = df
            self._log_callback(f"✓ {csv_type}.csv geladen ({len(df)} rijen)")
        except Exception as e:
            messagebox.showerror("Fout", f"Kon {csv_type} niet laden: {e}")
            self._log_callback(f"✗ Fout bij laden {csv_type}: {e}")
    
    def _refresh_json_preview(self):
        """Refresh JSON file list."""
        try:
            json_files = sorted(JSON_DIR.glob("*.json"))
            names = [f.stem for f in json_files]
            self.json_combo['values'] = names
            self._log_callback(f"✓ {len(names)} JSON bestanden geladen")
        except Exception as e:
            messagebox.showerror("Fout", f"Kon JSON bestanden niet laden: {e}")
    
    def _display_json(self):
        """Display selected JSON file."""
        try:
            if not self.json_combo.get():
                return
            
            json_file = JSON_DIR / f"{self.json_combo.get()}.json"
            with open(json_file) as f:
                import json
                content = json.load(f)
            
            pretty = json.dumps(content, indent=2, ensure_ascii=False)
            self.json_preview.configure(state=tk.NORMAL)
            self.json_preview.delete(1.0, tk.END)
            self.json_preview.insert(1.0, pretty)
            self.json_preview.configure(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Fout", f"Kon JSON niet laden: {e}")
    
    def _display_in_tree(self, tree, df):
        """Display DataFrame in Treeview."""
        # Clear existing
        for item in tree.get_children():
            tree.delete(item)
        
        # Configure columns
        tree["columns"] = list(df.columns)
        tree.column("#0", width=0, stretch=tk.NO)
        
        for col in df.columns:
            tree.column(col, anchor=tk.W, width=100)
            tree.heading(col, text=col, anchor=tk.W)
        
        # Insert data
        for idx, row in df.iterrows():
            values = [str(row[col])[:100] for col in df.columns]  # Truncate long values
            tree.insert("", tk.END, values=values)
    
    def _go_to_editor(self):
        """Switch to editor tab (no-op in single window)."""
        pass
    
    def _clear_log(self):
        """Clear log."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log_buffer = StringIO()


def main():
    root = tk.Tk()
    gui = PipelineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
