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
from pipeline.config import EENHEDEN_CSV, RUIMTEN_CSV, MAPPING_CSV, JSON_DIR


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
        
        # Auto-load existing data into editor and results tabs
        self.root.after(100, self._auto_load_data)
    
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
        self.notebook = ttk.Notebook(self.root)
        notebook = self.notebook
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
        
        # Tab 4: Recommendations
        self.recommendations_tab = ttk.Frame(notebook)
        notebook.add(self.recommendations_tab, text="💡 Aanbevelingen")
        self._build_recommendations()
    
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
        
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(control_frame, text="💾 Opslaan Eenheden", command=lambda: self._save_edited_csv("eenheden", "tree_eenheden")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Opslaan Ruimten", command=lambda: self._save_edited_csv("ruimten", "tree_ruimten")).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Opslaan Koppelingen", command=lambda: self._save_edited_csv("mapping", "tree_mapping")).pack(side=tk.LEFT, padx=5)
        
        # Hint
        hint = ttk.Label(frame, text="💡 Dubbelklik op een cel om de waarde te bewerken.", foreground="gray")
        hint.pack(anchor=tk.W, pady=(0, 5))
        
        # Notebook for different CSVs
        self.csv_notebook = ttk.Notebook(frame)
        self.csv_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Eenheden tab
        eenheden_frame = ttk.Frame(self.csv_notebook)
        self.csv_notebook.add(eenheden_frame, text="Eenheden")
        self.tree_eenheden = self._build_tree_view(eenheden_frame, editable=True)
        
        # Ruimten tab
        ruimten_frame = ttk.Frame(self.csv_notebook)
        self.csv_notebook.add(ruimten_frame, text="Ruimten")
        self.tree_ruimten = self._build_tree_view(ruimten_frame, editable=True)
        
        # Mapping tab
        mapping_frame = ttk.Frame(self.csv_notebook)
        self.csv_notebook.add(mapping_frame, text="Koppelingen")
        self.tree_mapping = self._build_tree_view(mapping_frame, editable=True)
    
    def _build_tree_view(self, parent, editable=False):
        """Create and return a Treeview widget."""
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tree = ttk.Treeview(container, height=25)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(container, orient=tk.VERTICAL, command=tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        tree.configure(xscrollcommand=hsb.set)
        
        if editable:
            tree.bind("<Double-1>", lambda e: self._on_tree_double_click(e, tree))
        
        return tree
    
    def _on_tree_double_click(self, event, tree):
        """Handle double-click on a Treeview cell to edit it inline."""
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        row_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not row_id or not column:
            return
        
        # Get column index (Tkinter columns are like "#1", "#2", ...)
        col_idx = int(column.replace("#", "")) - 1
        columns = tree["columns"]
        if col_idx < 0 or col_idx >= len(columns):
            return
        
        # Get current value
        current_values = tree.item(row_id, "values")
        current_value = current_values[col_idx] if col_idx < len(current_values) else ""
        
        # Get cell bounding box
        bbox = tree.bbox(row_id, column)
        if not bbox:
            return
        
        x, y, w, h = bbox
        
        # Create an Entry widget over the cell
        entry = tk.Entry(tree, font=("TkDefaultFont",))
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus_set()
        
        def commit(event=None):
            new_value = entry.get()
            values = list(tree.item(row_id, "values"))
            values[col_idx] = new_value
            tree.item(row_id, values=values)
            entry.destroy()
        
        def cancel(event=None):
            entry.destroy()
        
        entry.bind("<Return>", commit)
        entry.bind("<Tab>", commit)
        entry.bind("<Escape>", cancel)
        entry.bind("<FocusOut>", commit)
    
    def _save_edited_csv(self, csv_type: str, tree_attr: str):
        """Save the edited Treeview data back to CSV."""
        try:
            tree = getattr(self, tree_attr)
            columns = list(tree["columns"])
            
            rows = []
            for item in tree.get_children():
                values = tree.item(item, "values")
                rows.append(dict(zip(columns, values)))
            
            df = pd.DataFrame(rows, columns=columns)
            self.backend.save_csv(csv_type, df)
            self.current_dfs[tree_attr] = df
            self._log_callback(f"✓ {csv_type}.csv opgeslagen ({len(df)} rijen)")
            messagebox.showinfo("Opgeslagen", f"{csv_type}.csv is opgeslagen ({len(df)} rijen)")
        except Exception as e:
            messagebox.showerror("Fout", f"Kon {csv_type} niet opslaan: {e}")
            self._log_callback(f"✗ Fout bij opslaan {csv_type}: {e}")
    
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
    
    def _build_recommendations(self):
        """Build the recommendations tab."""
        frame = ttk.Frame(self.recommendations_tab, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(control_frame, text="Selecteer eenheid:").pack(side=tk.LEFT, padx=5)
        self.rec_combo = ttk.Combobox(control_frame, state="readonly", width=30)
        self.rec_combo.pack(side=tk.LEFT, padx=5)
        self.rec_combo.bind("<<ComboboxSelected>>", lambda e: self._display_recommendations())
        
        ttk.Button(control_frame, text="🔄 Vernieuwen", command=self._refresh_recommendations_list).pack(side=tk.LEFT, padx=5)
        
        # Recommendations display
        self.recommendations_view = scrolledtext.ScrolledText(frame, height=30, width=100,
                                                               state=tk.DISABLED, font=("Courier", 9), wrap=tk.WORD)
        self.recommendations_view.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
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
                # Reload editor data after extraction
                self.root.after(100, self._auto_load_data)
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
                # Reload results after JSON generation
                self.root.after(100, self._auto_load_data)
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
    
    def _auto_load_data(self):
        """Automatically load all available data into the GUI on startup."""
        status = self.backend.get_status()
        
        # --- Editor Tab: Load CSVs ---
        if status["extract_done"]:
            try:
                df_e = self.backend.read_csv("eenheden")
                self._display_in_tree(self.tree_eenheden, df_e)
                self.current_dfs["tree_eenheden"] = df_e
                self.csv_notebook.tab(0, text=f"Eenheden ({len(df_e)})")
                self._log_callback(f"✓ eenheden.csv geladen ({len(df_e)} rijen)")
            except Exception as e:
                self._log_callback(f"⚠ Kon eenheden niet laden: {e}")
            
            try:
                df_r = self.backend.read_csv("ruimten")
                self._display_in_tree(self.tree_ruimten, df_r)
                self.current_dfs["tree_ruimten"] = df_r
                self.csv_notebook.tab(1, text=f"Ruimten ({len(df_r)})")
                self._log_callback(f"✓ ruimten.csv geladen ({len(df_r)} rijen)")
            except Exception as e:
                self._log_callback(f"⚠ Kon ruimten niet laden: {e}")
            
            try:
                df_m = self.backend.read_csv("mapping")
                self._display_in_tree(self.tree_mapping, df_m)
                self.current_dfs["tree_mapping"] = df_m
                self.csv_notebook.tab(2, text=f"Koppelingen ({len(df_m)})")
                self._log_callback(f"✓ mapping.csv geladen ({len(df_m)} rijen)")
            except Exception as e:
                self._log_callback(f"⚠ Kon mapping niet laden: {e}")
        
        # --- Results Tab: JSON preview + per-unit summary + statistics ---
        if status["json_done"]:
            # Populate JSON dropdown
            self._refresh_json_preview()
            # Select first JSON by default
            if self.json_combo['values']:
                self.json_combo.current(0)
                self._display_json()
            
            # Build per-unit summary in scores tree
            self._load_unit_summary()
            
            # Compute statistics
            self._compute_statistics()
            
            # Load recommendations list
            self._refresh_recommendations_list()
    
    def _load_unit_summary(self):
        """Build a per-unit summary table showing key info per eenheid."""
        try:
            import json as jsonlib
            
            json_files = sorted(JSON_DIR.glob("*.json"))
            if not json_files:
                return
            
            rows = []
            for jf in json_files:
                with open(jf, encoding="utf-8") as f:
                    data = jsonlib.load(f)
                
                eid = data.get("id", "")
                adres = data.get("adres", {})
                straat = adres.get("straatnaam", "")
                huisnr = adres.get("huisnummer", "")
                postcode = adres.get("postcode", "")
                plaats = adres.get("woonplaats", {}).get("naam", "")
                
                ruimten = data.get("ruimten", [])
                n_rooms = len(ruimten)
                total_opp = sum(r.get("oppervlakte", 0) for r in ruimten)
                n_vertrek = sum(1 for r in ruimten if r.get("soort", {}).get("code") == "VTK")
                n_verkeer = sum(1 for r in ruimten if r.get("soort", {}).get("code") == "VRK")
                n_overig = sum(1 for r in ruimten if r.get("soort", {}).get("code") == "OVR")
                verwarmd_opp = sum(r.get("oppervlakte", 0) for r in ruimten if r.get("verwarmd"))
                
                bouwjaar = data.get("bouwjaar", "")
                wws = data.get("woningwaarderingstelsel", {}).get("code", "")
                
                rows.append({
                    "Eenheid ID": eid,
                    "Adres": f"{straat} {huisnr}",
                    "Postcode": postcode,
                    "Plaats": plaats,
                    "WWS": wws,
                    "Bouwjaar": str(bouwjaar) if bouwjaar else "-",
                    "Ruimten": n_rooms,
                    "Vertrekken": n_vertrek,
                    "Verkeers": n_verkeer,
                    "Overig": n_overig,
                    "Opp. (m²)": f"{total_opp:.1f}",
                    "Verwarmd (m²)": f"{verwarmd_opp:.1f}",
                })
            
            df_summary = pd.DataFrame(rows)
            self._display_in_tree(self.tree_scores, df_summary)
            self.current_dfs["tree_scores"] = df_summary
            self._log_callback(f"✓ Overzicht geladen: {len(rows)} eenheden met ruimtedata")
        except Exception as e:
            self._log_callback(f"⚠ Kon overzicht niet laden: {e}")
    
    def _compute_statistics(self):
        """Compute and display summary statistics from the JSON data."""
        try:
            import json as jsonlib
            
            json_files = sorted(JSON_DIR.glob("*.json"))
            if not json_files:
                return
            
            total_units = 0
            total_rooms = 0
            total_area = 0.0
            total_heated_area = 0.0
            room_type_counts = {}
            detail_counts = {}
            areas_per_unit = []
            rooms_per_unit = []
            
            for jf in json_files:
                with open(jf, encoding="utf-8") as f:
                    data = jsonlib.load(f)
                
                total_units += 1
                ruimten = data.get("ruimten", [])
                unit_area = 0.0
                rooms_per_unit.append(len(ruimten))
                
                for r in ruimten:
                    total_rooms += 1
                    opp = r.get("oppervlakte", 0)
                    total_area += opp
                    unit_area += opp
                    if r.get("verwarmd"):
                        total_heated_area += opp
                    
                    soort = r.get("soort", {}).get("naam", "Onbekend")
                    room_type_counts[soort] = room_type_counts.get(soort, 0) + 1
                    
                    detail = r.get("detailSoort", {}).get("naam", "Onbekend")
                    detail_counts[detail] = detail_counts.get(detail, 0) + 1
                
                areas_per_unit.append(unit_area)
            
            avg_area = total_area / total_units if total_units else 0
            avg_rooms = total_rooms / total_units if total_units else 0
            min_area = min(areas_per_unit) if areas_per_unit else 0
            max_area = max(areas_per_unit) if areas_per_unit else 0
            
            lines = []
            lines.append("=" * 60)
            lines.append("  STATISTIEKEN OVERZICHT")
            lines.append("=" * 60)
            lines.append("")
            lines.append(f"  Totaal eenheden:             {total_units}")
            lines.append(f"  Totaal ruimten:              {total_rooms}")
            lines.append(f"  Gemiddeld ruimten/eenheid:   {avg_rooms:.1f}")
            lines.append("")
            lines.append(f"  Totaal oppervlakte:          {total_area:.1f} m²")
            lines.append(f"  Verwarmd oppervlakte:        {total_heated_area:.1f} m²")
            lines.append(f"  Gem. oppervlakte/eenheid:    {avg_area:.1f} m²")
            lines.append(f"  Min. oppervlakte:            {min_area:.1f} m²")
            lines.append(f"  Max. oppervlakte:            {max_area:.1f} m²")
            lines.append("")
            lines.append("-" * 40)
            lines.append("  RUIMTESOORTEN")
            lines.append("-" * 40)
            for soort, count in sorted(room_type_counts.items(), key=lambda x: -x[1]):
                lines.append(f"    {soort:<30s} {count:>4d}")
            lines.append("")
            lines.append("-" * 40)
            lines.append("  DETAIL RUIMTESOORTEN")
            lines.append("-" * 40)
            for detail, count in sorted(detail_counts.items(), key=lambda x: -x[1]):
                lines.append(f"    {detail:<30s} {count:>4d}")
            lines.append("")
            lines.append("=" * 60)
            
            text = "\n".join(lines)
            self.stats_view.configure(state=tk.NORMAL)
            self.stats_view.delete(1.0, tk.END)
            self.stats_view.insert(1.0, text)
            self.stats_view.configure(state=tk.DISABLED)
            self._log_callback("✓ Statistieken berekend")
        except Exception as e:
            self._log_callback(f"⚠ Kon statistieken niet berekenen: {e}")
    
    def _go_to_editor(self):
        """Switch to editor tab."""
        self.notebook.select(self.editor_tab)
    
    def _clear_log(self):
        """Clear log."""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.log_buffer = StringIO()
    
    def _refresh_recommendations_list(self):
        """Refresh list of available units for recommendations."""
        try:
            json_files = sorted(JSON_DIR.glob("*.json"))
            names = [f.stem for f in json_files]
            self.rec_combo['values'] = names
            if names:
                self.rec_combo.current(0)
                self._display_recommendations()
            
            # Test which units have working recommendations
            working_units = []
            failed_units = []
            for unit_id in names[:5]:  # Test first 5 for quick feedback
                result = self.backend.get_recommendations_for_unit(unit_id)
                if result.get("success"):
                    working_units.append(unit_id)
                else:
                    failed_units.append(unit_id)
            
            if failed_units:
                msg = (f"✓ {len(names)} eenheden beschikbaar voor aanbevelingen\n"
                       f"   {len(working_units)} van {len(names[:5])} geteste eenheden hebben werkende aanbevelingen")
                self._log_callback(msg)
            else:
                self._log_callback(f"✓ {len(names)} eenheden beschikbaar voor aanbevelingen")
        except Exception as e:
            messagebox.showerror("Fout", f"Kon eenheden niet laden: {e}")
            self._log_callback(f"✗ Fout bij laden van eenheden: {e}")
    
    def _display_recommendations(self):
        """Display recommendations for the selected unit."""
        try:
            selected_unit = self.rec_combo.get()
            if not selected_unit:
                return
            
            self.recommendations_view.configure(state=tk.NORMAL)
            self.recommendations_view.delete(1.0, tk.END)
            
            # Show loading message
            self.recommendations_view.insert(tk.END, "⏳ Aanbevelingen genereren...\n")
            self.recommendations_view.configure(state=tk.DISABLED)
            self.root.update()
            
            # Get recommendations from backend
            result = self.backend.get_recommendations_for_unit(selected_unit)
            
            self.recommendations_view.configure(state=tk.NORMAL)
            self.recommendations_view.delete(1.0, tk.END)
            
            if not result.get("success"):
                error_msg = result.get('error', 'Onbekende fout')
                # Check if it's an optimization module error
                if "douchebak" in error_msg.lower() or "attribute" in error_msg.lower():
                    self.recommendations_view.insert(tk.END, 
                        f"⚠ Opmerking voor eenheid {selected_unit}:\n\n"
                        f"De aanbevelingen kunnen niet worden gegenereerd vanwege ontbrekende\n"
                        f"bouwelelementgegevens in de woningwaarderingslibrary.\n\n"
                        f"Volgende stappen:\n"
                        f"1. Zorg dat alle CSV-gegevens volledig zijn ingevuld\n"
                        f"2. Klik '🤖 Auto-fill standaardwaarden' in de Dashboard\n"
                        f"3. Regenereer de JSON-bestanden\n\n"
                        f"Details: {error_msg}\n")
                else:
                    self.recommendations_view.insert(tk.END, f"❌ Fout: {error_msg}\n")
                self.recommendations_view.configure(state=tk.DISABLED)
                self._log_callback(f"⚠ {error_msg}")
                return
            
            recommendations = result.get("recommendations", [])
            
            # Format recommendations
            lines = []
            lines.append("=" * 100)
            lines.append(f"  AANBEVELINGEN VOOR EENHEID {selected_unit}")
            lines.append("=" * 100)
            
            if not recommendations:
                lines.append("\n✓ Geen aanbevelingen - deze eenheid is al optimaal!")
            else:
                lines.append(f"\n📋 {len(recommendations)} aanbevelingen gevonden:\n")
                
                for i, rec in enumerate(recommendations, 1):
                    lines.append("-" * 100)
                    lines.append(f"\n#{i} {rec.get('title', 'Onbekend')}")
                    lines.append(f"   Categorie: {rec.get('category', '-')}")
                    lines.append(f"   Score verhoging: +{rec.get('estimated_score_gain', 0):.1f} punten")
                    lines.append(f"   Inspanning: {rec.get('implementation_effort', '-')}")
                    lines.append(f"   Geschatte kosten: {rec.get('estimated_cost_indication', '-')}")
                    
                    description = rec.get('description', '')
                    lines.append(f"\n   Beschrijving:")
                    for line in description.split('\n'):
                        lines.append(f"   {line}")
                    
                    criteria = rec.get('affected_criteria', [])
                    if criteria:
                        lines.append(f"\n   Betrokken criteria:")
                        for crit in criteria:
                            lines.append(f"     • {crit}")
                    
                    lines.append("")
            
            lines.append("\n" + "=" * 100)
            
            # Insert text
            text = "\n".join(lines)
            self.recommendations_view.insert(1.0, text)
            self.recommendations_view.configure(state=tk.DISABLED)
            
            self._log_callback(f"✓ Aanbevelingen geladen voor eenheid {selected_unit}: {len(recommendations)} gevonden")
        
        except Exception as e:
            self.recommendations_view.configure(state=tk.NORMAL)
            self.recommendations_view.delete(1.0, tk.END)
            self.recommendations_view.insert(tk.END, f"❌ Fout: {e}")
            self.recommendations_view.configure(state=tk.DISABLED)
            self._log_callback(f"✗ Fout bij weergeven aanbevelingen: {e}")


def main():
    root = tk.Tk()
    gui = PipelineGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
