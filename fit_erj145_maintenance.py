"""
File: fit_erj145_maintenance.py
Fit Maintenance Model Parameters to Multiple Aircraft Target Costs

Author: Gabriel Bortoletto Molz
Date: February 11, 2026

Fits maintenance model parameters to achieve target costs for multiple aircraft:
- ERJ-145 XR: $1350/flight
- CRJ-700: $1450/flight
- CRJ-200: $1250/flight

Labor rate is NOT modified - only maintenance model coefficients.
"""

import numpy as np
from scipy.optimize import minimize
from dataclasses import replace
from cost_tool import FITTED_MAINTENANCE_PARAMS, AircraftParameters, MethodParameters, MaintenanceParameters, calculate_costs


def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


# ========== ERJ-145 XR Configuration (from e145_example.py) ==========
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

# ========== CRJ-700 Configuration (from crj700.py) ==========
crj_700 = AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:20:00"),
    flight_time_hours=hhmmss_to_hours("1:57:59"),
    flights_per_year=1200,
    
    # Weights
    maximum_takeoff_weight_kg=75000 / 2.205,
    operational_empty_weight_kg=43712 / 2.205,
    engine_weight_kg=1088,
    fuel_weight_kg=3514,
    payload_weight_kg=8431,
    
    # Mission
    range_nm=689,
    
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
)

# ========== CRJ-200 Configuration (from crj200.py) ==========
crj_200 = AircraftParameters(
    # Utilization
    block_time_hours=hhmmss_to_hours("2:20:00"),
    flight_time_hours=hhmmss_to_hours("1:53:57"),
    flights_per_year=1200,
    
    # Weights
    maximum_takeoff_weight_kg=53000 / 2.205,
    operational_empty_weight_kg=31904 / 2.205,
    engine_weight_kg=751.6,
    fuel_weight_kg=2650,
    payload_weight_kg=5487,
    
    # Mission
    range_nm=689,
    
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
)

# Target maintenance costs
TARGET_ERJ145 = 1350.0  # USD per flight
TARGET_CRJ700 = 1450.0  # USD per flight
TARGET_CRJ200 = 1250.0  # USD per flight

# Create aircraft list
aircraft_data = [
    {"name": "ERJ-145 XR", "aircraft": erj_145_xr, "target": TARGET_ERJ145},
    # {"name": "CRJ-700", "aircraft": crj_700, "target": TARGET_CRJ700},
    # {"name": "CRJ-200", "aircraft": crj_200, "target": TARGET_CRJ200},
]

# Base parameters (DO NOT modify labor_rate_usd_per_hour!)
base_params = MethodParameters()
base_params.maintenance = FITTED_MAINTENANCE_PARAMS

print("\n" + "="*70)
print("FITTING MAINTENANCE MODEL TO MULTIPLE AIRCRAFT")
print("="*70)
print(f"\nAircraft and Target Costs:")
for data in aircraft_data:
    print(f"  - {data['name']:<15} Target: ${data['target']:.2f}/flight")
print(f"\nLabor Rate: ${base_params.labor_rate_usd_per_hour:.2f}/hr (FIXED - not optimized)")
print("="*70 + "\n")


# ========== Calculate Baselines ==========
print("Baseline Maintenance Costs (AEA 1989a defaults):")
print("-" * 70)
for data in aircraft_data:
    baseline_result = calculate_costs(data['aircraft'], base_params, target_year=2025)
    baseline_cost = baseline_result.per_flight.maintenance
    diff = data['target'] - baseline_cost
    diff_pct = (data['target']/baseline_cost - 1) * 100
    
    data['baseline'] = baseline_cost
    
    print(f"{data['name']:<15} Baseline: ${baseline_cost:>7.2f}  Target: ${data['target']:>7.2f}  "
          f"Diff: ${diff:>8.2f} ({diff_pct:>+6.1f}%)")
print()


# ========== Define Parameters to Fit ==========
# Based on sensitivity analysis, fit top 10 parameters (excluding labor rate!)
# Expanded scope for better fitting with 3 aircraft
params_to_fit = [
    'airframe_labor_base_hours',                    # 12.03% sensitivity
    'airframe_labor_weight_numerator_kg',           # 7.35% sensitivity
    'airframe_labor_weight_denominator_offset_kg',  # 6.58% sensitivity
    'airframe_labor_time_coefficient',              # 4.07% sensitivity
    'engine_k1_base',                               # 3.69% sensitivity
    'engine_k2_opr_exponent',                       # 2.50% sensitivity
    'airframe_labor_time_base_factor',              # 2.29% sensitivity
    'engine_material_thrust_exponent',              # 1.79% sensitivity
    'airframe_labor_weight_coefficient',            # 1.69% sensitivity
    'engine_labor_base_coefficient',                # 1.52% sensitivity
]

print(f"Parameters to fit: {len(params_to_fit)}")
for i, param in enumerate(params_to_fit, 1):
    initial_val = getattr(base_params.maintenance, param)
    print(f"  {i:2d}. {param:45s}: {initial_val}")
print()


# Get initial values
initial_values = [
    getattr(base_params.maintenance, param)
    for param in params_to_fit
]


