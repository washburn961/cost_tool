"""
File: cost_tool_example.py
Aircraft Direct Operating Cost Tool - Example Usage

Author: Gabriel Bortoletto Molz
Date: February 9, 2026

This example demonstrates the calculation of Direct Operating Costs (DOC)
for a representative narrow-body commercial aircraft (Boeing 737-800 class).
"""

# import designTool_learis as dt
import matplotlib.pyplot as plt
import numpy as np
from cost_tool import FITTED_MAINTENANCE_PARAMS, AircraftParameters, MethodParameters, calculate_costs


def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


# airplane = dt.standard_airplane('CRJ200')
# airplane = dt.analyze(airplane)

# ========== CRJ_700 Aircraft Configuration ==========
crj_700 = AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:20:00"),                    # Average block time per flight
    flight_time_hours=hhmmss_to_hours("1:57:59"),                   # Average flight time per flight
    flights_per_year=1, # THIS DOESNT MATTER
    
    # Weights
    maximum_takeoff_weight_kg=75000 / 2.205,        # MTOW
    operational_empty_weight_kg=43712 / 2.205,      # OEW
    engine_weight_kg=1088,
    fuel_weight_kg=3514,                    # Fuel per flight (average)
    payload_weight_kg=8431,                # Typical payload
    
    # Mission
    range_nm=689,                          # Average stage length
    
    # Engine specifications
    engine_count=2,
    bypass_ratio=5,
    overall_pressure_ratio=28,
    compressor_stages=10,
    engine_shafts=2,
    takeoff_thrust_per_engine_N=61300,
    
    # Crew
    cockpit_crew_count=2,
    cabin_crew_count=1,
    
    # Pricing (optional - will be estimated if not provided)
    aircraft_delivery_price_usd=None,        # Will be estimated from OEW
    engine_price_usd=None                    # Will be estimated from thrust
)

# ========== Method Parameters (Fitted to 3 Regional Jets) ==========

params = MethodParameters(maintenance=FITTED_MAINTENANCE_PARAMS)

# ========== Calculate Direct Operating Costs ==========
crj_700_result = calculate_costs(crj_700, params, target_year=2025)

print("\n========== Cost Breakdown (Per Flight) CRJ-700 ==========")
print(f"OEW: {crj_700.operational_empty_weight_kg:.2f} kg - {crj_700.operational_empty_weight_kg * 2.20462:.2f} lbs")
print(f"MTOW: {crj_700.maximum_takeoff_weight_kg:.2f} kg - {crj_700.maximum_takeoff_weight_kg * 2.20462:.2f} lbs")
print(f"Fees & Charges:  ${crj_700_result.per_flight.fees_and_charges:,.2f}")
print(f"Crew:            ${crj_700_result.per_flight.crew:,.2f}")
print(f"Maintenance:     ${crj_700_result.per_flight.maintenance:,.2f}")
print(f"Fuel:            ${crj_700_result.per_flight.fuel:,.2f}")
print(f"Cash Operating Cost Per Flight: ${crj_700_result.per_flight.fees_and_charges + crj_700_result.per_flight.crew + crj_700_result.per_flight.maintenance + crj_700_result.per_flight.fuel:,.2f}")
print(f"{'='*50}")