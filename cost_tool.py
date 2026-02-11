"""
File: cost_tool.py
Aircraft Direct Operating Cost Tool

Author: Gabriel Bortoletto Molz
Based on: AEA 1989a/b method (Association of European Airlines)
Date: February 5, 2026
"""

from dataclasses import dataclass


@dataclass
class AircraftParameters:
    """Aircraft design and operational parameters.
    
    Attributes for utilization, pricing, and engine specifications.
    """
    # Utilization
    block_time_hours: float | None = None  # block time per flight, t_b [h]
    flight_time_hours: float | None = None  # mission flight time, t_f [h]
    flights_per_year: int | None = None # annual number of flights, n_flights [1/year]
    
    # Airplane pricing
    aircraft_delivery_price_usd: float | None = None # price of the aircraft, without spares, from manufacturer [USD]
    engine_price_usd: float | None = None # price per engine unit [USD]

    # Weights
    maximum_takeoff_weight_kg: float | None = None # aircraft MTOW [kg]
    operational_empty_weight_kg: float | None = None # aircraft OEW [kg]
    engine_weight_kg: float | None = None # engine weight per unit [kg]
    fuel_weight_kg: float | None = None  # m_f, fuel weight consumed during flight [kg]
    payload_weight_kg: float | None = None  # payload weight [kg]
    
    # Mission
    range_nm: float | None = None  # range [nautical miles]
    
    # Engine
    engine_count: int = 2  # n_E
    bypass_ratio: float | None = None  # BPR
    overall_pressure_ratio: float | None = None  # OAPR
    compressor_stages: int | None = None  # n_c (incl. fan)
    engine_shafts: int | None = None  # n_s in {1,2,3}
    takeoff_thrust_per_engine_N: float | None = None  # T_TO,E [N]

    # Crew
    cockpit_crew_count: int = 2 # Amount of dudes in the cockpit, typically 2 for transport airplanes (pilot + co-pilot)
    cabin_crew_count: int = 1 # Amount of cabin crew members, typically 1 per 50 passengers


@dataclass
class MethodParameters:
    """Cost calculation method parameters.
    
    Factors and rates used in AEA 1989a/b cost methods.
    """
    # Spares
    airframe_spares_factor: float = 0.1
    engine_spares_factor: float = 0.3
    
    # Depreciation
    depreciation_period_years: int = 16  # useful service life, n_dep [years]
    depreciation_relative_residual: float = 0.1
    
    # Interest
    interest_rate: float = 0.08
    repayment_period_years: int = 16  # repayment period, n_pay [years]
    balloon_fraction: float = 0.1
    
    # Insurance
    insurance_factor: float = 0.005  # k_ins, fraction of delivery price
    
    # Inflation
    inflation_rate: float = 0.013  # p_inf 1.3% average annual yields good results
    
    # Fuel
    fuel_price_usd: float = 0.888 * 0.7 # fuel price [USD/kg] 0.888 usd per kg = 2.7 usd per gal

    # Engine installation
    installed_engine_factor: float = 1.15 # 1.15 for jet engines in transport airplanes
    installed_engine_reverse_factor: float = 1.18 # 1.0 for non-reverse thrust engines, 1.18 for reverse thrust engines
    
    # Maintenance
    labor_rate_usd_per_hour: float = 65 # [USD/hour] 65 is the value for 1989 labor rate

    # Crew
    cabin_crew_rate_usd_per_hour : float = 0 # [USD/hour] estimated cabin crew cost per hour
    cockpit_crew_rate_usd_per_hour : float = 295 / 2 # [USD/hour] estimated cockpit crew cost per hour
    
    # Fees and charges (AEA 1989a/b values)
    landing_fee_factor: float = 0.0078 / 15  # k_LD [USD/kg] - 0.0078 for AEA 1989a, 0.0059 for AEA 1989b
    navigation_fee_factor: float = 0.00414 / 15  # k_NAV [USD/(nm·√kg)] - 0.00414 for AEA 1989a, 0.00166 for AEA 1989b
    ground_handling_factor: float = 0.10 / 15  # k_GND [USD/kg] - adjusted for realistic ground handling costs


