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
from cost_tool import AircraftParameters, MethodParameters, MaintenanceParameters, calculate_costs


def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


airplane = dt.standard_airplane('CRJ200')
airplane = dt.analyze(airplane)

# ========== CRJ_200 Aircraft Configuration ==========
crj_200 = AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:20:00"),                    # Average block time per flight
    flight_time_hours=hhmmss_to_hours("1:53:57"),                   # Average flight time per flight
    flights_per_year=1, # THIS DOESNT MATTER
    
    # Weights
    maximum_takeoff_weight_kg=53000 / 2.205,        # MTOW
    operational_empty_weight_kg=31904 / 2.205,      # OEW
    engine_weight_kg=751.6,
    fuel_weight_kg=2650,                    # Fuel per flight (average)
    payload_weight_kg=5487,                # Typical payload
    
    # Mission
    range_nm=689,                          # Average stage length
    
    # Engine specifications
    engine_count=2,
    bypass_ratio=6.2,
    overall_pressure_ratio=14,
    compressor_stages=14,
    engine_shafts=2,
    takeoff_thrust_per_engine_N=41000,
    
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
    airframe_labor_base_hours=7.677337282966461,
    airframe_labor_time_base_factor=0.1,
    airframe_labor_time_coefficient=0.8590882764848947,
    airframe_labor_weight_coefficient=1e-06,
    airframe_labor_weight_denominator_offset_kg=74999.77106224232,
    airframe_labor_weight_numerator_kg=349999.964837715,
    airframe_material_base_coefficient=4.2e-06,
    airframe_material_time_coefficient=2.2e-06,
    engine_k1_base=0.5,
    engine_k1_bpr_coefficient=0.2,
    engine_k1_bpr_exponent=0.2,
    engine_k2_base=0.4,
    engine_k2_opr_coefficient=0.4,
    engine_k2_opr_divisor=20,
    engine_k2_opr_exponent=0.5000000033638023,
    engine_k3_compressor_coefficient=0.032,
    engine_k4_single_shaft=0.5,
    engine_k4_triple_shaft=0.64,
    engine_k4_twin_shaft=0.57,
    engine_labor_base_coefficient=0.05,
    engine_labor_flight_time_constant=1.3,
    engine_labor_thrust_coefficient=0.000102,
    engine_labor_thrust_exponent=0.4,
    engine_material_base_coefficient=2.0,
    engine_material_flight_time_constant=1.3,
    engine_material_thrust_exponent=0.40000000060154356,
)

params = MethodParameters(maintenance=fitted_maintenance_params)

# ========== Calculate Direct Operating Costs ==========
crj_200_result = calculate_costs(crj_200, params, target_year=2025)

print("\n========== Cost Breakdown (Per Flight) CRJ-200 ==========")
print(f"OEW: {crj_200.operational_empty_weight_kg:.2f} kg - {crj_200.operational_empty_weight_kg * 2.20462:.2f} lbs")
print(f"MTOW: {crj_200.maximum_takeoff_weight_kg:.2f} kg - {crj_200.maximum_takeoff_weight_kg * 2.20462:.2f} lbs")
print(f"Fees & Charges:  ${crj_200_result.per_flight.fees_and_charges:,.2f}")
print(f"Crew:            ${crj_200_result.per_flight.crew:,.2f}")
print(f"Maintenance:     ${crj_200_result.per_flight.maintenance:,.2f}")
print(f"Fuel:            ${crj_200_result.per_flight.fuel:,.2f}")
print(f"Cash Operating Cost Per Flight: ${crj_200_result.per_flight.fees_and_charges + crj_200_result.per_flight.crew + crj_200_result.per_flight.maintenance + crj_200_result.per_flight.fuel:,.2f}")
print(f"{'='*50}")