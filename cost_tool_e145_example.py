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
from cost_tool import AircraftParameters, MethodParameters, MaintenanceParameters, calculate_costs


def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


# airplane = dt.standard_airplane('ERJ_145_XR')
# airplane = dt.analyze(airplane)

# ========== ERJ_145_XR Aircraft Configuration ==========
erj_145_xr = AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:05:00"),                    # Average block time per flight
    flight_time_hours=hhmmss_to_hours("1:34:00"),                   # Average flight time per flight
    flights_per_year=1, # THIS DOESNT MATTER
    
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
fitted_maintenance_params = MaintenanceParameters(
    airframe_labor_base_hours=8.122902723888275,
    airframe_labor_time_base_factor=0.16870063740188052,
    airframe_labor_time_coefficient=0.9003414675473087,
    airframe_labor_weight_coefficient=3.636374535885983e-05,
    airframe_labor_weight_denominator_offset_kg=74999.77124528734,
    airframe_labor_weight_numerator_kg=349999.9647928149,
    airframe_material_base_coefficient=4.2e-06,
    airframe_material_time_coefficient=2.2e-06,
    engine_k1_base=0.5542373120826335,
    engine_k1_bpr_coefficient=0.2,
    engine_k1_bpr_exponent=0.2,
    engine_k2_base=0.4,
    engine_k2_opr_coefficient=0.4,
    engine_k2_opr_divisor=20,
    engine_k2_opr_exponent=0.554237323109609,
    engine_k3_compressor_coefficient=0.032,
    engine_k4_single_shaft=0.5,
    engine_k4_triple_shaft=0.64,
    engine_k4_twin_shaft=0.57,
    engine_labor_base_coefficient=0.0662712266888201,
    engine_labor_flight_time_constant=1.3,
    engine_labor_thrust_coefficient=0.000102,
    engine_labor_thrust_exponent=0.4,
    engine_material_base_coefficient=2.0,
    engine_material_flight_time_constant=1.3,
    engine_material_thrust_exponent=0.42892656740853,
)

params = MethodParameters(maintenance=fitted_maintenance_params)

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