@dataclass
class PricingBreakdown:
    """Aircraft pricing component breakdown."""
    engine_price_usd: float
    delivery_price_usd: float
    airframe_price_usd: float
    spares_price_usd: float
    purchase_price_usd: float


@dataclass
class CostBreakdown:
    """Direct operating cost breakdown by category."""
    depreciation: float
    interest: float
    insurance: float
    fuel: float
    maintenance: float
    crew: float
    fees_and_charges: float
    total: float


@dataclass
class DOCResult:
    """Complete Direct Operating Cost calculation results.
    
    Attributes:
        prices: Pricing breakdown (engine, delivery, airframe, spares, purchase)
        annual: Annual costs breakdown [USD/year]
        per_flight: Per-flight costs breakdown [USD/flight]
        per_hour: Per-hour costs breakdown [USD/flight hour]
    """
    prices: PricingBreakdown
    annual: CostBreakdown
    per_flight: CostBreakdown
    per_hour: CostBreakdown


def estimate_engine_price(
    takeoff_thrust_per_engine_N: float
) -> float:
    """Estimate engine price from takeoff thrust.
    
    Functionality:
        Estimates individual engine price based on takeoff thrust rating.
        Uses empirical power-law correlation.
        
    Args:
        takeoff_thrust_per_engine_N: Takeoff thrust per engine [N]
        
    Returns:
        float: Estimated engine price per unit [USD]
        
    Formula:
        P_E = 293 USD · (T_TO,E / N)^0.81
        where T_TO,E is thrust in Newtons
    """
    P_E = 293 * (takeoff_thrust_per_engine_N) ** 0.81
    return P_E

def estimate_purchase_price_from_oew(
    operational_empty_weight_kg: float
) -> float:
    """Estimate total aircraft purchase price from operational empty weight.
    
    Functionality:
        Estimates the aircraft acquisition cost (purchase price including spares)
        based on the operational empty weight. Uses empirical correlation formulas
        that differ based on aircraft size category.
        
    Args:
        operational_empty_weight_kg: Aircraft operational empty weight [kg]
        
    Returns:
        float: Estimated purchase price (delivery + spares) [USD]
        
    Formulas:
        For m_oe >= 10000 kg:
            C_AC = 10^6 × (1.18 × m_oe^0.48 - 116)
        For m_oe < 10000 kg:
            C_AC = -0.002695 × m_oe^2 + 1967 × m_oe - 2158000
    """
    if operational_empty_weight_kg >= 10000:
        # Large aircraft formula
        C_AC = 1e6 * (1.18 * operational_empty_weight_kg**0.48 - 116)
    else:
        # Small aircraft formula
        C_AC = (-0.002695 * operational_empty_weight_kg**2 + 
                1967 * operational_empty_weight_kg - 
                2158000)
    
    return C_AC

def calculate_delivery_price_from_oew(
    operational_empty_weight_kg: float,
    engine_price_usd: float,
    engine_count: int,
    airframe_spares_factor: float,
    engine_spares_factor: float
) -> float:
    """Calculate aircraft delivery price from OEW and component parameters.
    
    Functionality:
        Estimates the aircraft delivery price (excluding spares) by first
        estimating the total purchase price from OEW, then working backwards
        to separate out the spares investment. Uses algebraic solution to
        avoid circular dependency between delivery and spares prices.
        
    Args:
        operational_empty_weight_kg: Aircraft operational empty weight [kg]
        engine_price_usd: Price per engine unit [USD]
        engine_count: Number of engines on the aircraft
        airframe_spares_factor: Fraction of airframe price for spares (typically 0.1)
        engine_spares_factor: Fraction of total engine price for spares (typically 0.3)
        
    Returns:
        float: Aircraft delivery price (excluding spares) [USD]
        
    Mathematical derivation:
        Given: P_total = P_delivery + P_spares
               P_spares = P_AF × k_s_AF + n_E × P_E × k_s_E
               P_AF = P_delivery - n_E × P_E
        
        Solving for P_delivery:
        P_delivery = (P_total - n_E × P_E × (k_s_E - k_s_AF)) / (1 + k_s_AF)
    """
    # Estimate total purchase price from OEW
    purchase_price_usd = estimate_purchase_price_from_oew(operational_empty_weight_kg)
    
    # Calculate delivery price using algebraic solution
    # This avoids circular dependency between delivery price and spares price
    numerator = (purchase_price_usd - 
                 engine_count * engine_price_usd * (engine_spares_factor - airframe_spares_factor))
    denominator = 1 + airframe_spares_factor
    
    delivery_price_usd = numerator / denominator
    
    return delivery_price_usd

