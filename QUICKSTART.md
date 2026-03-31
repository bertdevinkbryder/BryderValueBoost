# Quick Start Guide# QUICK START GUIDE - Woningwaardering RESTful API



## Installation## Installation



```bash### 1. Install Python (3.8 or higher)

pip install -r requirements.txtMake sure you have Python installed on your system.

```

### 2. Clone/Download the Project

## Run the API```bash

cd c:\Projects\DSGO

```bash```

python main.py

```### 3. Install Dependencies

```bash

API starts at: `http://localhost:8000`pip install -r requirements.txt

```

Interactive docs: `http://localhost:8000/docs`

This will install:

## Run Examples- FastAPI: Modern web framework

- Uvicorn: ASGI server

```bash- Pydantic: Data validation

python examples.py- woningwaardering: The core valuation library

```- pytest: Testing framework



## Run Tests## Running the API



```bash### Start the Server

# All tests```bash

pytestpython main.py

```

# Verbose output

pytest -vYou should see output like:

```

# Specific fileINFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

pytest test_api.py```



# With coverage### Access the API

pytest --cov

```**Interactive Documentation (Swagger UI):**

Visit: http://localhost:8000/docs

## API Endpoints

This provides an interactive interface to test all endpoints.

### Health Check

```bash**Alternative Documentation (ReDoc):**

curl http://localhost:8000/healthVisit: http://localhost:8000/redoc

```

## Basic Usage Examples

### Calculate Score

```bash### 1. Health Check

curl -X POST http://localhost:8000/calculate \```bash

  -H "Content-Type: application/json" \curl http://localhost:8000/health

  -d '{```

    "eenheid_data": {...},

    "peildatum": "2026-03-31"### 2. Calculate Woning Waarde

  }'```bash

```curl -X POST http://localhost:8000/calculate \

  -H "Content-Type: application/json" \

### Find Improvements  -d @- << 'EOF'

```bash{

curl -X POST http://localhost:8000/optimize \  "eenheid_data": {

  -H "Content-Type: application/json" \    "id": "woning_001",

  -d '{    "bouwjaar": 1975,

    "eenheid_data": {...},    "gebruiksoppervlakte": 100,

    "peildatum": "2026-03-31"    "woningwaarderingstelsel": "zelfstandige_woonruimten",

  }'    "adres": {

```      "straatnaam": "Teststraat",

      "huisnummer": "1",

### Batch Calculate      "postcode": "1234AB",

```bash      "woonplaats": {"naam": "Rotterdam"}

