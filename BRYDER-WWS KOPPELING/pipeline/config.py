from pathlib import Path

# Paden
BASE_DIR = Path(__file__).resolve().parent.parent
HUISDATA_DIR = BASE_DIR / "huisdata" / "havensteder" / "Nieuwebouwen_Fascination_laatsteblok"
OUTPUT_DIR = BASE_DIR / "output"

EXCEL_PATH = HUISDATA_DIR / "fascinatio nieuwbouw 20250218.xlsx"
IFC_B2_PATH = HUISDATA_DIR / "FAS_PLE_BWK-B2.ifc"
IFC_B3_PATH = HUISDATA_DIR / "FAS_PLE_BWK-B3.ifc"

EENHEDEN_CSV = OUTPUT_DIR / "eenheden.csv"
RUIMTEN_CSV = OUTPUT_DIR / "ruimten.csv"
MAPPING_CSV = OUTPUT_DIR / "mapping.csv"
JSON_DIR = OUTPUT_DIR / "json"

# IFC ruimtenaam -> VERA codes mapping
# (ifc_longname_lower): (ruimtesoort_code, ruimtesoort_naam, detailsoort_code, detailsoort_naam, verwarmd)
ROOM_TYPE_MAP = {
    "woonkamer / keuken": ("VTK", "Vertrek", "WOO", "Woonkamer", True),
    "woonkamer/keuken": ("VTK", "Vertrek", "WOO", "Woonkamer", True),
    "slaapkamer 1": ("VTK", "Vertrek", "SLA", "Slaapkamer", True),
    "slaapkamer 2": ("VTK", "Vertrek", "SLA", "Slaapkamer", True),
    "slaapkamer": ("VTK", "Vertrek", "SLA", "Slaapkamer", True),
    "badkamer / toilet": ("VTK", "Vertrek", "BAD", "Badruimte", True),
    "badkamer/toilet": ("VTK", "Vertrek", "BAD", "Badruimte", True),
    "badkamer": ("VTK", "Vertrek", "BAD", "Badruimte", True),
    "hal": ("VRK", "Verkeersruimte", "HAL", "Hal", True),
    "entree": ("VRK", "Verkeersruimte", "HAL", "Hal", False),
    "berging / techniek": ("OVR", "Overige ruimtes", "BER", "Berging", False),
    "berging/techniek": ("OVR", "Overige ruimtes", "BER", "Berging", False),
    "technische ruimte": ("OVR", "Overige ruimtes", "TEC", "Technische ruimte", False),
    "mk warm": ("OVR", "Overige ruimtes", "MET", "Meterruimte", False),
    "mk koud": ("OVR", "Overige ruimtes", "MET", "Meterruimte", False),
    "meterkast warm": ("OVR", "Overige ruimtes", "MET", "Meterruimte", False),
    "meterkast koud": ("OVR", "Overige ruimtes", "MET", "Meterruimte", False),
    "cvz kast": ("OVR", "Overige ruimtes", "TEC", "Technische ruimte", False),
}

# WOZ-waarde schatting
WOZ_EUR_PER_M2 = 3200  # Geschatte WOZ-waarde per m2 (Capelle a/d IJssel nieuwbouw)

# Gemeenschappelijke ruimten (uitsluiten van appartement-groepering)
COMMON_SPACES = {
    "fietsenstalling",
    "hydrofoor + werkkkast",
    "hydrofoor + werkkast",
    "installatieruimte warmte/koude",
    "installatieruimte warmte / koude",
    "distributiestation / trafo",
    "distributiestation/trafo",
}
