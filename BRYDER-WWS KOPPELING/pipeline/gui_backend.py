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
import json as jsonlib
from datetime import date
import platform
import os
import time

# Windows workaround: add dummy tzset if it doesn't exist
if platform.system() == "Windows" and not hasattr(time, 'tzset'):
    time.tzset = lambda: None


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
            df.to_csv(EENHEDEN_CSV, sep=";", index=False, encoding="utf-8-sig")
        elif csv_type == "ruimten":
            df.to_csv(RUIMTEN_CSV, sep=";", index=False, encoding="utf-8-sig")
        elif csv_type == "mapping":
            df.to_csv(MAPPING_CSV, sep=";", index=False, encoding="utf-8-sig")
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
    
    def get_recommendations_for_unit(self, eenheid_id: str) -> dict:
        """
        Get optimization recommendations for a specific housing unit.
        
        Returns:
            {
                "success": bool,
                "eenheid_id": str,
                "recommendations": [
                    {
                        "category": str,
                        "title": str,
                        "description": str,
                        "estimated_score_gain": float,
                        "implementation_effort": str,
                        "estimated_cost_indication": str,
                        "affected_criteria": [str]
                    },
                    ...
                ]
            }
        """
        try:
            json_file = JSON_DIR / f"{eenheid_id}.json"
            if not json_file.exists():
                return {
                    "success": False,
                    "recommendations": [],
                    "error": f"Geen JSON gevonden voor {eenheid_id}"
                }
            
            # Load JSON data
            with open(json_file, encoding="utf-8") as f:
                eenheid_data = jsonlib.load(f)
            
            # Normalize JSON data to ensure required fields exist
            eenheid_data = self._normalize_eenheid_data(eenheid_data)
            
            # Import optimization module from the parent directory
            import sys
            parent_dir = str(Path(__file__).parent.parent.parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            try:
                from optimization import find_optimization_opportunities
                from woningwaardering import Woningwaardering
                from woningwaardering.vera.bvg.generated import EenhedenEenheid
            except ImportError as import_err:
                error_msg = str(import_err)
                if "woningwaardering" in error_msg:
                    return {
                        "success": False,
                        "recommendations": [],
                        "error": f"woningwaardering module niet geïnstalleerd. Voer uit: pip install woningwaardering>=4.2.0"
                    }
                else:
                    return {
                        "success": False,
                        "recommendations": [],
                        "error": f"Kon modules niet laden: {error_msg}"
                    }
            
            try:
                # Parse to EenhedenEenheid
                eenheid = EenhedenEenheid.model_validate(eenheid_data)
                
                # Get baseline score and recommendations
                wws = Woningwaardering(peildatum=date.today())
                baseline_result = wws.waardeer(eenheid)
                
                recommendations = find_optimization_opportunities(
                    eenheid=eenheid,
                    wws=wws,
                    baseline_result=baseline_result,
                    peildatum=date.today(),
                    max_suggestions=10
                )
                
                # Convert to dict format
                recommendations_list = []
                for rec in recommendations:
                    rec_dict = {
                        "category": str(rec.category),
                        "title": rec.title,
                        "description": rec.description,
                        "estimated_score_gain": rec.estimated_score_gain,
                        "implementation_effort": rec.implementation_effort,
                        "estimated_cost_indication": rec.estimated_cost_indication or "-",
                        "affected_criteria": rec.affected_criteria or []
                    }
                    recommendations_list.append(rec_dict)
                
                return {
                    "success": True,
                    "eenheid_id": eenheid_id,
                    "recommendations": recommendations_list
                }
            
            except Exception as validation_error:
                # If validation fails due to WOZ, attempt to fix it
                error_str = str(validation_error)
                if "woz" in error_str.lower():
                    try:
                        # Fix WOZ and retry
                        if not eenheid_data.get("wozEenheden") or not eenheid_data["wozEenheden"]:
                            total_area = sum(r.get("oppervlakte", 0) for r in eenheid_data.get("ruimten", []))
                            default_woz = total_area * 4000 if total_area > 0 else 50000
                            eenheid_data["wozEenheden"] = [{
                                "vastgesteldeWaarde": default_woz,
                                "waardepeildatum": "2025-01-01"
                            }]
                        
                        # Retry validation
                        eenheid = EenhedenEenheid.model_validate(eenheid_data)
                        
                        wws = Woningwaardering(peildatum=date.today())
                        baseline_result = wws.waardeer(eenheid)
                        
                        recommendations = find_optimization_opportunities(
                            eenheid=eenheid,
                            wws=wws,
                            baseline_result=baseline_result,
                            peildatum=date.today(),
                            max_suggestions=10
                        )
                        
                        recommendations_list = []
                        for rec in recommendations:
                            rec_dict = {
                                "category": str(rec.category),
                                "title": rec.title,
                                "description": rec.description,
                                "estimated_score_gain": rec.estimated_score_gain,
                                "implementation_effort": rec.implementation_effort,
                                "estimated_cost_indication": rec.estimated_cost_indication or "-",
                                "affected_criteria": rec.affected_criteria or []
                            }
                            recommendations_list.append(rec_dict)
                        
                        return {
                            "success": True,
                            "eenheid_id": eenheid_id,
                            "recommendations": recommendations_list
                        }
                    except Exception as retry_error:
                        return {
                            "success": False,
                            "recommendations": [],
                            "error": f"Fout bij genereren aanbevelingen (na WOZ fix): {retry_error}"
                        }
                else:
                    return {
                        "success": False,
                        "recommendations": [],
                        "error": f"Fout bij genereren aanbevelingen: {validation_error}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "recommendations": [],
                "error": str(e)
            }
    
    def _normalize_eenheid_data(self, data: dict) -> dict:
        """
        Normalize JSON data to ensure all required fields exist and are not None.
        Ensures compatibility with older JSON files that may be missing fields.
        """
        # Ensure list fields are never None
        if data.get("energieprestaties") is None:
            data["energieprestaties"] = []
        if data.get("ruimten") is None:
            data["ruimten"] = []
        if data.get("monumenten") is None:
            data["monumenten"] = []
        if data.get("installaties") is None:
            data["installaties"] = []
        if data.get("bouwkundigeElementen") is None:
            data["bouwkundigeElementen"] = []
        
        # Ensure WOZ is valid and complete
        if not data.get("wozEenheden") or len(data.get("wozEenheden", [])) == 0:
            # Calculate from room areas if WOZ is missing
            try:
                total_area = sum(r.get("oppervlakte", 0) for r in data.get("ruimten", []))
                default_woz = total_area * 4000 if total_area > 0 else 50000
                data["wozEenheden"] = [{
                    "vastgesteldeWaarde": default_woz,
                    "waardepeildatum": "2025-01-01"
                }]
            except:
                data["wozEenheden"] = [{
                    "vastgesteldeWaarde": 50000,
                    "waardepeildatum": "2025-01-01"
                }]
        else:
            # Ensure each WOZ entry has a date
            for woz in data["wozEenheden"]:
                if "waardepeildatum" not in woz:
                    woz["waardepeildatum"] = "2025-01-01"
        
        # Ensure each ruimte has required fields
        for ruimte in data.get("ruimten", []):
            if ruimte.get("bouwkundigeElementen") is None:
                ruimte["bouwkundigeElementen"] = []
            if ruimte.get("installaties") is None:
                ruimte["installaties"] = []
        
        return data


# Global backend instance
_backend: Optional[PipelineBackend] = None

def get_backend(output_callback: Optional[Callable] = None) -> PipelineBackend:
    """Get or create the global backend instance."""
    global _backend
    if _backend is None:
        _backend = PipelineBackend(output_callback)
    return _backend