# Define bounds (reasonable ranges)
bounds = [
    (0.1, 20.0),      # airframe_labor_base_hours
    (1e4, 1e6),       # airframe_labor_weight_numerator_kg
    (1e3, 3e5),       # airframe_labor_weight_denominator_offset_kg
    (0.1, 2.0),       # airframe_labor_time_coefficient
    (0.5, 2.0),       # engine_k1_base
    (0.5, 2.0),       # engine_k2_opr_exponent
    (0.1, 2.0),       # airframe_labor_time_base_factor
    (0.4, 1.2),       # engine_material_thrust_exponent
    (1e-6, 1e-3),     # airframe_labor_weight_coefficient
    (0.05, 0.5),      # engine_labor_base_coefficient
]


def objective_function(param_values):
    """Calculate weighted sum of squared errors for all aircraft."""
    # Create updated maintenance parameters
    param_dict = dict(zip(params_to_fit, param_values))
    new_maint_params = replace(base_params.maintenance, **param_dict)
    new_params = replace(base_params, maintenance=new_maint_params)
    
    # Calculate total error across all aircraft
    total_error = 0.0
    for data in aircraft_data:
        result = calculate_costs(data['aircraft'], new_params, target_year=2025)
        predicted_cost = result.per_flight.maintenance
        
        # Squared error
        error = (predicted_cost - data['target']) ** 2
        total_error += error
    
    return total_error


# ========== Optimize ==========
print("Starting optimization...")
print("-" * 70)

result = minimize(
    objective_function,
    x0=initial_values,
    method='L-BFGS-B',
    bounds=bounds,
    options={
        'maxiter': 2000,     # Increased for more parameters
        'ftol': 1e-9,
        'gtol': 1e-7,
    }
)

print(f"Optimization complete: {result.success}")
print(f"Iterations: {result.nit}")
print(f"Final objective value: {result.fun:.4f}")
print(f"Final RMSE: ${np.sqrt(result.fun / len(aircraft_data)):.2f}")
print()


# ========== Results ==========
fitted_values = result.x
fitted_params_dict = dict(zip(params_to_fit, fitted_values))

# Create fitted parameters
fitted_maint_params = replace(base_params.maintenance, **fitted_params_dict)
fitted_params = replace(base_params, maintenance=fitted_maint_params)

# Calculate final costs for all aircraft
print("="*70)
print("FITTING RESULTS")
print("="*70)
print()

print("Final Maintenance Costs:")
print("-" * 70)
print(f"{'Aircraft':<15} {'Baseline':>10} {'Target':>10} {'Fitted':>10} {'Error':>10} {'Error %':>10}")
print("-" * 70)

total_rmse = 0.0
for data in aircraft_data:
    final_result = calculate_costs(data['aircraft'], fitted_params, target_year=2025)
    final_cost = final_result.per_flight.maintenance
    
    error = final_cost - data['target']
    error_pct = abs(error / data['target']) * 100
    
    total_rmse += error ** 2
    data['fitted'] = final_cost
    data['error'] = error
    
    print(f"{data['name']:<15} ${data['baseline']:>9.2f} ${data['target']:>9.2f} "
          f"${final_cost:>9.2f} ${error:>9.2f} {error_pct:>9.3f}%")

rmse = np.sqrt(total_rmse / len(aircraft_data))
print("-" * 70)
print(f"Overall RMSE: ${rmse:.2f}")
print()

print("Fitted Parameters:")
print("-" * 70)
print(f"{'Parameter':<45} {'Original':>15} {'Fitted':>15} {'Change':>10}")
print("-" * 70)

for param in params_to_fit:
    original = getattr(base_params.maintenance, param)
    fitted = getattr(fitted_params.maintenance, param)
    change_pct = (fitted / original - 1) * 100
    
    print(f"{param:<45} {original:>15.6e} {fitted:>15.6e} {change_pct:>9.1f}%")

print("-" * 70)
print()

# ========== Export Fitted Parameters ==========
print("="*70)
print("FITTED MAINTENANCE PARAMETERS (COPY THIS)")
print("="*70)
print()
print("fitted_maintenance_params = MaintenanceParameters(")
for field_name in sorted(dir(fitted_params.maintenance)):
    if not field_name.startswith('_'):
        value = getattr(fitted_params.maintenance, field_name)
        if isinstance(value, (int, float)):
            print(f"    {field_name}={value},")
print(")")
print()

print("To use these parameters:")
print("  from cost_tool import MethodParameters, MaintenanceParameters")
print("  params = MethodParameters(maintenance=fitted_maintenance_params)")
print("  result = calculate_costs(aircraft, params, target_year=2025)")
print()
print("="*70)

# ========== Verification ==========
print("\nVERIFICATION - Full Cost Breakdown with Fitted Parameters:")
print("="*70)

for data in aircraft_data:
    final_result = calculate_costs(data['aircraft'], fitted_params, target_year=2025)
    
    print(f"\n{data['name']}:")
    print("-" * 70)
    print(f"Depreciation:     ${final_result.per_flight.depreciation:,.2f}")
    print(f"Interest:         ${final_result.per_flight.interest:,.2f}")
    print(f"Insurance:        ${final_result.per_flight.insurance:,.2f}")
    print(f"Fuel:             ${final_result.per_flight.fuel:,.2f}")
    print(f"Maintenance:      ${final_result.per_flight.maintenance:,.2f}  ← FITTED")
    print(f"Crew:             ${final_result.per_flight.crew:,.2f}")
    print(f"Fees & Charges:   ${final_result.per_flight.fees_and_charges:,.2f}")
    print(f"{'='*70}")
    print(f"TOTAL:            ${final_result.per_flight.total:,.2f}")

print()
