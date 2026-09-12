# 🌧️ AquaAlert AI — Hyper-Local Urban Flood Intelligence

> **Smart India Hackathon (SIH) Prototype**  
> *A 6-Agent Hybrid Hydrological & Machine Learning Architecture for Real-Time Waterlogging Risk Intelligence.*

---

## 🏛️ System Architecture & 6-Agent Ownership

```
                          ┌──────────────────────────┐
                          │   OPEN-METEO LIVE API    │
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │   Agent 1: Weather Layer │ (data/weather/)
                          └─────────────┬────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
     ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
     │  Copernicus DEM  │      │   OSM Drainage   │      │  Guaranteed Demo │
     │ (Elevation/Slope)│      │ (Distance/Density│      │  Offline Scenarios
     └────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
              │                         │                         │
              └─────────────────────────┼─────────────────────────┘
                                        ▼
                          ┌──────────────────────────┐
                          │  Agent 2: Terrain Layer  │ (data/terrain/)
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │  Agent 3: ML & Physics   │ (model/)
                          │  Prediction Subsystem    │
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │  Agent 4: Backend API &  │ (backend/)
                          │  Pipeline Orchestrator   │
                          └─────────────┬────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │  Agent 5: Streamlit UI & │ (app/)
                          │  3D PyDeck Risk Maps     │
                          └──────────────────────────┘
                                        │
                          ┌──────────────────────────┐
                          │  Agent 6: QA & Testing   │ (tests/)
                          └──────────────────────────┘
```

---

## 👥 6-Agent Directory Ownership Breakdown

| Agent | Responsibility | Primary Directory | Teammate Role |
|---|---|---|---|
| **Agent 1** | Weather & Rainfall Data Layer | `data/weather/` | Data Engineer (Meteorology) |
| **Agent 2** | Terrain & Drainage Geospatial Layer | `data/terrain/` | GIS / Geospatial Engineer |
| **Agent 3** | ML & Physics Hybrid Prediction Engine | `model/` | AI / ML Engineer |
| **Agent 4** | Backend Orchestration & Service Layer | `backend/` | Backend Systems Engineer |
| **Agent 5** | Streamlit UI & Interactive PyDeck Map | `app/` | Frontend / UX Engineer |
| **Agent 6** | Testing, QA & Final Integration | `tests/` | QA & Integration Lead |

---

## 🚀 Quickstart Guide (Run in 2 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Launch Streamlit Dashboard
```bash
streamlit run app/main.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## 🎯 1-Minute SIH Judge Demonstration Walkthrough

1. **Open AquaAlert**: Default loads to the **Overview** dashboard on the **Delhi NCR** basin.
2. **Review Current Risk KPI**: Point out the primary hazard score (e.g. `72 / 100 MEDIUM`) and telemetry stats (`Rainfall last 3h: 42 mm`, `8 hotspots detected`, `+3h peak expected`).
3. **Explore 3D Risk Map**: Show the interactive 3D PyDeck extruded columns. High-risk basins extrude into the air and glow crimson red (`HIGH`), while well-drained ridges remain green (`LOW`).
4. **Demonstrate "Why Is This High?" Attribution**:
   - In the **Sector Inspector**, select `Minto Bridge Underpass` or `Sector 18`.
   - Show the dynamic feature attribution bars: **Rainfall (42%)**, **Drainage (28%)**, **Slope (18%)**, **Elevation (12%)**.
   - Read the actionable recommendation: *"Avoid low-lying routes & subterranean corridors."*
5. **Switch Forecast to +3h**: Change the **Forecast Horizon** in the sidebar to `+3 hours`. Show judges how the system predicts waterlogging intensification before it occurs.
6. **Show Tab 3 (Forecast 0–6h)**: Walk judges through the tabular progression and precipitation surge curve.
7. **Toggle Live vs Demo Mode**: Explain the rock-solid offline fallback assurance ensuring zero crashes even under API outages.

---

## 🧪 Running Automated Test Suite
```bash
python -m pytest -v
```
All 23 unit, integration, and physics-monotonicity tests run and validate the complete pipeline.
