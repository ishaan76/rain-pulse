# AquaAlert AI — Product, UX & Engineering Specification

## 1. Product Goal
AquaAlert is a flood/waterlogging risk intelligence dashboard.
The system combines:
- Rainfall and weather information
- Terrain/elevation information
- Slope
- Drainage-related information
- Historical/environmental vulnerability
to estimate localized waterlogging/flood risk for geographical grid cells over the next 0–6 hours.

### User-Facing Output
- **Risk Score**: 0–100
- **Risk Level**: LOW, MEDIUM, or HIGH
- **Explanation**: Primary risk drivers (Rainfall, Slope, Drainage, Elevation)
- **Recommended Action**: Clear operational action (e.g. "Avoid low-lying underpasses")

*Rule: Do not present prototype ML probabilities as scientifically calibrated probabilities of flooding.*

---

## 2. 6-Agent Architecture & Ownership

| Agent | Responsibility | Primary Directory |
|---|---|---|
| **Agent 1** | Weather & Rainfall Data Layer | `data/weather/` |
| **Agent 2** | Terrain & Drainage Geospatial Layer | `data/terrain/` |
| **Agent 3** | ML & Physics Hybrid Prediction Engine | `model/` |
| **Agent 4** | Backend Orchestration & Service Layer | `backend/` |
| **Agent 5** | Streamlit UI & Interactive PyDeck Map | `app/` |
| **Agent 6** | Testing, QA & Final Integration | `tests/` |

---

## 3. Technology Stack
- **Frontend**: Streamlit
- **Maps / Geospatial**: PyDeck
- **Data Processing**: pandas, numpy
- **Machine Learning**: scikit-learn, joblib
- **Validation**: Python dataclasses
- **HTTP / API Clients**: requests
- **Testing**: pytest
- **Code Quality**: ruff