def calculate_airframe_price(
    delivery_price_usd: float,
    engine_price_usd: float,
    engine_count: int
) -> float:
    """Calculate airframe price by subtracting engine costs from delivery price.
    
    Functionality:
        Separates the airframe cost from total delivery price by removing
        the cost of all engines. Used for maintenance cost calculations.
        
    Args:
        delivery_price_usd: Aircraft delivery price from manufacturer [USD]
        engine_price_usd: Price per engine unit [USD]
        engine_count: Number of engines on the aircraft
        
    Returns:
        float: Airframe price (delivery price minus all engines) [USD]
    """
    return delivery_price_usd - engine_count * engine_price_usd

def calculate_spares_price(
    engine_price_usd: float,
    engine_count: int,
    airframe_price_usd: float,
    airframe_spares_factor: float,
    engine_spares_factor: float
) -> float:
    """Calculate total spares investment price.
    
    Functionality:
        Calculates initial spares investment as a fraction of airframe and
        engine costs. Spares are kept in inventory for maintenance.
        Based on AEA 1989a method.
        
    Args:
        engine_price_usd: Price per engine unit [USD]
        engine_count: Number of engines on the aircraft
        airframe_price_usd: Airframe price (delivery minus engines) [USD]
        airframe_spares_factor: Fraction of airframe price for spares (typically 0.1)
        engine_spares_factor: Fraction of total engine price for spares (typically 0.3)
        
    Returns:
        float: Total spares investment price [USD]
    """
    P_s_af = airframe_price_usd * airframe_spares_factor
    P_s_e = engine_price_usd * engine_count * engine_spares_factor
    P_s = P_s_af + P_s_e
    return P_s

def calculate_purchase_price(
    delivery_price_usd: float,
    spares_price_usd: float
) -> float:
    """Calculate total aircraft purchase price including spares.
    
    Functionality:
        Combines delivery price and initial spares investment to get
        total capital investment for the aircraft.
        
    Args:
        delivery_price_usd: Aircraft delivery price [USD]
        spares_price_usd: Initial spares investment [USD]
        
    Returns:
        float: Total purchase price (delivery + spares) [USD]
    """
    return delivery_price_usd + spares_price_usd


def calculate_depreciation(
    purchase_price_usd: float,
    residual_value_fraction: float,
    depreciation_period_years: int
) -> float:
    """Calculate annual depreciation cost.
    
    Functionality:
        Calculates straight-line depreciation over the useful service life.
        Assumes linear value loss from purchase price to residual value.
        Based on AEA 1989a method.
        
    Args:
        purchase_price_usd: Total aircraft purchase price (delivery + spares) [USD]
        residual_value_fraction: Residual value as fraction of purchase price (typically 0.1)
        depreciation_period_years: Useful service life for depreciation (typically 16 years)
        
    Returns:
        float: Annual depreciation cost [USD/year]
        
    Formula:
        C_dep = P_total * (1 - residual_fraction) / n_dep
    """
    C_dep = purchase_price_usd * (1 - residual_value_fraction) / depreciation_period_years
    return C_dep


