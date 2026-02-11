# Maintenance Cost Model - Sensitivity Analysis Summary

**Date:** February 11, 2026  
**Aircraft:** Embraer ERJ-145 XR  
**Baseline Maintenance Cost:** $1,278.83 per flight

---

## Executive Summary

Sensitivity analysis reveals that **airframe maintenance parameters dominate** the cost model, with the top parameter having **12% sensitivity** (10% parameter change → 12% cost change).

---

## Top 15 Most Sensitive Parameters

| Rank | Parameter | Sensitivity | Category | Priority |
|------|-----------|-------------|----------|----------|
| 1 | **Airframe Labor Base Hours** | **12.03%** | Airframe | 🔴 CRITICAL |
| 2 | **Airframe Labor Weight Numerator** | **7.35%** | Airframe | 🔴 CRITICAL |
| 3 | **Airframe Labor Weight Denominator Offset** | **6.58%** | Airframe | 🔴 CRITICAL |
| 4 | Airframe Labor Time Coefficient | 4.07% | Airframe | 🟠 HIGH |
| 5 | Engine K1 Base | 3.69% | Engine | 🟠 HIGH |
| 6 | Engine K2 OPR Exponent | 2.50% | Engine | 🟡 MEDIUM |
| 7 | Airframe Labor Time Base Factor | 2.29% | Airframe | 🟡 MEDIUM |
| 8 | Engine Material Thrust Exponent | 1.79% | Engine | 🟡 MEDIUM |
| 9 | Airframe Labor Weight Coefficient | 1.69% | Airframe | 🟡 MEDIUM |
| 10 | Engine Labor Base Coefficient | 1.52% | Engine | 🟢 LOW |
| 11 | Engine Material Base Coefficient | 1.38% | Engine | 🟢 LOW |
| 12 | Engine Labor Thrust Coefficient | 1.37% | Engine | 🟢 LOW |
| 13 | Engine K4 Twin Shaft | 1.36% | Engine | 🟢 LOW |
| 14 | Engine Labor Thrust Exponent | 0.99% | Engine | 🟢 LOW |
| 15 | Engine K1 BPR Coefficient | 0.79% | Engine | 🟢 LOW |

---

## Key Insights

### 1. **Airframe vs Engine Parameters**
- **Top 4 parameters are all airframe-related**
- Airframe parameters collectively have higher sensitivity than engine parameters
- For regional jets like ERJ-145, airframe maintenance dominates costs

### 2. **Parameter Groupings**

**CRITICAL (>6% sensitivity):**
- `airframe_labor_base_hours` (6.7)
- `airframe_labor_weight_numerator_kg` (350,000)
- `airframe_labor_weight_denominator_offset_kg` (75,000)

**HIGH (3-6% sensitivity):**
- `airframe_labor_time_coefficient` (0.68)
- `engine_k1_base` (1.27)

**MEDIUM (1-3% sensitivity):**
- 10 parameters including k-factors and time dependencies

**LOW (<1% sensitivity):**
- 11 parameters with minimal impact on total costs

### 3. **Unused Parameters**
- `engine_k4_single_shaft` and `engine_k4_triple_shaft` have **zero sensitivity** for ERJ-145 (twin-shaft engines)
- These only matter for aircraft with different engine configurations

---

## Implications for Model Fitting

### Priority Tiers for Calibration:

#### **Tier 1: Must Fit Accurately** (Top 3)
These parameters account for ~25% of cost variance:
1. `airframe_labor_base_hours`
2. `airframe_labor_weight_numerator_kg`
3. `airframe_labor_weight_denominator_offset_kg`

**Recommendation:** Use detailed airframe maintenance records to constrain these parameters. Small errors here cause large cost prediction errors.

#### **Tier 2: Important to Fit** (Rank 4-8)
Mid-range sensitivity parameters:
- Airframe time coefficients
- Engine k1 and k2 factors

**Recommendation:** Fit using combined airframe+engine maintenance data. Can accept moderate uncertainty.

#### **Tier 3: Can Use Literature Values** (Rank >8)
Low sensitivity parameters:
- Material cost coefficients
- Thrust exponents
- BPR/OPR dependencies

