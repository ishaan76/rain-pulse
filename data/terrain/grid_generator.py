"""AquaAlert AI — Agent 2: Geospatial Grid Generator.

Generates standardized topographical grid cells with elevation, slope,
and drainage attributes for pilot monitoring areas.
"""

from typing import List, Dict
from backend.contracts import GridCell


PILOT_AREA_CELLS: Dict[str, List[Dict[str, Any]]] = {
    "Delhi NCR": [
        {"cell_id": "DEL_01", "name": "Minto Bridge Underpass", "lat": 28.6328, "lon": 77.2223, "elev": 198.0, "slope": 1.1, "drain_dist": 750.0, "drain_dens": 0.25, "hist_risk": 0.95},
        {"cell_id": "DEL_02", "name": "ITO Ring Road Junction", "lat": 28.6289, "lon": 77.2435, "elev": 204.0, "slope": 1.4, "drain_dist": 620.0, "drain_dens": 0.35, "hist_risk": 0.85},
        {"cell_id": "DEL_03", "name": "Kashmere Gate ISBT", "lat": 28.6675, "lon": 77.2300, "elev": 202.0, "slope": 1.3, "drain_dist": 580.0, "drain_dens": 0.30, "hist_risk": 0.80},
        {"cell_id": "DEL_04", "name": "AIIMS Flyover Depression", "lat": 28.5672, "lon": 77.2100, "elev": 215.0, "slope": 1.8, "drain_dist": 400.0, "drain_dens": 0.55, "hist_risk": 0.60},
        {"cell_id": "DEL_05", "name": "Connaught Place Inner Circle", "lat": 28.6315, "lon": 77.2167, "elev": 218.0, "slope": 2.2, "drain_dist": 300.0, "drain_dens": 0.70, "hist_risk": 0.40},
        {"cell_id": "DEL_06", "name": "Dhaula Kuan Ridge", "lat": 28.5921, "lon": 77.1607, "elev": 238.0, "slope": 4.5, "drain_dist": 250.0, "drain_dens": 0.80, "hist_risk": 0.20},
        {"cell_id": "DEL_07", "name": "Lajpat Nagar Ring Road", "lat": 28.5700, "lon": 77.2400, "elev": 208.0, "slope": 1.5, "drain_dist": 480.0, "drain_dens": 0.45, "hist_risk": 0.65},
        {"cell_id": "DEL_08", "name": "Sarai Kale Khan Basin", "lat": 28.5880, "lon": 77.2600, "elev": 201.0, "slope": 1.2, "drain_dist": 690.0, "drain_dens": 0.28, "hist_risk": 0.90},
    ],
    "Noida": [
        {"cell_id": "NOI_01", "name": "Sector 18 Commercial Hub", "lat": 28.5708, "lon": 77.3261, "elev": 196.0, "slope": 1.2, "drain_dist": 720.0, "drain_dens": 0.28, "hist_risk": 0.90},
        {"cell_id": "NOI_02", "name": "Sector 62 IT Park Lowland", "lat": 28.6271, "lon": 77.3725, "elev": 198.0, "slope": 1.4, "drain_dist": 550.0, "drain_dens": 0.40, "hist_risk": 0.75},
        {"cell_id": "NOI_03", "name": "Botanical Garden Underpass", "lat": 28.5644, "lon": 77.3343, "elev": 195.0, "slope": 1.0, "drain_dist": 680.0, "drain_dens": 0.32, "hist_risk": 0.85},
        {"cell_id": "NOI_04", "name": "Noida-Greater Noida Expressway", "lat": 28.5100, "lon": 77.3800, "elev": 202.0, "slope": 2.1, "drain_dist": 350.0, "drain_dens": 0.65, "hist_risk": 0.45},
        {"cell_id": "NOI_05", "name": "Sector 137 Residential Pocket", "lat": 28.5030, "lon": 77.4080, "elev": 199.0, "slope": 1.6, "drain_dist": 480.0, "drain_dens": 0.50, "hist_risk": 0.55},
        {"cell_id": "NOI_06", "name": "Sector 15A Yamuna Bank", "lat": 28.5850, "lon": 77.3100, "elev": 193.0, "slope": 0.9, "drain_dist": 820.0, "drain_dens": 0.20, "hist_risk": 0.95},
    ],
    "Gurugram": [
        {"cell_id": "GUR_01", "name": "Hero Honda Chowk Underpass", "lat": 28.4350, "lon": 77.0100, "elev": 218.0, "slope": 1.0, "drain_dist": 850.0, "drain_dens": 0.20, "hist_risk": 0.95},
        {"cell_id": "GUR_02", "name": "Subhash Chowk Junction", "lat": 28.4410, "lon": 77.0420, "elev": 221.0, "slope": 1.3, "drain_dist": 680.0, "drain_dens": 0.30, "hist_risk": 0.85},
        {"cell_id": "GUR_03", "name": "IFFCO Chowk", "lat": 28.4720, "lon": 77.0725, "elev": 226.0, "slope": 1.8, "drain_dist": 450.0, "drain_dens": 0.50, "hist_risk": 0.60},
        {"cell_id": "GUR_04", "name": "Golf Course Road Underpass", "lat": 28.4610, "lon": 77.1020, "elev": 224.0, "slope": 1.4, "drain_dist": 590.0, "drain_dens": 0.42, "hist_risk": 0.70},
        {"cell_id": "GUR_05", "name": "Cyber City Transit Hub", "lat": 28.4950, "lon": 77.0890, "elev": 230.0, "slope": 2.5, "drain_dist": 310.0, "drain_dens": 0.75, "hist_risk": 0.35},
        {"cell_id": "GUR_06", "name": "Badshahpur Drain Culvert", "lat": 28.4120, "lon": 77.0450, "elev": 214.0, "slope": 0.8, "drain_dist": 920.0, "drain_dens": 0.18, "hist_risk": 0.98},
    ],
    "Ghaziabad": [
        {"cell_id": "GHA_01", "name": "Mohan Nagar Crossing", "lat": 28.6750, "lon": 77.3820, "elev": 208.0, "slope": 1.2, "drain_dist": 710.0, "drain_dens": 0.26, "hist_risk": 0.88},
        {"cell_id": "GHA_02", "name": "Sahibabad Industrial Area", "lat": 28.6590, "lon": 77.3600, "elev": 206.0, "slope": 1.1, "drain_dist": 760.0, "drain_dens": 0.22, "hist_risk": 0.92},
        {"cell_id": "GHA_03", "name": "Raj Nagar Extension Lowland", "lat": 28.7120, "lon": 77.4200, "elev": 212.0, "slope": 1.5, "drain_dist": 540.0, "drain_dens": 0.40, "hist_risk": 0.65},
        {"cell_id": "GHA_04", "name": "Hindon Barrage Approach", "lat": 28.6650, "lon": 77.4100, "elev": 204.0, "slope": 0.9, "drain_dist": 880.0, "drain_dens": 0.20, "hist_risk": 0.94},
        {"cell_id": "GHA_05", "name": "Kavi Nagar Commercial Belt", "lat": 28.6700, "lon": 77.4600, "elev": 216.0, "slope": 2.4, "drain_dist": 350.0, "drain_dens": 0.68, "hist_risk": 0.35},
    ],
}


def generate_pilot_grid(area_name: str) -> List[GridCell]:
    """Build standardized GridCell contracts for a given pilot area.

    Args:
        area_name: Pilot area (e.g. 'Delhi NCR', 'Noida', 'Gurugram', 'Ghaziabad').

    Returns:
        List of typed GridCell objects.
    """
    raw_cells = PILOT_AREA_CELLS.get(area_name, PILOT_AREA_CELLS["Delhi NCR"])
    return [
        GridCell(
            cell_id=c["cell_id"],
            name=c["name"],
            latitude=c["lat"],
            longitude=c["lon"],
            elevation=c["elev"],
            slope=c["slope"],
            drainage_distance=c["drain_dist"],
            drainage_density=c["drain_dens"],
            historical_risk=c["hist_risk"],
        )
        for c in raw_cells
    ]