curl -X POST http://localhost:8000/batch-calculate \    },

  -H "Content-Type: application/json" \    "ruimten": [

  -d '[{...}, {...}]'      {

```        "id": "room_1",

        "soort": "vertrek",

## Using Docker        "detail_soort": "slaapkamer",

        "naam": "Slaapkamer",

```bash        "oppervlakte": 15,

docker build -t woningwaardering-api .        "inhoud": 37.5,

docker run -p 8000:8000 woningwaardering-api        "verwarmd": true

```      }

    ]

## Documentation  }

}

- **README.md** - Complete API documentationEOF

- **examples.py** - Runnable code examples```

- **CLEANUP_SUMMARY.md** - What was cleaned up

### 3. Find Optimization Opportunities

## Next Steps```bash

curl -X POST http://localhost:8000/optimize \

1. See examples.py for usage patterns  -H "Content-Type: application/json" \

2. Check README.md for full API reference  -d @- << 'EOF'

3. Review test files for more examples{

4. Deploy with Docker for production  "eenheid_data": {

    "id": "woning_001",
    "bouwjaar": 1975,
    "gebruiksoppervlakte": 80,
    "woningwaarderingstelsel": "zelfstandige_woonruimten",
    "adres": {
      "straatnaam": "Teststraat",
      "huisnummer": "1",
      "postcode": "1234AB",
      "woonplaats": {"naam": "Rotterdam"}
    },
    "ruimten": [
      {
        "id": "room_1",
        "soort": "vertrek",
        "detail_soort": "slaapkamer",
        "naam": "Slaapkamer",
        "oppervlakte": 12,
        "inhoud": 30,
        "verwarmd": true
      }
    ]
  }
}
EOF
```

## Using Python Examples

### Run Basic Examples
```bash
python examples.py
```

This demonstrates:
1. Basic calculation
2. Optimization suggestions
3. Batch processing

### Use Example Inputs
```python
from example_inputs import BASIC_UNIT, FAMILY_HOME, STUDIO
import requests

response = requests.post(
    "http://localhost:8000/calculate",
    json={"eenheid_data": BASIC_UNIT}
)
print(response.json())
```

## Project Structure

```
c:\Projects\DSGO\
├── main.py                 # FastAPI application & endpoints
├── models.py              # Pydantic data models
├── optimization.py        # Space exploration & optimization logic
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── examples.py            # Example usage scripts
├── example_inputs.py      # Example housing unit data
├── test_api.py            # Unit tests
├── README.md              # Full documentation
└── QUICKSTART.md          # This file
```

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check API status |
| POST | `/calculate` | Calculate woning waarde score |
| POST | `/optimize` | Find improvement opportunities |
| POST | `/batch-calculate` | Process multiple units |

## Input Format

The API expects housing unit data in the VERA standard format:

```json
{
  "eenheid_data": {
    "id": "unique_id",
    "bouwjaar": 1975,
    "gebruiksoppervlakte": 100,
    "woningwaarderingstelsel": "zelfstandige_woonruimten",
    "adres": {
      "straatnaam": "Straatnaam",
      "huisnummer": "42",
      "postcode": "1234AB",
      "woonplaats": {"naam": "Rotterdam"}
    },
    "ruimten": [
      {
        "id": "room_001",
        "soort": "vertrek",
        "detail_soort": "slaapkamer",
        "naam": "Room Name",
        "oppervlakte": 20,
        "inhoud": 50,
        "verwarmd": true
      }
    ]
  },
  "peildatum": "2026-03-26"
}
```

## Understanding the Output

### Score Output
- **detailed_json**: Complete scoring breakdown with all criteria
- **table_output**: Formatted table view of results

### Optimization Suggestions Include:
- **category**: Type of improvement (room, energy, facilities, etc.)
- **title**: Short description of the suggestion
- **estimated_score_gain**: How many points this could add
- **implementation_effort**: Low/Medium/High
- **estimated_cost_indication**: Rough cost estimate
- **affected_criteria**: Which scoring factors are affected

## Testing

Run the test suite:
```bash
pytest test_api.py -v
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'woningwaardering'"
- Solution: Run `pip install -r requirements.txt`

### Connection refused
- Make sure the API is running: `python main.py`
- Check that port 8000 is not in use

### Invalid input errors
- Check that your JSON matches the VERA standard format
- Ensure required fields are present (id, bouwjaar, adres, ruimten)

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Try examples**: Run `python examples.py`
3. **Integrate with your system**: Use the API endpoints in your application
4. **Extend functionality**: Add custom optimization rules in `optimization.py`

## Architecture Overview

```
┌─────────────────────┐
│   FastAPI Server    │
│   (main.py)         │
└──────────┬──────────┘
           │
      ┌────┴───┐
      │         │
   ┌──▼──┐  ┌──▼──────────┐
   │VERA │  │Optimization │
   │Data │  │Engine       │
   └──┬──┘  └──┬──────────┘
      │        │
      └────┬───┘
           │
      ┌────▼──────────────┐
      │Woningwaardering   │
      │Library            │
      └───────────────────┘
```

## Common Room Types (detail_soort)

- `slaapkamer` - Bedroom
- `woonkamer` - Living room
- `keuken` - Kitchen
- `badkamer` - Bathroom
- `toilet` - Toilet
- `hal` - Hallway
- `gang` - Corridor

## Resources

- **Documentation**: https://woningwaardering.readthedocs.io/
- **GitHub**: https://github.com/woonstadrotterdam/woningwaardering
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **VERA Standard**: https://www.coraveraonline.nl/

## Support

For issues with:
- **This API**: Check the README.md and troubleshooting section
- **Woningwaardering library**: See https://github.com/woonstadrotterdam/woningwaardering/issues
- **FastAPI**: See https://fastapi.tiangolo.com/