def calculate_interest(
    purchase_price_usd: float,
    interest_rate: float,
    repayment_period_years: int,
    depreciation_period_years: int,
    balloon_fraction: float
) -> float:
    """Calculate annual interest cost on aircraft financing.
    
    Functionality:
        Calculates average annual interest payment considering balloon payment
        structure. Accounts for declining principal balance over time.
        Based on AEA 1989a method.
        
    Args:
        purchase_price_usd: Total aircraft purchase price [USD]
        interest_rate: Annual interest rate (e.g., 0.08 for 8%)
        repayment_period_years: Loan repayment period (typically 16 years)
        depreciation_period_years: Depreciation period (typically 16 years)
        balloon_fraction: Final balloon payment as fraction of initial price (typically 0.1)
        
    Returns:
        float: Annual interest cost [USD/year]
        
    Formula:
        p_av = [((q^n_pay - kn_k0)*(q-1))/(q^n_pay - 1)] * (n_pay/n_dep) - (1-kn_k0)/n_dep
        C_int = P_total * p_av
        where q = 1 + interest_rate
    """
    q = 1 + interest_rate
    
    p_av = (
        (((q**repayment_period_years - balloon_fraction) * (q - 1)) / 
         (q**repayment_period_years - 1)) * 
        (repayment_period_years / depreciation_period_years) - 
        (1 - balloon_fraction) / depreciation_period_years
    )
    
    C_int = purchase_price_usd * p_av
    return C_int


def calculate_insurance(
    delivery_price_usd: float,
    insurance_factor: float
) -> float:
    """Calculate annual insurance cost.
    
    Functionality:
        Calculates insurance premium as a fraction of aircraft delivery price.
        Based on AEA 1989a method.
        
    Args:
        delivery_price_usd: Aircraft delivery price [USD]
        insurance_factor: Insurance cost factor (typically 0.005, i.e., 0.5%)
        
    Returns:
        float: Annual insurance cost [USD/year]
        
    Formula:
        C_ins = P_delivery * k_ins
    """
    return delivery_price_usd * insurance_factor


def calculate_fuel(
    fuel_weight_kg: float,
    fuel_price_usd_per_kg: float,
    flights_per_year: int
) -> float:
    """Calculate annual fuel cost.
    
    Functionality:
        Calculates total fuel cost based on per-flight consumption,
        fuel price, and annual utilization.
        
    Args:
        fuel_weight_kg: Fuel weight consumed per flight [kg]
        fuel_price_usd_per_kg: Fuel price [USD/kg]
        flights_per_year: Number of flights per year
        
    Returns:
        float: Annual fuel cost [USD/year]
        
    Formula:
        C_fuel = m_f * P_f * n_flights
    """
    return fuel_weight_kg * fuel_price_usd_per_kg * flights_per_year

def calculate_installed_engine_weight(
        installed_engine_factor: float,
        installed_engine_reverse_factor: float,
        engine_weight_kg: float,
        engine_count: int,
) -> float:
    """Calculate total installed engine weight including installation equipment.
    
    Functionality:
        Calculates the total weight of all engines including installation
        equipment (mounts, cowlings, etc.) and reverse thrust system if present.
        Uses multiplication factors to account for additional hardware.
        
    Args:
        installed_engine_factor: Installation equipment factor (typically 1.15 for jet engines)
        installed_engine_reverse_factor: Reverse thrust factor (1.0 without, 1.18 with reverse thrust)
        engine_weight_kg: Bare engine weight per unit [kg]
        engine_count: Number of engines on the aircraft
        
    Returns:
        float: Total installed engine weight for all engines [kg]
        
    Formula:
        m_installed = k_install * k_reverse * m_engine * n_engines
    """
    installed_engine_weight_kg = installed_engine_factor * installed_engine_reverse_factor * engine_weight_kg * engine_count
    return installed_engine_weight_kg

