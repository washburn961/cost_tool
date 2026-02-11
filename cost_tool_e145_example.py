"""
File: cost_tool_example.py
Aircraft Direct Operating Cost Tool - Example Usage

Author: Gabriel Bortoletto Molz
Date: February 9, 2026

This example demonstrates the calculation of Direct Operating Costs (DOC)
for a representative narrow-body commercial aircraft (Boeing 737-800 class).
"""

import designTool_learis as dt
import matplotlib.pyplot as plt
import numpy as np
from cost_tool import AircraftParameters, MethodParameters, calculate_costs


def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


airplane = dt.standard_airplane('ERJ_145_XR')
airplane = dt.analyze(airplane)

# ========== ERJ_145_XR Aircraft Configuration ==========
erj_145_xr = AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:20:00"),                    # Average block time per flight
    flight_time_hours=hhmmss_to_hours("2:05:13"),                   # Average flight time per flight
    flights_per_year=1, # THIS DOESNT MATTER
    
    # Weights
    maximum_takeoff_weight_kg=48501 / 2.205,        # MTOW
    operational_empty_weight_kg=27550 / 2.205,      # OEW
    engine_weight_kg=751.6,
    fuel_weight_kg=2664,                    # Fuel per flight (average)
    payload_weight_kg=5403,                # Typical payload
    
    # Mission
    range_nm=689,                          # Average stage length
    
    # Engine specifications
    engine_count=2,
    bypass_ratio=4.7,
    overall_pressure_ratio=20,
    compressor_stages=9,
    engine_shafts=2,
    takeoff_thrust_per_engine_N=39670,
    
    # Crew
    cockpit_crew_count=2,
    cabin_crew_count=1,
    
    # Pricing (optional - will be estimated if not provided)
    aircraft_delivery_price_usd=None,        # Will be estimated from OEW
    engine_price_usd=None                    # Will be estimated from thrust
)

# ========== Method Parameters (AEA 1989a defaults) ==========
params = MethodParameters()  # Uses all default values

# ========== Calculate Direct Operating Costs ==========
erj_145_xr_result = calculate_costs(erj_145_xr, params, target_year=2025)

print("\n========== Cost Breakdown (Per Flight) ERJ-145 XR ==========")
print(f"OEW: {erj_145_xr.operational_empty_weight_kg:.2f} kg - {erj_145_xr.operational_empty_weight_kg * 2.20462:.2f} lbs")
print(f"MTOW: {erj_145_xr.maximum_takeoff_weight_kg:.2f} kg - {erj_145_xr.maximum_takeoff_weight_kg * 2.20462:.2f} lbs")
print(f"Fees & Charges:  ${erj_145_xr_result.per_flight.fees_and_charges:,.2f}")
print(f"Crew:            ${erj_145_xr_result.per_flight.crew:,.2f}")
print(f"Maintenance:     ${erj_145_xr_result.per_flight.maintenance:,.2f}")
print(f"Fuel:            ${erj_145_xr_result.per_flight.fuel:,.2f}")
print(f"Cash Operating Cost Per Flight: ${erj_145_xr_result.per_flight.fees_and_charges + erj_145_xr_result.per_flight.crew + erj_145_xr_result.per_flight.maintenance + erj_145_xr_result.per_flight.fuel:,.2f}")
print(f"{'='*50}")