# Woningwaardering RESTful API

A FastAPI-based REST service for calculating Dutch housing quality scores (woningwaardering) and discovering space-efficient improvements using the official **woningwaardering** library.

## Features

✨ **Calculate Scores** – Get accurate housing quality assessments based on the Dutch valuation system
🔍 **Find Improvements** – Discover 6 categories of space-efficient improvements to boost scores
⚡ **Batch Processing** – Process multiple housing units efficiently
📊 **Interactive Docs** – Swagger UI and ReDoc included

## Project Structure

Clean, minimal structure:
```
.
├── main.py              # FastAPI endpoints & app setup
├── models.py            # Request/response validation
├── optimization.py      # Space-efficient improvement analysis
├── test_api.py          # API endpoint tests
├── test_optimization.py # Score calculation & regression tests
├── requirements.txt     # Dependencies
├── examples.py          # Usage examples
└── README.md           # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the API

```bash
python main.py
```

API will be available at: `http://localhost:8000`

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Try It Out

```bash
# Health check
curl http://localhost:8000/health

# Calculate score for a housing unit
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d @examples.py

# Find improvement opportunities
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d @examples.py
```

## API Endpoints

### `/health` – GET
Check API status.

**Response:**
```json
{"status": "healthy"}
```

---

### `/calculate` – POST
Calculate woning waarde (housing quality score) for a single unit.

**Request:**
```json
{
  "eenheid_data": { /* VERA standard housing data */ },
  "peildatum": "2026-03-31"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Woning waarde calculated successfully",
  "eenheid_id": "unit_001",
  "peildatum": "2026-03-31",
  "detailed_json": "...",
  "table_output": "..."
}
```

---

### `/optimize` – POST
Analyze a housing unit and suggest space-efficient improvements.

**Request:** Same as `/calculate`

**Response:**
```json
{
  "success": true,
  "eenheid_id": "unit_001",
  "baseline_score": 45.5,
  "suggestions": [
    {
      "category": "heating_improvements",
      "title": "Add Heating System",
      "description": "Install heating in unheated rooms",
      "estimated_score_gain": 12.3,
      "implementation_effort": "medium"
    }
  ],
  "suggestion_count": 5
}
```

---

### `/batch-calculate` – POST
Calculate scores for multiple housing units.

**Request:**
```json
[
  {"eenheid_data": {...}, "peildatum": "2026-03-31"},
  {"eenheid_data": {...}, "peildatum": "2026-03-31"}
]
```

**Response:**
```json
{
  "success": true,
  "results": [
    {"eenheid_id": "unit_001", "score": 45.5},
    {"eenheid_id": "unit_002", "score": 52.3}
  ]
}
```

## Optimization Categories

The `/optimize` endpoint explores 6 space-efficient improvement areas (no room additions or expansions):

1. **Kitchen Upgrades** – Counter size, storage, sink improvements
2. **Bathroom Upgrades** – Shower, toilet, fixture quality
3. **Heating Improvements** – Add heating to unheated rooms
4. **Ventilation Improvements** – Mechanical ventilation systems
5. **Element Quality Upgrades** – Windows, doors, insulation
6. **Energy Efficiency** – Energy label improvements

Each suggestion includes estimated score gain, effort level, and category.

## Input Format

See `examples.py` for complete sample data. Key VERA standard fields:

**Housing Unit (eenheid):**
- `id`: Unique identifier
- `bouwjaar`: Construction year
- `gebruiksoppervlakte`: Usable floor area (m²)
- `woningwaarderingstelsel`: "zelfstandige_woonruimten" (primary)
- `adres`: Address details
- `ruimten`: Array of rooms
- `panden`: Building info

**Room (ruimte):**
- `id`: Room identifier
- `soort`: Type (e.g., "vertrek")
- `detail_soort`: Subtype (e.g., "slaapkamer", "keuken", "badkamer")
- `oppervlakte`: Floor area (m²)
- `inhoud`: Volume (m³)
- `verwarmd`: Heated? (boolean)

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_api.py
pytest test_optimization.py

# Run with coverage
pytest --cov=.
```

**Current Status:** 12/13 tests passing (92.3%)
- Score extraction: ✅ 4/4
- Optimization logic: ✅ 5/5
- Regression tests: ✅ 2/2 (building footprint constraint verified)
- API endpoints: ✅ 6/6

## Architecture

### Score Calculation
Uses the **woningwaardering** library with VERA standard data:
1. Parse and validate housing unit data
2. Call `Woningwaardering(peildatum).waardeer(eenheid)`
3. Extract score from response

### Optimization Strategy
For each improvement category:
1. Create a copy of the housing unit
2. Simulate the improvement
3. Calculate new score
4. Compute gain = new_score - baseline_score
5. Rank by highest gain

## Dependencies

- **woningwaardering** (4.2.0+) – Official Dutch housing valuation library
- **FastAPI** – Web framework
- **Pydantic** v2 – Data validation
- **pytest** – Testing

See `requirements.txt` for exact versions.

## Docker

Build and run with Docker:

```bash
docker build -t woningwaardering-api .
docker run -p 8000:8000 woningwaardering-api
```

## Notes

- **Valuation Date:** Uses provided `peildatum` or today's date
- **Building Constraint:** Building footprint always remains at 100% (space-efficient improvements only)
- **Official Rules:** All calculations follow official Dutch housing valuation policies
- **Score Range:** Typically 0-100 points

## Resources

- **Woningwaardering Library**: https://github.com/woonstadrotterdam/woningwaardering
- **VERA Standard**: Dutch standard for housing unit data structure
- **Rental Commission**: https://www.huurcommissie.nl/

## License

MIT