def calculate_airframe_weight(
        operational_empty_weight_kg: float,
        installed_engine_weight_kg: float
) -> float:
    return operational_empty_weight_kg - installed_engine_weight_kg

def calculate_inflation_factor(
        inflation_rate: float,
        target_year: int,
        reference_year: int
) -> float:
    return (1 + inflation_rate) ** (target_year - reference_year)

def calculate_maintenance(
        # Airframe parameters
        flight_time_hours: float,
        airframe_weight_kg: float,
        airframe_price_usd: float,
        # Engine parameters
        bypass_ratio: float,
        overall_pressure_ratio: float,
        compressor_stages: int,
        engine_shafts: int,
        takeoff_thrust_per_engine_N: float,
        engine_count: int,
        # Common parameters
        flights_per_year: int,
        labor_rate_usd_per_hour: float,
        inflation_factor: float
) -> float:
    """Calculate total maintenance cost (airframe + engine).
    This is the most complicated shit took me a few hours...
    
    Functionality:
        Calculates combined airframe and engine maintenance costs based on
        aircraft characteristics and utilization. Based on AEA 1989a method.
        
    Args:
        flight_time_hours: Flight time per mission [h]
        airframe_weight_kg: Airframe weight [kg]
        airframe_price_usd: Airframe price [USD]
        bypass_ratio: Engine bypass ratio (BPR)
        overall_pressure_ratio: Overall air pressure ratio (OAPR)
        compressor_stages: Number of compressor stages including fan
        engine_shafts: Number of engine shafts (1, 2, or 3)
        takeoff_thrust_per_engine_N: Takeoff thrust per engine [N]
        engine_count: Number of engines
        flights_per_year: Number of flights per year
        labor_rate_usd_per_hour: Maintenance labor rate [USD/h]
        inflation_factor: Inflation adjustment factor k_INF
        
    Returns:
        float: Total annual maintenance cost (airframe + engine) [USD/year]
        
    Formulas (AEA 1989a):
        Airframe:
            t_M,AF,f = (1/t_f) * (9·10^-5 * m_AF + 6.7 * 350000/(m_AF + 75000)) * (0.8 + 0.68*t_f)
            C_M,M,AF,f = (1/t_f) * (4.2·10^-6 + 2.2·10^-6 * t_f) * P_AF
        Engine:
            t_M,E,f = n_E · 0.21 · k_1 · k_3 · (1 + 1.02·10^-4 · T_TO,E)^0.4 · (1 + 1.3/t_f)
            C_M,M,E,f = n_E · 2.56 · k_1 · (k_2 + k_3) · (1 + 1.02·10^-4 · T_TO,E)^0.8 · (1 + 1.3/t_f) · k_INF
    """
    # AIRFRAME MAINTENANCE
    # Maintenance labor hours per flight
    t_M_AF_f = (1 / flight_time_hours * 
                (9e-5 * airframe_weight_kg + 6.7 - 350000 / (airframe_weight_kg + 75000)) * 
                (0.8 + 0.68 * flight_time_hours))
    
    # Maintenance cost per flight
    C_M_M_AF_f = (1 / flight_time_hours * 
                  (4.2e-6 + 2.2e-6 * flight_time_hours) * 
                  airframe_price_usd)
    
    # ENGINE MAINTENANCE
    # Calculate k-factors
    k1 = 1.27 - 0.2 * bypass_ratio ** 0.2
    k2 = 0.4 * overall_pressure_ratio ** 1.3 / 20 + 0.4
    
    # k4 depends on number of engine shafts
    match engine_shafts:
        case 1:
            k4 = 0.5  # Single-shaft engine value
        case 2:
            k4 = 0.57  # Twin-shaft engine value
        case 3:
            k4 = 0.64  # Triple-shaft engine value
        case _:
            raise ValueError(f"engine_shafts must be 1, 2, or 3, got {engine_shafts}")
    
    k3 = 0.032 * compressor_stages + k4
    
    # Maintenance labor hours per flight
    t_M_E_f = (engine_count * 0.17 * k1 * k3 * 
               (1 + 1.02e-4 * takeoff_thrust_per_engine_N) ** 0.4 * 
               (1 + 1.3 / flight_time_hours))
    
    # Maintenance cost per flight
    C_M_M_E_f = (engine_count * 2.0 * k1 * (k2 + k3) * 
                 (1 + 1.02e-4 * takeoff_thrust_per_engine_N) ** 0.8 * 
                 (1 + 1.3 / flight_time_hours) * inflation_factor)
    
    # Total maintenance cost
    return ((t_M_AF_f + t_M_E_f) * labor_rate_usd_per_hour + C_M_M_AF_f + C_M_M_E_f) * flight_time_hours * flights_per_year


