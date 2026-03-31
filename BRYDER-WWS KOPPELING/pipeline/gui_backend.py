"""
GUI Backend - Refactored pipeline API for easy use in GUI applications.
Wraps existing pipeline functions and provides structured output.
"""

import io
import sys
from pathlib import Path
from contextlib import redirect_stdout
import pandas as pd
from typing import Optional, Callable

from pipeline.config import (
    EXCEL_PATH,
    IFC_B2_PATH,
    IFC_B3_PATH,
    EENHEDEN_CSV,
    RUIMTEN_CSV,
    MAPPING_CSV,
    JSON_DIR,
)
from pipeline.extract_excel import extract_eenheden
from pipeline.extract_ifc import extract_rooms_from_ifc, write_ruimten_csv
from pipeline.link_eenheden import link_ruimten_to_eenheden
from pipeline.csv_to_json import convert_to_json


class PipelineBackend:
    """Manages pipeline operations with structured output for GUI."""
    
    def __init__(self, output_callback: Optional[Callable] = None):
        """
        Initialize backend.
        
        Args:
            output_callback: Function to receive log messages: callback(message: str)
        """
        self.output_callback = output_callback or (lambda x: None)
        self.last_log = ""
    
    def _log(self, message: str):
        """Log a message to callback and store."""
        self.last_log += message + "\n"
        self.output_callback(message)
    
    def extract(self) -> dict:
        """
        Run extraction: Excel + IFC → CSVs.
        
        Returns:
            {
                "success": bool,
                "log": str,
                "eenheden_count": int,
                "ruimten_count": int,
                "mapped_count": int,
                "b2_apartments": int,
                "b3_apartments": int,
            }
        """
        self.last_log = ""
        
        try:
            self._log("=" * 60)
            self._log("STAP 1: Extractie naar CSV")
            self._log("=" * 60)
            
            # Excel extraction
            self._log("\n--- Excel extractie ---")
            try:
                extract_eenheden(EXCEL_PATH, EENHEDEN_CSV)
                self._log(f"✓ Excel geïmporteerd → {EENHEDEN_CSV}")
            except Exception as e:
                self._log(f"✗ Excel extractie mislukt: {e}")
                return {
                    "success": False,
                    "log": self.last_log,
                    "error": str(e)
                }
            
            # IFC extraction
            self._log("\n--- IFC extractie ---")
            try:
                apartments_b3 = extract_rooms_from_ifc(IFC_B3_PATH, "B3")
                apartments_b2 = extract_rooms_from_ifc(IFC_B2_PATH, "B2")
                all_apartments = apartments_b3 + apartments_b2
                rooms_b3 = sum(len(a["rooms"]) for a in apartments_b3)
                rooms_b2 = sum(len(a["rooms"]) for a in apartments_b2)
                write_ruimten_csv(all_apartments, RUIMTEN_CSV)
                self._log(f"✓ IFC B3 geïmporteerd → {len(apartments_b3)} appartementen, {rooms_b3} ruimten")
                self._log(f"✓ IFC B2 geïmporteerd → {len(apartments_b2)} appartementen, {rooms_b2} ruimten")
            except Exception as e:
                self._log(f"✗ IFC extractie mislukt: {e}")
                return {
                    "success": False,
                    "log": self.last_log,
                    "error": str(e)
                }
            
            # Link eenheden
            self._log("\n--- Koppeling ruimten <-> eenheden ---")
            try:
                link_ruimten_to_eenheden(EENHEDEN_CSV, RUIMTEN_CSV, MAPPING_CSV)
                self._log(f"✓ Koppeling succesvol → {MAPPING_CSV}")
            except Exception as e:
                self._log(f"✗ Koppeling mislukt: {e}")
                return {
                    "success": False,
                    "log": self.last_log,
                    "error": str(e)
                }
            
            # Count results
            eenheden_df = pd.read_csv(EENHEDEN_CSV, delimiter=";")
            ruimten_df = pd.read_csv(RUIMTEN_CSV, delimiter=";")
            mapping_df = pd.read_csv(MAPPING_CSV, delimiter=";")
            
            eenheden_count = len(eenheden_df)
            ruimten_count = len(ruimten_df)
            mapped_count = len(mapping_df)
            
            self._log(f"\n--- Resultaat ---")
            self._log(f"  {eenheden_count} eenheden")
            self._log(f"  {ruimten_count} ruimten")
            self._log(f"  {mapped_count} koppelingen")
            self._log(f"✓ Extractie voltooid!")
            
            return {
                "success": True,
                "log": self.last_log,
                "eenheden_count": eenheden_count,
                "ruimten_count": ruimten_count,
                "mapped_count": mapped_count,
                "b2_apartments": len(apartments_b2),
                "b3_apartments": len(apartments_b3),
            }
        
        except Exception as e:
            self._log(f"\n✗ Onverwachte fout: {e}")
            return {
                "success": False,
                "log": self.last_log,
                "error": str(e)
            }
    
    def json_convert(self) -> dict:
        """
        Convert CSVs to JSON files.
        
        Returns:
            {
                "success": bool,
                "log": str,
                "json_count": int,
            }
        """
        self.last_log = ""
        
        try:
            self._log("=" * 60)
            self._log("STAP 2: CSV → JSON conversie")
            self._log("=" * 60)
            
            if not EENHEDEN_CSV.exists():
                raise FileNotFoundError(f"{EENHEDEN_CSV} niet gevonden")
            if not RUIMTEN_CSV.exists():
                raise FileNotFoundError(f"{RUIMTEN_CSV} niet gevonden")
            
            JSON_DIR.mkdir(parents=True, exist_ok=True)
            
            self._log(f"\nConverteer naar JSON...")
            count = convert_to_json(EENHEDEN_CSV, RUIMTEN_CSV, JSON_DIR)
            self._log(f"✓ {count} JSON bestanden gegenereerd in {JSON_DIR}")
            
            return {
                "success": True,
                "log": self.last_log,
                "json_count": count,
            }
        
        except Exception as e:
            self._log(f"✗ Conversie mislukt: {e}")
            return {
                "success": False,
                "log": self.last_log,
                "error": str(e)
            }
    
    def read_csv(self, csv_type: str) -> pd.DataFrame:
        """Read a CSV file."""
        if csv_type == "eenheden":
            return pd.read_csv(EENHEDEN_CSV, delimiter=";")
        elif csv_type == "ruimten":
            return pd.read_csv(RUIMTEN_CSV, delimiter=";")
        elif csv_type == "mapping":
            return pd.read_csv(MAPPING_CSV, delimiter=";")
        else:
            raise ValueError(f"Unknown CSV type: {csv_type}")
    
    def save_csv(self, csv_type: str, df: pd.DataFrame):
        """Save a CSV file."""
        if csv_type == "eenheden":
            df.to_csv(EENHEDEN_CSV, delimiter=";", index=False, encoding="utf-8-sig")
        elif csv_type == "ruimten":
            df.to_csv(RUIMTEN_CSV, delimiter=";", index=False, encoding="utf-8-sig")
        elif csv_type == "mapping":
            df.to_csv(MAPPING_CSV, delimiter=";", index=False, encoding="utf-8-sig")
        else:
            raise ValueError(f"Unknown CSV type: {csv_type}")
    
    def get_status(self) -> dict:
        """Check which steps are complete."""
        return {
            "extract_done": EENHEDEN_CSV.exists() and RUIMTEN_CSV.exists() and MAPPING_CSV.exists(),
            "json_done": bool(list(JSON_DIR.glob("*.json"))) if JSON_DIR.exists() else False,
            "eenheden_path": str(EENHEDEN_CSV),
            "ruimten_path": str(RUIMTEN_CSV),
            "mapping_path": str(MAPPING_CSV),
            "json_dir": str(JSON_DIR),
        }
    
    def fill_defaults_eenheden(self) -> dict:
        """Fill default values for new eenheden entries."""
        try:
            df = self.read_csv("eenheden")
            
            # Fill common defaults for nieuwbouw
            df["bouwjaar"] = df["bouwjaar"].fillna(2025)
            df["klimaatbeheersing"] = df["klimaatbeheersing"].fillna("IND")
            df["energielabel"] = df["energielabel"].fillna("A")
            df["energieprestatie_soort"] = df["energieprestatie_soort"].fillna("EPE")
            df["monument"] = df["monument"].fillna("NEE")
            
            # WOZ default (scale by area if available)
            if "bruto_gebruiksoppervlakte_m2" in df.columns:
                from pipeline.config import WOZ_EUR_PER_M2
                df["woz_waarde"] = df["woz_waarde"].fillna(
                    df["bruto_gebruiksoppervlakte_m2"] * WOZ_EUR_PER_M2
                )
            
            self.save_csv("eenheden", df)
            self._log("✓ Standaardwaarden ingevuld voor eenheden")
            
            return {"success": True, "log": self.last_log}
        except Exception as e:
            self._log(f"✗ Fout bij invullen defaults: {e}")
            return {"success": False, "log": self.last_log, "error": str(e)}


# Global backend instance
_backend: Optional[PipelineBackend] = None

def get_backend(output_callback: Optional[Callable] = None) -> PipelineBackend:
    """Get or create the global backend instance."""
    global _backend
    if _backend is None:
        _backend = PipelineBackend(output_callback)
    return _backend
