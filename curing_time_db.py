"""
Database of curing times and waiting intervals for flooring materials.
All values are theoretical and based on TDS data at +20°C (standard conditions).
Created for project scheduling logic.
"""

# Dict structure:
# "Material Name exactly as in systems_db.json": {
#   "min_overcoating_time_h": float,  # Min hours before next liquid layer
#   "foot_traffic_h": float,         # Hours before able to walk on (for broadcasting or final access)
#   "full_cure_days": float          # Days for full mechanical/chemical resistance
# }

CURING_TIMES = {
    # --- SIKA SYSTEMS ---
    # Epoxy / PU based
    "Sikafloor®-151": {
        "min_overcoating_time_h": 12.0, # At +20C
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Sikafloor®-161": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Sikafloor®-377": {
        "min_overcoating_time_h": 12.0, # Base coat
        "foot_traffic_h": 24.0,         # Before broadcasting or overcoating
        "full_cure_days": 7.0
    },
    "Sikafloor®-359 N": {
        "min_overcoating_time_h": 18.0, # Hard to overcoat itself, usually top coat
        "foot_traffic_h": 24.0,         # To traffic
        "full_cure_days": 7.0
    },
    "Sikafloor®-378": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Sikafloor®-264": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Sikafloor®-264 (seal coat)": { # Explicit name from recipe
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    # MMA based (Pronto) - ULTRA FAST
    "Sikafloor®-10 / 11 Pronto": {
        "min_overcoating_time_h": 1.0,  # ~60 min at +20C
        "foot_traffic_h": 1.0,
        "full_cure_days": 0.08          # ~2 hours
    },
    "Sikafloor®-14 Pronto": {
        "min_overcoating_time_h": 1.0,  # Intermediate
        "foot_traffic_h": 1.0,          # Before broadcast
        "full_cure_days": 0.08
    },
    "Sikafloor®-18 Pronto": {
        "min_overcoating_time_h": 1.0,
        "foot_traffic_h": 1.0,          # To traffic
        "full_cure_days": 0.08
    },

    # --- MAPEI SYSTEMS (Standard data at +23°C) ---
    "Primer SN": {
        "min_overcoating_time_h": 12.0, # (Range 12-24)
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Mapefloor PU 400": {
        "min_overcoating_time_h": 12.0, # Base coat
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Mapefloor Finish 451": {
        "min_overcoating_time_h": 24.0, # Usually final layer
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Mapefloor I 300 SL": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },
    "Mapefloor I 300 SL (colored)": { # Explicit name from recipe
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 24.0,
        "full_cure_days": 7.0
    },

    # --- MC-BAUCHEMIE SYSTEMS ---
    # Standard / Epoxy
    "MC-DUR 1320 VK": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 16.0,
        "full_cure_days": 7.0
    },
    "MC-DUR 2211 MB": {
        "min_overcoating_time_h": 12.0, # Combined seal/wear
        "foot_traffic_h": 16.0,         # Before broadcast
        "full_cure_days": 7.0
    },
    "MC-DUR 1311": {
        "min_overcoating_time_h": 12.0, # Top coat
        "foot_traffic_h": 16.0,         # To traffic
        "full_cure_days": 7.0
    },
    "MC-DUR 1322": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 16.0,
        "full_cure_days": 7.0
    },
    "MC-DUR 1200 VK": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 16.0,
        "full_cure_days": 7.0
    },
    "MC-DUR VK + quartz sand": { # Scratch coat explicitly named
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 16.0,
        "full_cure_days": 7.0
    },
    "MC-DUR 1252": {
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 16.0,
        "full_cure_days": 7.0
    },
    "MC-DUR 1252 + quartz sand": { # Wear layer explicitly named
        "min_overcoating_time_h": 12.0,
        "foot_traffic_h": 16.0,
        "full_cure_days": 7.0
    },
    # KineticBoost / Fast Track
    "MC-DUR 1311 VK": {
        "min_overcoating_time_h": 3.0,  # KineticBoost technology
        "foot_traffic_h": 4.0,
        "full_cure_days": 1.0          # Very rapid
    },
    "MC-DUR 2211 WL": {
        "min_overcoating_time_h": 3.0,  # Wear layer fast
        "foot_traffic_h": 4.0,
        "full_cure_days": 1.0
    },

    # --- Aggregates (No curing time needed, added for safety) ---
    "Quartz Sand 0.6-1.2 mm": {"min_overcoating_time_h": 0.0, "foot_traffic_h": 0.0, "full_cure_days": 0.0},
    "Quartz Sand 0.5 mm": {"min_overcoating_time_h": 0.0, "foot_traffic_h": 0.0, "full_cure_days": 0.0},
    "Quartz sand 0.3-0.8 mm": {"min_overcoating_time_h": 0.0, "foot_traffic_h": 0.0, "full_cure_days": 0.0},
    "Quartz sand 0.1-0.3 mm": {"min_overcoating_time_h": 0.0, "foot_traffic_h": 0.0, "full_cure_days": 0.0},
}