def calculate_crew(
        block_time_hours: float,
        flights_per_year: int,
        cockpit_crew_count: int,
        cabin_crew_count: int,
        cockpit_crew_rate_usd_per_hour: float,
        cabin_crew_rate_usd_per_hour: float
) -> float:
    """Calculate crew cost.
    
    Functionality:
        Calculates crew costs including salaries,
        training, and benefits. Based on AEA 1989b method.
        
    Returns:
        float: Annual crew cost [USD/year]
    """
    return (cockpit_crew_count * cockpit_crew_rate_usd_per_hour + 
            cabin_crew_count * cabin_crew_rate_usd_per_hour) * block_time_hours * flights_per_year


def calculate_fees_and_charges(
        maximum_takeoff_weight_kg: float,
        payload_weight_kg: float,
        range_nm: float,
        flights_per_year: int,
        landing_fee_factor: float,
        navigation_fee_factor: float,
        ground_handling_factor: float,
        inflation_factor: float
) -> float:
    """Calculate annual fees and charges.
    
    Functionality:
        Calculates total operating fees including landing fees, ATC/navigation
        charges, and ground handling charges. Based on AEA 1989a/b method.
        
    Args:
        maximum_takeoff_weight_kg: Maximum takeoff weight [kg]
        payload_weight_kg: Payload weight [kg]
        range_nm: Range [nautical miles]
        flights_per_year: Number of flights per year
        landing_fee_factor: Landing fee factor k_LD [USD/kg] 
                           (e.g., 0.0078 for AEA 1989a, 0.0059 for AEA 1989b)
        navigation_fee_factor: Navigation fee factor k_NAV [USD/(nm·√kg)]
                              (e.g., 0.00414 for AEA 1989a, 0.00166 for AEA 1989b)
        ground_handling_factor: Ground handling factor k_GND [USD/kg]
                               (e.g., 0.10 for AEA 1989a, 0.11 for AEA 1989b)
        inflation_factor: Inflation adjustment factor k_INF
        
    Returns:
        float: Total annual fees and charges [USD/year]
        
    Formulas (AEA 1989a/b):
        C_FEE,LD = k_LD · m_MTO · n_t,a · k_INF
        C_FEE,NAV = k_NAV · R · √(m_MTO) · n_t,a · k_INF
        C_FEE,GND = k_GND · m_PL · n_t,a · k_INF
        C_FEE = C_FEE,LD + C_FEE,NAV + C_FEE,GND
    """
    # Landing fees - based on maximum takeoff weight
    C_FEE_LD = (landing_fee_factor * 
                maximum_takeoff_weight_kg * 
                flights_per_year * 
                inflation_factor)
    
    # Navigation/ATC charges - based on distance and √(MTOW)
    C_FEE_NAV = (navigation_fee_factor * 
                 range_nm * 
                 (maximum_takeoff_weight_kg ** 0.5) * 
                 flights_per_year * 
                 inflation_factor)
    
    # Ground handling charges - based on payload weight
    C_FEE_GND = (ground_handling_factor * 
                 payload_weight_kg * 
                 flights_per_year * 
                 inflation_factor)
    
    # Total fees and charges
    C_FEE = C_FEE_LD + C_FEE_NAV + C_FEE_GND
    
    return C_FEE


