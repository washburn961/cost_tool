# Aircraft Direct Operating Cost Tool

A comprehensive Python library for calculating aircraft Direct Operating Costs (DOC) using the AEA 1989a/b methodology. This tool provides accurate cost estimations for aircraft operations, including depreciation, financing, maintenance, fuel, crew, and operational fees.

**Author:** Gabriel Bortoletto Molz  
**Date:** February 2026  
**Method:** AEA 1989a/b (Association of European Airlines)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [Detailed Usage](#detailed-usage)
- [Parameter Reference](#parameter-reference)
- [Integration with Other Tools](#integration-with-other-tools)
- [Methodology](#methodology)
- [Examples](#examples)
- [Cost Categories](#cost-categories)
- [Pricing Estimation](#pricing-estimation)

---

## Overview

The **Aircraft Direct Operating Cost Tool** calculates the complete economic operating costs for commercial aircraft. It is based on industry-standard AEA (Association of European Airlines) methods from 1989, which remain widely used for preliminary aircraft design and economic analysis.

### What are Direct Operating Costs?

Direct Operating Costs (DOC) are expenses directly attributable to flying an aircraft:
- **Fixed Costs**: Depreciation, interest, insurance
- **Variable Costs**: Fuel, maintenance, crew salaries, airport/navigation fees

### Key Capabilities

- Calculate costs on **annual**, **per-flight**, and **per-hour** bases
- Automatic **price estimation** from aircraft weight and engine thrust
- **Inflation adjustment** to any target year
- Comprehensive **maintenance cost modeling** (airframe + engine)
- Detailed **pricing breakdown** (delivery, engines, airframe, spares)
- **Modular design** for easy integration into aircraft design tools

---

## Features

✅ **Complete DOC Calculation**: All cost categories per AEA 1989a/b  
✅ **Automated Price Estimation**: No need to know exact aircraft prices  
✅ **Inflation Handling**: Adjusts historical correlations to target year  
✅ **Flexible Configuration**: Override any parameter or use defaults  
✅ **Multiple Output Formats**: Annual, per-flight, per-hour breakdowns  
✅ **Type-Safe**: Uses Python dataclasses with type hints  
✅ **Well-Documented**: Comprehensive docstrings and formula references  
✅ **Integration-Ready**: Easy to embed in optimization or sizing tools  
✅ **Calibrated Parameters**: Fitted maintenance parameters for improved accuracy on regional jets

---

## Model Calibration & Fitted Parameters

### Overview

The tool includes **empirically-fitted maintenance parameters** (`FITTED_MAINTENANCE_PARAMS`) calibrated to actual operating data from three regional jets:

- **ERJ-145 XR** (Embraer 145, 50-seat)
- **CRJ-700** (Bombardier CRJ-700, 70-seat)  
- **CRJ-200** (Bombardier CRJ-200, 50-seat)

### Calibration Process

1. **Sensitivity Analysis**: Identified the 10 most influential maintenance parameters out of 26 total parameters
2. **Multi-Aircraft Optimization**: Used scipy's L-BFGS-B algorithm to minimize RMSE across all three aircraft
3. **Constrained Fitting**: Maintained physical bounds on all parameters to ensure realistic values
4. **Validation**: Achieved **RMSE of $21.75** across all aircraft

### Accuracy Improvement

| Aircraft | AEA 1989a Default | Fitted Parameters | Improvement |
|----------|-------------------|-------------------|-------------|
| **ERJ-145 XR** | $2,076 (54% error) | $1,330 (1.5% error) | **52.5 pp** |
| **CRJ-700** | $2,646 (83% error) | $1,442 (0.6% error) | **82.4 pp** |
| **CRJ-200** | $2,113 (69% error) | $1,281 (2.4% error) | **66.6 pp** |

### When to Use Fitted Parameters

**Use `FITTED_MAINTENANCE_PARAMS` when:**
- Analyzing regional jets (40-100 seats, 12,000-20,000 kg OEW)
- Twin turbofan engines with BPR 4-6, OPR 18-25
- Accuracy is critical for economic analysis
- You have validated the results against known data

**Use default parameters when:**
- Analyzing wide-body or narrow-body jets (significantly larger than regional jets)
- Using turboprops (different maintenance characteristics)
- First-pass preliminary design (AEA defaults are still reasonable)
- Comparing relative differences between configurations

### How to Use Fitted Parameters

```python
from cost_tool import (AircraftParameters, MethodParameters, 
                       calculate_costs, FITTED_MAINTENANCE_PARAMS)

# Option 1: Use default AEA 1989a parameters
params_default = MethodParameters()
result_default = calculate_costs(aircraft, params_default)

# Option 2: Use fitted parameters (recommended for regional jets)
params_fitted = MethodParameters(maintenance=FITTED_MAINTENANCE_PARAMS)
result_fitted = calculate_costs(aircraft, params_fitted)

print(f"Default maintenance: ${result_default.per_flight.maintenance:,.2f}")
print(f"Fitted maintenance:  ${result_fitted.per_flight.maintenance:,.2f}")
```

### Fitted Parameters Details

The calibration process optimized 10 key parameters while keeping 16 parameters at AEA defaults:

**Top optimized parameters:**
1. `airframe_labor_base_hours`: 6.7 → 7.68 (+14.6%)
2. `airframe_labor_time_coefficient`: 0.68 → 0.86 (+26.3%)
3. `engine_k1_base`: 1.27 → 0.5 (-60.6%)
4. `engine_k2_opr_exponent`: 1.3 → 0.5 (-61.5%)
5. `airframe_labor_time_base_factor`: 0.8 → 0.1 (-87.5%)

Full parameter set is available in `cost_tool.py` as `FITTED_MAINTENANCE_PARAMS`.

### Sensitivity Analysis

A complete sensitivity analysis tool (`maintenance_sensitivity_analysis.py`) is included to identify which parameters most influence maintenance costs. Key findings:

| Parameter | Sensitivity (%) | Category |
|-----------|-----------------|----------|
| `airframe_labor_base_hours` | 12.03% | Airframe Labor |
| `airframe_labor_time_coefficient` | 6.45% | Airframe Labor |
| `engine_k1_base` | 5.93% | Engine k-factors |
| `engine_labor_base_coefficient` | 5.52% | Engine Labor |

The top 10 parameters account for ~60% of total maintenance cost variance.

---

## Installation

### Requirements

- Python 3.10 or higher (uses modern type hints: `float | None`)
- No external dependencies for core functionality

### Setup

1. **Clone or download** the repository containing `cost_tool.py`

2. **Place** `cost_tool.py` in your project directory or Python path

3. **Import** the module:
```python
from cost_tool import AircraftParameters, MethodParameters, calculate_costs
```

That's it! The tool is a single, self-contained Python file with no dependencies.

---

## Quick Start

Here's a minimal example calculating DOC for an ERJ-145 XR regional jet:

```python
from cost_tool import (AircraftParameters, MethodParameters, 
                       calculate_costs, FITTED_MAINTENANCE_PARAMS)

# Define aircraft parameters
aircraft = AircraftParameters(
    # Utilization
    block_time_hours=2.33,                      # 2:20:00 in decimal hours
    flight_time_hours=2.087,                    # 2:05:13 in decimal hours
    flights_per_year=1500,                      # Annual utilization
    
    # Weights (kg)
    maximum_takeoff_weight_kg=21996,            # MTOW
    operational_empty_weight_kg=12495,          # OEW
    engine_weight_kg=751.6,                     # per engine
    fuel_weight_kg=2664,                        # per flight
    payload_weight_kg=5403,                     # typical payload
    
    # Mission
    range_nm=689,                               # nautical miles
    
    # Engine specifications
    engine_count=2,
    bypass_ratio=4.7,
    overall_pressure_ratio=20,
    compressor_stages=9,
    engine_shafts=2,
    takeoff_thrust_per_engine_N=39670,          # Newtons
    
    # Crew
    cockpit_crew_count=2,
    cabin_crew_count=1,
)

# Option 1: Use default AEA 1989a parameters
params = MethodParameters()
result = calculate_costs(aircraft, params, target_year=2025)

# Option 2: Use fitted parameters (recommended for regional jets)
params_fitted = MethodParameters(maintenance=FITTED_MAINTENANCE_PARAMS)
result_fitted = calculate_costs(aircraft, params_fitted, target_year=2025)

# Display results (using fitted parameters)
print(f"Total DOC (annual): ${result_fitted.annual.total:,.0f}")
print(f"Total DOC (per flight): ${result_fitted.per_flight.total:,.2f}")
print(f"Total DOC (per hour): ${result_fitted.per_hour.total:,.2f}")
print(f"Maintenance (per flight): ${result_fitted.per_flight.maintenance:,.2f}")
```

### Output Structure

The `calculate_costs()` function returns a `DOCResult` object containing:

```python
result.prices          # PricingBreakdown - aircraft/engine/spares prices
result.annual          # CostBreakdown - annual costs [USD/year]
result.per_flight      # CostBreakdown - per-flight costs [USD/flight]
result.per_hour        # CostBreakdown - per-hour costs [USD/hour]
```

Each `CostBreakdown` contains:
- `depreciation`
- `interest`
- `insurance`
- `fuel`
- `maintenance`
- `crew`
- `fees_and_charges`
- `total`

---

## Core Components

### 1. `AircraftParameters`

Dataclass containing all aircraft design, operational, and pricing parameters.

**Key categories:**
- **Utilization**: Block time, flight time, annual flights
- **Weights**: MTOW, OEW, engine weight, fuel, payload
- **Mission**: Range
- **Engine**: Count, bypass ratio, pressure ratio, stages, thrust
- **Crew**: Cockpit and cabin crew counts
- **Pricing**: Delivery price, engine price (optional - will be estimated)

### 2. `MethodParameters`

Dataclass containing cost method factors and rates.

**Key parameters:**
- **Spares factors**: Airframe (0.1), Engine (0.3)
- **Depreciation**: 16-year period, 10% residual value
- **Interest**: 8% rate, 16-year repayment, 10% balloon
- **Insurance**: 0.5% of delivery price
- **Fuel**: Price per kg (default: $0.622/kg)
- **Labor**: Maintenance rate (default: $65/hr + inflation)
- **Crew**: Cockpit and cabin rates
- **Fees**: Landing, navigation, ground handling factors

### 3. `calculate_costs()`

Main calculation function that orchestrates all DOC computations.

**Signature:**
```python
def calculate_costs(
    aircraft: AircraftParameters,
    params: MethodParameters,
    target_year: int = 2026,
) -> DOCResult
```

**Returns:** `DOCResult` with complete pricing and cost breakdowns

---

## Detailed Usage

### Example: Step-by-Step Analysis

```python
from cost_tool import AircraftParameters, MethodParameters, calculate_costs

# ========== STEP 1: Define Aircraft ==========
my_aircraft = AircraftParameters(
    # Utilization (required for annual costs)
    block_time_hours=2.5,           # taxi + flight + taxi
    flight_time_hours=2.2,          # airborne time only
    flights_per_year=2000,          # annual utilization
    
    # Weights (all in kg)
    maximum_takeoff_weight_kg=25000,
    operational_empty_weight_kg=14000,
    engine_weight_kg=800,
    fuel_weight_kg=3000,
    payload_weight_kg=8000,
    
    # Mission
    range_nm=750,
    
    # Engine parameters (critical for maintenance costs)
    engine_count=2,
    bypass_ratio=5.0,               # modern turbofan
    overall_pressure_ratio=25,      # compression ratio
    compressor_stages=10,           # including fan
    engine_shafts=2,                # 1, 2, or 3
    takeoff_thrust_per_engine_N=50000,
    
    # Crew
    cockpit_crew_count=2,           # pilot + copilot
    cabin_crew_count=2,             # 1 per 50 passengers rule
    
    # Optional: provide known prices (otherwise estimated)
    aircraft_delivery_price_usd=30_000_000,
    engine_price_usd=2_500_000,
)

# ========== STEP 2: Configure Method Parameters ==========
my_params = MethodParameters(
    # Override defaults as needed
    fuel_price_usd=0.70,            # current fuel price per kg
    inflation_rate=0.02,            # 2% annual inflation
    interest_rate=0.06,             # 6% financing rate
    
    # Crew costs (per hour)
    cockpit_crew_rate_usd_per_hour=150,  # per pilot
    cabin_crew_rate_usd_per_hour=50,     # per FA
    
    # Keep other defaults...
)

# ========== STEP 3: Calculate Costs ==========
result = calculate_costs(my_aircraft, my_params, target_year=2026)

# ========== STEP 4: Access Results ==========

# Pricing breakdown
print("=== PRICING ===")
print(f"Engine (each):   ${result.prices.engine_price_usd:,.0f}")
print(f"Delivery price:  ${result.prices.delivery_price_usd:,.0f}")
print(f"Airframe:        ${result.prices.airframe_price_usd:,.0f}")
print(f"Spares:          ${result.prices.spares_price_usd:,.0f}")
print(f"Total purchase:  ${result.prices.purchase_price_usd:,.0f}")

# Annual costs
print("\n=== ANNUAL COSTS ===")
print(f"Depreciation:    ${result.annual.depreciation:,.0f}")
print(f"Interest:        ${result.annual.interest:,.0f}")
print(f"Insurance:       ${result.annual.insurance:,.0f}")
print(f"Fuel:            ${result.annual.fuel:,.0f}")
print(f"Maintenance:     ${result.annual.maintenance:,.0f}")
print(f"Crew:            ${result.annual.crew:,.0f}")
print(f"Fees & Charges:  ${result.annual.fees_and_charges:,.0f}")
print(f"TOTAL:           ${result.annual.total:,.0f}")

# Per-flight costs
print("\n=== PER-FLIGHT COSTS ===")
print(f"Total:           ${result.per_flight.total:,.2f}")

# Per-hour costs
print("\n=== PER-HOUR COSTS ===")
print(f"Total:           ${result.per_hour.total:,.2f}")

# Cash operating cost (variable costs only)
cash_cost = (result.per_flight.fuel + 
             result.per_flight.maintenance + 
             result.per_flight.crew + 
             result.per_flight.fees_and_charges)
print(f"\nCash Operating Cost (per flight): ${cash_cost:,.2f}")
```

---

## Parameter Reference

### AircraftParameters

#### Utilization
| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| `block_time_hours` | `float` | hours | Block time per flight (brakes off → brakes on) |
| `flight_time_hours` | `float` | hours | Airborne time per flight |
| `flights_per_year` | `int` | flights/year | Annual utilization |

#### Weights
| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| `maximum_takeoff_weight_kg` | `float` | kg | Maximum takeoff weight (MTOW) |
| `operational_empty_weight_kg` | `float` | kg | Operational empty weight (OEW) |
| `engine_weight_kg` | `float` | kg | Dry weight per engine |
| `fuel_weight_kg` | `float` | kg | Fuel consumed per flight |
| `payload_weight_kg` | `float` | kg | Payload weight |

#### Mission
| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| `range_nm` | `float` | nautical miles | Flight range |

#### Engine
| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| `engine_count` | `int` | - | Number of engines (typically 2) |
| `bypass_ratio` | `float` | - | Engine bypass ratio (BPR) |
| `overall_pressure_ratio` | `float` | - | Overall air pressure ratio (OAPR) |
| `compressor_stages` | `int` | - | Compressor stages (including fan) |
| `engine_shafts` | `int` | - | Number of shafts (1, 2, or 3) |
| `takeoff_thrust_per_engine_N` | `float` | Newtons | Takeoff thrust per engine |

#### Crew
| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| `cockpit_crew_count` | `int` | - | Cockpit crew (default: 2) |
| `cabin_crew_count` | `int` | - | Cabin crew (default: 1) |

#### Pricing (Optional)
| Parameter | Type | Units | Description |
|-----------|------|-------|-------------|
| `aircraft_delivery_price_usd` | `float \| None` | USD | Aircraft price (will be estimated if `None`) |
| `engine_price_usd` | `float \| None` | USD | Price per engine (will be estimated if `None`) |

---

### MethodParameters

All parameters have sensible defaults based on AEA 1989a/b methodology.

#### Key Overridable Parameters

| Parameter | Default | Units | Description |
|-----------|---------|-------|-------------|
| `fuel_price_usd` | `0.622` | USD/kg | Fuel price ($0.888 × 0.7 factor) |
| `inflation_rate` | `0.013` | - | Annual inflation rate (1.3%) |
| `interest_rate` | `0.08` | - | Loan interest rate (8%) |
| `labor_rate_usd_per_hour` | `65` | USD/h | 1989 base labor rate (auto-inflated) |
| `cockpit_crew_rate_usd_per_hour` | `147.5` | USD/h | Per cockpit crew member |
| `cabin_crew_rate_usd_per_hour` | `0` | USD/h | Per cabin crew member |
| `landing_fee_factor` | `0.00052` | USD/kg | Landing fee rate |
| `navigation_fee_factor` | `0.000276` | USD/(nm·√kg) | Navigation fee rate |
| `ground_handling_factor` | `0.00667` | USD/kg | Ground handling rate |

---

## Integration with Other Tools

### Example: Integration with Aircraft Design Tool

The cost tool integrates seamlessly with aircraft sizing and performance tools:

```python
import designTool_learis as dt  # Your aircraft design tool
from cost_tool import AircraftParameters, MethodParameters, calculate_costs

# ========== Use Your Design Tool ==========
airplane = dt.standard_airplane('ERJ_145_XR')
airplane = dt.analyze(airplane)  # Size, performance, weights

# ========== Map to Cost Tool Parameters ==========
aircraft_params = AircraftParameters(
    # Pull data from your design tool
    operational_empty_weight_kg=airplane.weights.OEW,
    maximum_takeoff_weight_kg=airplane.weights.MTOW,
    engine_weight_kg=airplane.propulsion.engine_weight,
    fuel_weight_kg=airplane.mission.fuel_weight,
    payload_weight_kg=airplane.mission.payload,
    
    # Mission profile
    range_nm=airplane.mission.range_nm,
    block_time_hours=airplane.mission.block_time,
    flight_time_hours=airplane.mission.flight_time,
    flights_per_year=1500,  # from market analysis
    
    # Engine from your propulsion module
    engine_count=airplane.propulsion.n_engines,
    bypass_ratio=airplane.propulsion.BPR,
    overall_pressure_ratio=airplane.propulsion.OPR,
    compressor_stages=airplane.propulsion.stages,
    engine_shafts=2,
    takeoff_thrust_per_engine_N=airplane.propulsion.thrust_TO,
    
    # Crew from cabin layout
    cockpit_crew_count=2,
    cabin_crew_count=airplane.cabin.n_FA,
)

# Calculate costs
result = calculate_costs(aircraft_params, MethodParameters())

# Use results in your optimization
cost_per_seat_mile = result.per_flight.total / (airplane.cabin.n_pax * airplane.mission.range_nm)
```

### Integration Patterns

#### 1. Parametric Studies
```python
import numpy as np
import matplotlib.pyplot as plt

# Vary aircraft size
OEWs = np.linspace(10000, 30000, 20)  # kg
costs = []

for oew in OEWs:
    aircraft = AircraftParameters(
        operational_empty_weight_kg=oew,
        # ... scale other parameters proportionally
    )
    result = calculate_costs(aircraft, MethodParameters())
    costs.append(result.per_flight.total)

plt.plot(OEWs, costs)
plt.xlabel('OEW (kg)')
plt.ylabel('DOC per Flight (USD)')
plt.show()
```

#### 2. Multi-Disciplinary Optimization (MDO)
```python
def objective_function(design_vector):
    """Minimize cost per available seat mile."""
    # 1. Unpack design variables
    wing_area, thrust, ... = design_vector
    
    # 2. Run aerodynamics, weights, performance
    aircraft = your_design_tool.analyze(wing_area, thrust, ...)
    
    # 3. Calculate DOC
    cost_result = calculate_costs(
        map_to_aircraft_params(aircraft),
        MethodParameters()
    )
    
    # 4. Return objective
    CASM = cost_result.per_flight.total / (n_seats * range_nm)
    return CASM
```

#### 3. Uncertainty Analysis (Monte Carlo)
```python
import random

results = []
for _ in range(1000):
    # Sample uncertain parameters
    aircraft = AircraftParameters(
        operational_empty_weight_kg=random.gauss(15000, 500),
        fuel_weight_kg=random.gauss(3000, 200),
        # ...
    )
    
    params = MethodParameters(
        fuel_price_usd=random.uniform(0.5, 0.9),
        interest_rate=random.uniform(0.05, 0.10),
    )
    
    result = calculate_costs(aircraft, params)
    results.append(result.per_flight.total)

# Analyze distribution
mean_cost = np.mean(results)
std_cost = np.std(results)
print(f"DOC: ${mean_cost:.2f} ± ${std_cost:.2f}")
```

---

## Methodology

### AEA 1989a/b Method

This tool implements the **Association of European Airlines (AEA)** Direct Operating Cost methodology from 1989, which consists of:

- **AEA 1989a**: Original method with detailed maintenance modeling
- **AEA 1989b**: Refined version with updated fee structures

The method is widely used in:
- Preliminary aircraft design
- Fleet planning and evaluation
- Market analysis and feasibility studies
- Academic research

### Cost Categories

#### 1. **Depreciation**
Straight-line depreciation over useful life (16 years), with residual value (10%)

#### 2. **Interest**
Average interest on declining loan balance, with optional balloon payment

#### 3. **Insurance**
Hull insurance as percentage of delivery price (0.5%)

#### 4. **Fuel**
Direct fuel consumption cost per flight

#### 5. **Maintenance**
- **Airframe maintenance**: Labor + materials based on weight and utilization
- **Engine maintenance**: Labor + materials based on engine complexity and thrust

Complex formulas account for:
- Aircraft weight and structure
- Flight time per cycle
- Engine bypass ratio, pressure ratio, stages, shafts
- Thrust rating

#### 6. **Crew**
Salaries and benefits for cockpit crew and cabin crew

#### 7. **Fees and Charges**
- **Landing fees**: Based on MTOW
- **Navigation/ATC fees**: Based on distance × √(MTOW)
- **Ground handling**: Based on payload weight

### Inflation Handling

The tool automatically adjusts historical price correlations:

- **Engine price formula**: Based on 1999 data
- **Aircraft price formula**: Based on 2010 data  
- **Labor rates**: Based on 1989 data
- **Fee structures**: Based on 1989 data

All are adjusted to the `target_year` using the specified inflation rate (default: 1.3% annually).

---

## Examples

### Example 1: Cash Operating Cost Only

If you only care about variable costs (fuel, maintenance, crew, fees):

```python
result = calculate_costs(aircraft, params)

cash_cost_per_flight = (
    result.per_flight.fuel +
    result.per_flight.maintenance +
    result.per_flight.crew +
    result.per_flight.fees_and_charges
)

print(f"Cash operating cost: ${cash_cost_per_flight:,.2f} per flight")
```

### Example 2: Custom Fuel Price Analysis

```python
fuel_prices = [0.50, 0.60, 0.70, 0.80, 0.90]  # USD/kg
total_costs = []

for fuel_price in fuel_prices:
    params = MethodParameters(fuel_price_usd=fuel_price)
    result = calculate_costs(aircraft, params)
    total_costs.append(result.per_flight.total)

# Plot sensitivity
import matplotlib.pyplot as plt
plt.plot(fuel_prices, total_costs, marker='o')
plt.xlabel('Fuel Price (USD/kg)')
plt.ylabel('Total DOC per Flight (USD)')
plt.grid(True)
plt.show()
```

### Example 3: Time Conversion Helper

```python
def hhmmss_to_hours(time_str):
    """Convert HH:MM:SS string to decimal hours."""
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600

aircraft = AircraftParameters(
    block_time_hours=hhmmss_to_hours("2:30:00"),
    flight_time_hours=hhmmss_to_hours("2:15:30"),
    # ...
)
```

### Example 4: Compare Multiple Aircraft

```python
aircraft_list = [
    ('ERJ-145', erj_params),
    ('CRJ-200', crj_params),
    ('E175', e175_params),
]

print(f"{'Aircraft':<12} {'DOC/flight':>12} {'DOC/hour':>12}")
print("=" * 40)

for name, params in aircraft_list:
    result = calculate_costs(params, MethodParameters())
    print(f"{name:<12} ${result.per_flight.total:>11,.2f} ${result.per_hour.total:>11,.2f}")
```

---

## Cost Categories

### Fixed Costs (Independent of Utilization)

These costs are incurred regardless of flight hours:

| Category | Annual Formula | Notes |
|----------|----------------|-------|
| **Depreciation** | (Purchase - Residual) / Years | Straight-line |
| **Interest** | Purchase × Average Rate | Declining balance |
| **Insurance** | Delivery × 0.5% | Hull insurance |

### Variable Costs (Dependent on Utilization)

These costs scale with flight hours and cycles:

| Category | Driver | Key Factors |
|----------|--------|-------------|
| **Fuel** | Weight × Distance | Fuel consumption, price |
| **Maintenance** | Hours × Complexity | Weight, thrust, BPR, OPR |
| **Crew** | Hours × Personnel | Cockpit + cabin crew |
| **Fees** | Cycles × Weight | MTOW, range, payload |

---

## Pricing Estimation

### Automatic Price Estimation

If you don't provide `aircraft_delivery_price_usd` or `engine_price_usd`, they are estimated:

#### Engine Price Estimation
```
P_engine = 293 × (T_TO [N])^0.81
```
Based on 1999 data, inflated to target year.

**Example**: For 50,000 N thrust → ~$2.4M (1999) → ~$3.8M (2026)

#### Aircraft Delivery Price Estimation  

From operational empty weight (OEW):

**For OEW ≥ 10,000 kg:**
```
Delivery = 860 × OEW [kg]
```

**For OEW < 10,000 kg:**
```
Delivery = -0.002695 × OEW² + 1967 × OEW - 2,158,000
```

Based on 2010 data, inflated to target year.

### Manual Price Override

For accuracy, provide known prices:

```python
aircraft = AircraftParameters(
    # ...other params...
    aircraft_delivery_price_usd=32_000_000,  # From manufacturer
    engine_price_usd=2_800_000,              # From engine OEM
)
```

This bypasses estimation and uses your values directly (assumed to be in current-year dollars).

---

## Tips and Best Practices

### ✅ Do's

- **Provide known prices** when available for better accuracy
- **Use consistent units**: kg for weights, nautical miles for range, Newtons for thrust
- **Validate engine parameters**: Ensure BPR, OPR, stages match the actual engine
- **Check crew counts**: Use 1 FA per 50 passengers as a rule of thumb
- **Update fuel prices**: Adjust `fuel_price_usd` to current market rates
- **Consider inflation**: Use appropriate `target_year` for your analysis period

### ❌ Don'ts

- **Don't mix units**: DOC methods are sensitive to unit errors
- **Don't use unrealistic utilization**: 2000-3000 flights/year is typical for commercial
- **Don't ignore crew costs**: They can be 10-15% of total DOC
- **Don't forget spares**: Initial spares investment is included in purchase price
- **Don't assume constant fees**: Landing/navigation fees vary by region

---

## Troubleshooting

### Common Issues

**Issue: Unrealistic costs**
- Check that all weights are in **kg**, not lbs
- Verify thrust is in **Newtons**, not pounds or kN
- Ensure range is in **nautical miles**, not km or statute miles

**Issue: High maintenance costs**
- Verify engine parameters (BPR, OPR, stages) are correct
- Check that `flight_time_hours` is reasonable (1-5 hours typical)
- Ensure `engine_shafts` is 1, 2, or 3 (not left as None)

**Issue: Price estimation seems off**
- Consider providing `aircraft_delivery_price_usd` manually
- Check that OEW is realistic for the aircraft class
- Verify `target_year` matches your economic assumptions

---

## References

1. **AEA (1989a)**: "Short-Medium Range Aircraft AEA Requirements", Association of European Airlines
2. **AEA (1989b)**: "Long Range Aircraft AEA Requireuments", Association of European Airlines  
3. **Roskam, J.** (1990): "Airplane Design, Part VIII: Airplane Cost Estimation"
4. **Raymer, D.P.** (2018): "Aircraft Design: A Conceptual Approach", 6th Edition

---

## License

This tool is provided for educational and research purposes. The AEA methodology is publicly available in aircraft design literature.

---

## Contributing

For questions, bug reports, or suggestions on integration with other aircraft design tools, please contact the author.

**Author:** Gabriel Bortoletto Molz  
**Date:** February 2026

---

## Complete Working Example

```python
"""Complete example: Regional jet DOC analysis"""
from cost_tool import AircraftParameters, MethodParameters, calculate_costs

def hhmmss_to_hours(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600

# ERJ-145 XR regional jet
aircraft = AircraftParameters(
    block_time_hours=hhmmss_to_hours("2:20:00"),
    flight_time_hours=hhmmss_to_hours("2:05:13"),
    flights_per_year=1500,
    
    maximum_takeoff_weight_kg=21996,
    operational_empty_weight_kg=12495,
    engine_weight_kg=751.6,
    fuel_weight_kg=2664,
    payload_weight_kg=5403,
    
    range_nm=689,
    
    engine_count=2,
    bypass_ratio=4.7,
    overall_pressure_ratio=20,
    compressor_stages=9,
    engine_shafts=2,
    takeoff_thrust_per_engine_N=39670,
    
    cockpit_crew_count=2,
    cabin_crew_count=1,
)

# Calculate with defaults
result = calculate_costs(aircraft, MethodParameters(), target_year=2025)

# Print summary
print("\n" + "="*60)
print(" ERJ-145 XR DIRECT OPERATING COST ANALYSIS (2025)")
print("="*60)

print(f"\nAIRCRAFT SPECIFICATION")
print(f"  OEW:  {aircraft.operational_empty_weight_kg:>8,.0f} kg ({aircraft.operational_empty_weight_kg * 2.20462:>8,.0f} lbs)")
print(f"  MTOW: {aircraft.maximum_takeoff_weight_kg:>8,.0f} kg ({aircraft.maximum_takeoff_weight_kg * 2.20462:>8,.0f} lbs)")
print(f"  Range: {aircraft.range_nm:>7,.0f} nm")
print(f"  Utilization: {aircraft.flights_per_year:>4,} flights/year")

print(f"\nPRICING BREAKDOWN")
print(f"  Engine (each):  ${result.prices.engine_price_usd:>12,.0f}")
print(f"  Delivery price: ${result.prices.delivery_price_usd:>12,.0f}")
print(f"  Spares:         ${result.prices.spares_price_usd:>12,.0f}")
print(f"  Total purchase: ${result.prices.purchase_price_usd:>12,.0f}")

print(f"\nANNUAL COSTS (USD/year)")
print(f"  Depreciation:   ${result.annual.depreciation:>12,.0f}")
print(f"  Interest:       ${result.annual.interest:>12,.0f}")
print(f"  Insurance:      ${result.annual.insurance:>12,.0f}")
print(f"  Fuel:           ${result.annual.fuel:>12,.0f}")
print(f"  Maintenance:    ${result.annual.maintenance:>12,.0f}")
print(f"  Crew:           ${result.annual.crew:>12,.0f}")
print(f"  Fees & Charges: ${result.annual.fees_and_charges:>12,.0f}")
print(f"  {'─'*30}")
print(f"  TOTAL:          ${result.annual.total:>12,.0f}")

print(f"\nPER-FLIGHT COSTS (USD/flight)")
print(f"  Total DOC:      ${result.per_flight.total:>12,.2f}")

cash_cost = (result.per_flight.fuel + result.per_flight.maintenance + 
             result.per_flight.crew + result.per_flight.fees_and_charges)
print(f"  Cash Op Cost:   ${cash_cost:>12,.2f}")

print(f"\nPER-HOUR COSTS (USD/flight hour)")
print(f"  Total DOC:      ${result.per_hour.total:>12,.2f}")

print("\n" + "="*60 + "\n")
```

---

**End of Documentation**