**Recommendation:** Use AEA 1989a default values or adjust slightly based on fleet data. Errors here have minimal impact.

---

## Recommended Fitting Strategy

### Phase 1: Fixed Parameters (Use Defaults)
Lock low-sensitivity parameters (<1%) at AEA 1989a values:
- Material cost coefficients
- BPR/OPR exponents
- Unused k4 values

### Phase 2: Fit Critical Parameters (Optimize Top 3)
Use empirical maintenance cost data to fit:
- `airframe_labor_base_hours`
- `airframe_labor_weight_numerator_kg`
- `airframe_labor_weight_denominator_offset_kg`

**Method:** Least-squares optimization on actual maintenance costs

### Phase 3: Fine-Tune Medium Parameters (Optimize Rank 4-10)
Once critical parameters are set, adjust:
- Time coefficients
- Engine k-factors

**Method:** Residual minimization

### Phase 4: Validation
- Test on hold-out aircraft data
- Check for overfitting
- Validate against industry benchmarks

---

## Data Requirements for Fitting

### Minimum Required:
- **Actual maintenance costs** for 5+ aircraft types
- **Airframe weights** (OEW, installed engine weights)
- **Airframe prices** (delivery price or estimates)
- **Flight time profiles** (average per mission)
- **Annual utilization** (flights/year)

### Highly Valuable:
- **Split costs:** Airframe vs engine maintenance separately
- **Labor hours:** Actual maintenance man-hours per flight
- **Material costs:** Parts and consumables per flight

### Nice to Have:
- Time series data (detect trends)
- Different operators (validate robustness)
- Various mission profiles (short vs long haul)

---

## Statistical Fitting Approach

### Suggested Method: Weighted Least Squares

```python
def objective_function(params_to_fit, fixed_params, actual_data):
    """
    Minimize sum of squared errors between predicted and actual
    maintenance costs, weighted by parameter sensitivity.
    """
    predictions = []
    for aircraft in actual_data:
        # Update parameters
        updated_params = create_params(params_to_fit, fixed_params)
        
        # Calculate predicted cost
        pred_cost = calculate_maintenance_only(aircraft, updated_params)
        predictions.append(pred_cost)
    
    # Weighted residuals (weight by inverse variance or sensitivity)
    residuals = actual_data['cost'] - predictions
    weighted_residuals = residuals * weights
    
    return np.sum(weighted_residuals**2)
```

### Optimization Algorithm:
- **Start:** Scipy `minimize()` with L-BFGS-B (allows bounds)
- **Constraints:** Physical bounds on parameters (all positive, reasonable ranges)
- **Initial guess:** AEA 1989a default values
- **Validation:** 5-fold cross-validation

---

## Next Steps

1. ✅ **Complete sensitivity analysis** ← DONE
2. ⏸️ **Gather empirical maintenance data**
   - Collect actual costs from operators
   - Multiple aircraft types
   - Various utilization patterns
3. 🔄 **Implement fitting pipeline**
   - Create optimization script
   - Add parameter bounds
   - Implement cross-validation
4. 🔄 **Fit model to data**
   - Phase 1: Critical parameters
   - Phase 2: Medium parameters
   - Phase 3: Validation
5. 📊 **Document fitted parameters**
   - Compare to AEA 1989a defaults
   - Analyze residuals
   - Create calibration report

---

## Files Generated

- `sensitivity_ranking.png` - Bar chart of parameter sensitivities
- `sensitivity_tornado.png` - Tornado diagram showing ±10% impacts
- `maintenance_sensitivity_results.csv` - Complete numerical results

---

## Questions for Further Investigation

1. **Do airframe parameters vary significantly by aircraft type?**
   - Regional jets vs narrow-body vs wide-body
   
2. **How stable are these parameters over time?**
   - Aging aircraft effects
   - Technology improvements
   
3. **Can we identify aircraft-specific scaling factors?**
   - Multipliers instead of re-fitting all parameters
   
4. **What's the minimum data needed for reasonable accuracy?**
   - How many aircraft? How many data points per aircraft?

---

**Conclusion:** The sensitivity analysis successfully identifies that **3 airframe labor parameters** are critical for accurate cost prediction. Fitting efforts should focus primarily on these parameters, while less sensitive parameters can use literature values with confidence.
