"""
File: maintenance_sensitivity_analysis.py
Maintenance Cost Model Sensitivity Analysis

Author: Gabriel Bortoletto Molz
Date: February 11, 2026

Performs sensitivity analysis on all maintenance model parameters to identify
which coefficients have the greatest impact on total maintenance costs.
This informs which parameters should be prioritized during model fitting.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import fields, replace
from typing import Dict, List, Tuple
import designTool_learis as dt
from cost_tool import (
    AircraftParameters, 
    MethodParameters, 
    MaintenanceParameters,
    calculate_costs,
)


def hhmmss_to_hours(time_str):
    """Convert HH:MM:SS time string to decimal hours."""
    h, m, s = map(int, time_str.split(":"))
    return h + m/60 + s/3600


def calculate_maintenance_only(
    aircraft: AircraftParameters, 
    params: MethodParameters
) -> float:
    """Extract just the maintenance cost from full DOC calculation."""
    result = calculate_costs(aircraft, params, target_year=2025)
    return result.per_flight.maintenance


def sensitivity_analysis(
    aircraft: AircraftParameters,
    base_params: MethodParameters,
    perturbation_fractions: List[float] = [-0.20, -0.10, 0.10, 0.20]
) -> pd.DataFrame:
    """
    Perform one-at-a-time sensitivity analysis on all maintenance parameters.
    
    Args:
        aircraft: Aircraft configuration to analyze
        base_params: Baseline method parameters
        perturbation_fractions: Fractional perturbations to apply (e.g., 0.10 = +10%)
    
    Returns:
        DataFrame with sensitivity results for each parameter
    """
    # Calculate baseline maintenance cost
    base_cost = calculate_maintenance_only(aircraft, base_params)
    
    results = []
    
    # Get all maintenance parameter fields
    maint_fields = fields(MaintenanceParameters)
    
    for field in maint_fields:
        param_name = field.name
        base_value = getattr(base_params.maintenance, param_name)
        
        # Skip if base value is zero (can't calculate percentage change)
        if base_value == 0:
            continue
        
        param_results = {
            'parameter': param_name,
            'base_value': base_value,
            'base_cost': base_cost,
        }
        
        # Test each perturbation
        for frac in perturbation_fractions:
            # Create perturbed parameter set
            new_value = base_value * (1 + frac)
            new_maint_params = replace(
                base_params.maintenance,
                **{param_name: new_value}
            )
            new_params = replace(base_params, maintenance=new_maint_params)
            
            # Calculate new cost
            new_cost = calculate_maintenance_only(aircraft, new_params)
            
            # Calculate absolute and relative changes
            abs_change = new_cost - base_cost
            rel_change = (new_cost / base_cost - 1) * 100 if base_cost != 0 else 0
            
            # Store results
            param_results[f'cost_{int(frac*100):+d}pct'] = new_cost
            param_results[f'abs_change_{int(frac*100):+d}pct'] = abs_change
            param_results[f'rel_change_{int(frac*100):+d}pct'] = rel_change
        
        # Calculate sensitivity coefficient (average absolute relative change per 10% perturbation)
        sensitivity_scores = []
        for frac in perturbation_fractions:
            rel_change = param_results[f'rel_change_{int(frac*100):+d}pct']
            # Normalize to per 10% perturbation
            sensitivity = abs(rel_change) / abs(frac * 100) * 10
            sensitivity_scores.append(sensitivity)
        
        param_results['sensitivity'] = np.mean(sensitivity_scores)
        param_results['sensitivity_std'] = np.std(sensitivity_scores)
        
        results.append(param_results)
    
    # Convert to DataFrame and sort by sensitivity
    df = pd.DataFrame(results)
    df = df.sort_values('sensitivity', ascending=False)
    
    return df


def plot_sensitivity_tornado(
    df: pd.DataFrame, 
    perturbation_pct: float = 10.0,
    top_n: int = 15,
    save_path: str = None
):
    """
    Create tornado diagram showing parameter sensitivities.
    
    Args:
        df: Sensitivity analysis results DataFrame
        perturbation_pct: Which perturbation to visualize (e.g., 10.0 for ±10%)
        top_n: Number of top parameters to show
        save_path: Optional path to save figure
    """
    # Select top N most sensitive parameters
    df_plot = df.head(top_n).copy()
    
    # Get the low and high values for the specified perturbation
    low_col = f'rel_change_{-int(perturbation_pct):+d}pct'
    high_col = f'rel_change_{int(perturbation_pct):+d}pct'
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = np.arange(len(df_plot))
    
    # Plot bars
    for i, (idx, row) in enumerate(df_plot.iterrows()):
        low_val = row[low_col]
        high_val = row[high_col]
        
        # Bar from low to high
        ax.barh(i, high_val - low_val, left=low_val, height=0.7, 
               color='steelblue', alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Formatting
    ax.set_yticks(y_pos)
    ax.set_yticklabels([name.replace('_', ' ').title() for name in df_plot['parameter']])
    ax.set_xlabel(f'Change in Maintenance Cost [%]\n(for ±{perturbation_pct:.0f}% parameter change)', 
                  fontsize=11, fontweight='bold')
    ax.set_title('Maintenance Cost Model - Parameter Sensitivity Analysis\n(Tornado Diagram)', 
                fontsize=13, fontweight='bold', pad=20)
    
    # Add zero line
    ax.axvline(x=0, color='black', linewidth=1.5, linestyle='-', alpha=0.8)
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def plot_sensitivity_ranking(
    df: pd.DataFrame, 
    top_n: int = 20,
    save_path: str = None
):
    """
    Create bar chart ranking parameters by sensitivity coefficient.
    
    Args:
        df: Sensitivity analysis results DataFrame
        top_n: Number of top parameters to show
        save_path: Optional path to save figure
    """
    df_plot = df.head(top_n).copy()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Color code by parameter category
    colors = []
    for param in df_plot['parameter']:
        if 'airframe' in param:
            colors.append('coral')
        elif 'engine' in param:
            colors.append('steelblue')
        else:
            colors.append('gray')
    
    y_pos = np.arange(len(df_plot))
    ax.barh(y_pos, df_plot['sensitivity'], color=colors, alpha=0.8, 
           edgecolor='black', linewidth=0.5)
    
    # Error bars for sensitivity std
    ax.errorbar(df_plot['sensitivity'], y_pos, 
               xerr=df_plot['sensitivity_std'], 
               fmt='none', color='black', alpha=0.6, capsize=3)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([name.replace('_', ' ').title() for name in df_plot['parameter']])
    ax.set_xlabel('Sensitivity Coefficient\n(% Cost Change per 10% Parameter Change)', 
                  fontsize=11, fontweight='bold')
    ax.set_title('Maintenance Model Parameter Sensitivity Ranking', 
                fontsize=13, fontweight='bold', pad=20)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='coral', edgecolor='black', label='Airframe Parameters'),
        Patch(facecolor='steelblue', edgecolor='black', label='Engine Parameters'),
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()


def print_sensitivity_summary(df: pd.DataFrame, top_n: int = 10):
    """Print summary of sensitivity analysis results."""
    print("\n" + "="*80)
    print("MAINTENANCE COST MODEL - SENSITIVITY ANALYSIS SUMMARY")
    print("="*80)
    print(f"\nBaseline Maintenance Cost: ${df.iloc[0]['base_cost']:.2f} per flight\n")
    
    print(f"TOP {top_n} MOST SENSITIVE PARAMETERS:")
    print("-"*80)
    print(f"{'Rank':<6} {'Parameter':<40} {'Sensitivity':<12} {'Base Value':<15}")
    print("-"*80)
    
    for i, (idx, row) in enumerate(df.head(top_n).iterrows(), 1):
        param_name = row['parameter'].replace('_', ' ').title()
        sensitivity = row['sensitivity']
        base_val = row['base_value']
        
        print(f"{i:<6} {param_name:<40} {sensitivity:>8.4f}%     {base_val:>12.4e}")
    
    print("-"*80)
    print("\nInterpretation:")
    print("Sensitivity = % change in maintenance cost per 10% change in parameter")
    print("Higher sensitivity → More important for model fitting")
    print("="*80 + "\n")


def export_sensitivity_results(df: pd.DataFrame, filepath: str = "sensitivity_results.csv"):
    """Export detailed sensitivity results to CSV."""
    df.to_csv(filepath, index=False)
    print(f"✓ Sensitivity results exported to: {filepath}")


# ========== MAIN ANALYSIS ==========
if __name__ == "__main__":
    print("\n" + "="*80)
    print("STARTING MAINTENANCE COST SENSITIVITY ANALYSIS")
    print("="*80)
    
    # Define aircraft configuration (ERJ-145 XR)
    aircraft = AircraftParameters(
        # Utilization
        block_time_hours=hhmmss_to_hours("2:20:00"),
        flight_time_hours=hhmmss_to_hours("2:05:13"),
        flights_per_year=1200,
        
        # Weights
        maximum_takeoff_weight_kg=48501 / 2.205,
        operational_empty_weight_kg=27550 / 2.205,
        engine_weight_kg=751.6,
        fuel_weight_kg=2664,
        payload_weight_kg=5403,
        
        # Mission
        range_nm=689,
        
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
    )
    
    # Baseline parameters
    base_params = MethodParameters()
    
    print("\n► Running sensitivity analysis...")
    print(f"   Aircraft: ERJ-145 XR")
    print(f"   Testing perturbations: ±10%, ±20%")
    print(f"   Number of parameters: {len(fields(MaintenanceParameters))}")
    
    # Perform analysis
    results_df = sensitivity_analysis(
        aircraft, 
        base_params,
        perturbation_fractions=[-0.20, -0.10, 0.10, 0.20]
    )
    
    # Print summary
    print_sensitivity_summary(results_df, top_n=15)
    
    # Export results
    export_sensitivity_results(results_df, "maintenance_sensitivity_results.csv")
    
    # Create visualizations
    print("\n► Generating visualizations...")
    plot_sensitivity_ranking(results_df, top_n=20, 
                            save_path="sensitivity_ranking.png")
    plot_sensitivity_tornado(results_df, perturbation_pct=10.0, top_n=15,
                            save_path="sensitivity_tornado.png")
    
    print("\n✓ Sensitivity analysis complete!")
    print("="*80 + "\n")