def calculate_costs(
    aircraft: AircraftParameters,
    params: MethodParameters,
    target_year: int = 2026,
) -> DOCResult:
    """Calculate complete Direct Operating Cost breakdown.
    
    Functionality:
        Orchestrates all DOC calculations, handling both provided and estimated
        prices with proper inflation adjustments. Returns comprehensive cost 
        breakdown at annual, per-flight, and per-hour bases.
        
    Args:
        aircraft: Aircraft parameters (design, operational, pricing)
        params: Method parameters (factors, rates, spares fractions)
        target_year: Year for cost calculation (default: 2026)
        
    Returns:
        DOCResult: Comprehensive cost breakdown containing:
            - prices: PricingBreakdown with all pricing components
            - annual: CostBreakdown with annual costs [USD/year]
            - per_flight: CostBreakdown with per-flight costs [USD/flight]
            - per_hour: CostBreakdown with per-hour costs [USD/flight hour]
    
    Notes:
        - Engine price estimates are from 1999, inflation-adjusted to target_year
        - Purchase price estimates are from 2010, inflation-adjusted to target_year
        - If aircraft.engine_price_usd is provided, uses it directly
        - If aircraft.aircraft_delivery_price_usd is provided, uses it directly
    """
    
    # ========== PHASE 0: Inflation Factors ==========
    # General inflation factor (1989 -> target_year)
    inflation_factor = calculate_inflation_factor(
        params.inflation_rate,
        target_year,
        1989
    )

    labor_rate_target_year = params.labor_rate_usd_per_hour * inflation_factor
    
    # ========== PHASE 1: Pricing Estimation ==========
    # Estimate or use provided engine price
    if aircraft.engine_price_usd is not None:
        engine_price_usd = aircraft.engine_price_usd
    else:
        # Estimate from thrust (1999 baseline) and inflate to target year
        engine_price_1999 = estimate_engine_price(aircraft.takeoff_thrust_per_engine_N)
        engine_inflation = calculate_inflation_factor(params.inflation_rate, target_year, 1999)
        engine_price_usd = engine_price_1999 * engine_inflation
    
    # Estimate or use provided delivery price
    if aircraft.aircraft_delivery_price_usd is not None:
        delivery_price_usd = aircraft.aircraft_delivery_price_usd
    else:
        # Estimate from OEW (2010 baseline) and inflate to target year
        # delivery_price_1999 = calculate_delivery_price_from_oew(
        #     aircraft.operational_empty_weight_kg,
        #     engine_price_usd,
        #     aircraft.engine_count,
        #     params.airframe_spares_factor,
        #     params.engine_spares_factor
        # )

        delivery_price_1999 = 860 * aircraft.operational_empty_weight_kg
        delivery_inflation = calculate_inflation_factor(params.inflation_rate, target_year, 1999)
        delivery_price_usd = delivery_price_1999 * delivery_inflation
    
    # Calculate airframe price (delivery minus engines)
    airframe_price_usd = calculate_airframe_price(
        delivery_price_usd,
        engine_price_usd,
        aircraft.engine_count
    )
    
    # Calculate spares price
    spares_price_usd = calculate_spares_price(
        engine_price_usd,
        aircraft.engine_count,
        airframe_price_usd,
        params.airframe_spares_factor,
        params.engine_spares_factor
    )
    
    # Calculate total purchase price
    purchase_price_usd = calculate_purchase_price(delivery_price_usd, spares_price_usd)
    
    # ========== PHASE 2: Weight Calculations ==========
    
    installed_engine_weight_kg = calculate_installed_engine_weight(
        params.installed_engine_factor,
        params.installed_engine_reverse_factor,
        aircraft.engine_weight_kg,
        aircraft.engine_count
    )
    
    airframe_weight_kg = calculate_airframe_weight(
        aircraft.operational_empty_weight_kg,
        installed_engine_weight_kg
    )
    
    # ========== PHASE 3: Fixed Costs (Annual) ==========
    depreciation = calculate_depreciation(
        purchase_price_usd,
        params.depreciation_relative_residual,
        params.depreciation_period_years
    )
    
    interest = calculate_interest(
        purchase_price_usd,
        params.interest_rate,
        params.repayment_period_years,
        params.depreciation_period_years,
        params.balloon_fraction
    )
    
    insurance = calculate_insurance(
        delivery_price_usd,
        params.insurance_factor
    )
    
    # ========== PHASE 4: Variable Costs (Annual) ==========
    fuel = calculate_fuel(
        aircraft.fuel_weight_kg,
        params.fuel_price_usd,
        aircraft.flights_per_year
    )
    
    maintenance = calculate_maintenance(
        aircraft.flight_time_hours,
        airframe_weight_kg,
        airframe_price_usd,
        aircraft.bypass_ratio,
        aircraft.overall_pressure_ratio,
        aircraft.compressor_stages,
        aircraft.engine_shafts,
        aircraft.takeoff_thrust_per_engine_N,
        aircraft.engine_count,
        aircraft.flights_per_year,
        labor_rate_target_year,
        inflation_factor
    )
    
    crew = calculate_crew(
        aircraft.block_time_hours,
        aircraft.flights_per_year,
        aircraft.cockpit_crew_count,
        aircraft.cabin_crew_count,
        params.cockpit_crew_rate_usd_per_hour,
        params.cabin_crew_rate_usd_per_hour
    )
    
    fees_and_charges = calculate_fees_and_charges(
        aircraft.maximum_takeoff_weight_kg,
        aircraft.payload_weight_kg,
        aircraft.range_nm,
        aircraft.flights_per_year,
        params.landing_fee_factor,
        params.navigation_fee_factor,
        params.ground_handling_factor,
        inflation_factor
    )
    
    # ========== PHASE 5: Aggregate and Normalize ==========
    # Annual totals
    total_annual = depreciation + interest + insurance + fuel + maintenance + crew + fees_and_charges
    
    annual_costs = CostBreakdown(
        depreciation=depreciation,
        interest=interest,
        insurance=insurance,
        fuel=fuel,
        maintenance=maintenance,
        crew=crew,
        fees_and_charges=fees_and_charges,
        total=total_annual
    )
    
    # Per-flight costs
    per_flight_costs = CostBreakdown(
        depreciation=depreciation / aircraft.flights_per_year,
        interest=interest / aircraft.flights_per_year,
        insurance=insurance / aircraft.flights_per_year,
        fuel=fuel / aircraft.flights_per_year,
        maintenance=maintenance / aircraft.flights_per_year,
        crew=crew / aircraft.flights_per_year,
        fees_and_charges=fees_and_charges / aircraft.flights_per_year,
        total=total_annual / aircraft.flights_per_year
    )
    
    # Per-hour costs
    total_flight_hours = aircraft.flights_per_year * aircraft.flight_time_hours
    per_hour_costs = CostBreakdown(
        depreciation=depreciation / total_flight_hours,
        interest=interest / total_flight_hours,
        insurance=insurance / total_flight_hours,
        fuel=fuel / total_flight_hours,
        maintenance=maintenance / total_flight_hours,
        crew=crew / total_flight_hours,
        fees_and_charges=fees_and_charges / total_flight_hours,
        total=total_annual / total_flight_hours
    )
    
    # Pricing breakdown
    pricing = PricingBreakdown(
        engine_price_usd=engine_price_usd,
        delivery_price_usd=delivery_price_usd,
        airframe_price_usd=airframe_price_usd,
        spares_price_usd=spares_price_usd,
        purchase_price_usd=purchase_price_usd
    )
    
    # ========== PHASE 6: Return Comprehensive Results ==========
    return DOCResult(
        prices=pricing,
        annual=annual_costs,
        per_flight=per_flight_costs,
        per_hour=per_hour_costs
    )

