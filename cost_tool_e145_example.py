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
import cost_tool as ct


def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


# airplane = dt.standard_airplane('ERJ_145_XR')
# airplane = dt.analyze(airplane)

# ========== ERJ_145_XR Aircraft Configuration ==========
erj_145_xr = ct.AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:05:00"),                    # Average block time per flight
    flight_time_hours=hhmmss_to_hours("1:34:00"),                   # Average flight time per flight
    flights_per_year=None, # THIS DOESNT MATTER
    
    # Weights
    maximum_takeoff_weight_kg=48501 / 2.205,        # MTOW
    operational_empty_weight_kg=27550 / 2.205,      # OEW
    engine_weight_kg=751.6,
    fuel_weight_kg=1731,                    # Trip fuel
    payload_weight_kg=3800,                # Typical payload for 80% load factor
    
    # Mission
    range_nm=654,                          # Stage length
    
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

# ========== Method Parameters (Fitted to 3 Regional Jets) ==========
# Fitted simultaneously to ERJ-145 XR ($1,350), CRJ-700 ($1,450), CRJ-200 ($1,250)
# 10 parameters optimized, Overall RMSE: $21.75 across all aircraft
fitted_maintenance_params = ct.FITTED_MAINTENANCE_PARAMS

params = ct.MethodParameters(maintenance=fitted_maintenance_params)

# ========== Calculate Direct Operating Costs ==========
erj_145_xr_result = ct.calculate_costs(erj_145_xr, params, target_year=2025, verbose=True)

# print("\n========== Cost Breakdown (Per Flight) ERJ-145 XR ==========")
# print(f"OEW: {erj_145_xr.operational_empty_weight_kg:.2f} kg - {erj_145_xr.operational_empty_weight_kg * 2.20462:.2f} lbs")
# print(f"MTOW: {erj_145_xr.maximum_takeoff_weight_kg:.2f} kg - {erj_145_xr.maximum_takeoff_weight_kg * 2.20462:.2f} lbs")
# print(f"Fees & Charges:  ${erj_145_xr_result.per_flight.fees_and_charges:,.2f}")
# print(f"Crew:            ${erj_145_xr_result.per_flight.crew:,.2f}")
# print(f"Maintenance:     ${erj_145_xr_result.per_flight.maintenance:,.2f}")
# print(f"Fuel:            ${erj_145_xr_result.per_flight.fuel:,.2f}")
# print(f"Cash Operating Cost Per Flight: ${erj_145_xr_result.per_flight.fees_and_charges + erj_145_xr_result.per_flight.crew + erj_145_xr_result.per_flight.maintenance + erj_145_xr_result.per_flight.fuel:,.2f}")
# print(f"{'='*50}")