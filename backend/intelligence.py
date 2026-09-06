"""
AgroFast Intelligence Module
Provides transparent, deterministic agronomic calculations for:
1. Farm Health Score (0-100) with factor breakdowns, positives, and warnings
2. Environmental Disease Risk Estimation (LOW, MODERATE, HIGH, CRITICAL)
3. Smart Irrigation Recommendations & Water Requirements
4. Smart NPK / Fertilizer Decision Support
5. Crop Profitability Simulation & Multi-Crop Comparison
"""

from typing import Dict, List, Any, Optional
import math
from datetime import datetime

# Crop baseline requirements
CROP_AGRONOMY = {
    "Maize": {
        "ideal_temp": 24, "temp_range": (18, 32),
        "ideal_hum": 60, "hum_range": (50, 75),
        "water_needs_mm_week": 35,
        "ideal_n": 60, "ideal_p": 45, "ideal_k": 40,
        "base_yield_tons": 2.5, "base_price_kg": 45,
        "base_seed_cost": 4500, "base_fert_cost": 8000, "base_labor_cost": 10000
    },
    "Tomato": {
        "ideal_temp": 23, "temp_range": (18, 28),
        "ideal_hum": 60, "hum_range": (50, 70),
        "water_needs_mm_week": 45,
        "ideal_n": 50, "ideal_p": 65, "ideal_k": 70,
        "base_yield_tons": 12.0, "base_price_kg": 75,
        "base_seed_cost": 9000, "base_fert_cost": 15000, "base_labor_cost": 22000
    },
    "Potato": {
        "ideal_temp": 18, "temp_range": (14, 24),
        "ideal_hum": 65, "hum_range": (55, 80),
        "water_needs_mm_week": 35,
        "ideal_n": 50, "ideal_p": 50, "ideal_k": 75,
        "base_yield_tons": 9.0, "base_price_kg": 40,
        "base_seed_cost": 12000, "base_fert_cost": 14000, "base_labor_cost": 16000
    },
    "Beans": {
        "ideal_temp": 21, "temp_range": (16, 27),
        "ideal_hum": 65, "hum_range": (55, 75),
        "water_needs_mm_week": 25,
        "ideal_n": 30, "ideal_p": 50, "ideal_k": 45,
        "base_yield_tons": 1.2, "base_price_kg": 110,
        "base_seed_cost": 4000, "base_fert_cost": 5000, "base_labor_cost": 8000
    },
    "Coffee": {
        "ideal_temp": 22, "temp_range": (15, 26),
        "ideal_hum": 75, "hum_range": (60, 85),
        "water_needs_mm_week": 30,
        "ideal_n": 65, "ideal_p": 35, "ideal_k": 65,
        "base_yield_tons": 2.0, "base_price_kg": 180,
        "base_seed_cost": 8000, "base_fert_cost": 18000, "base_labor_cost": 25000
    },
    "Rice": {
        "ideal_temp": 28, "temp_range": (22, 34),
        "ideal_hum": 80, "hum_range": (70, 90),
        "water_needs_mm_week": 60,
        "ideal_n": 70, "ideal_p": 50, "ideal_k": 45,
        "base_yield_tons": 3.0, "base_price_kg": 90,
        "base_seed_cost": 5000, "base_fert_cost": 11000, "base_labor_cost": 14000
    },
    "Wheat": {
        "ideal_temp": 18, "temp_range": (12, 25),
        "ideal_hum": 55, "hum_range": (45, 70),
        "water_needs_mm_week": 28,
        "ideal_n": 65, "ideal_p": 45, "ideal_k": 40,
        "base_yield_tons": 2.2, "base_price_kg": 55,
        "base_seed_cost": 4500, "base_fert_cost": 9000, "base_labor_cost": 7500
    }
}

# Soil water retention coefficients
SOIL_RETENTION = {
    "clay": 1.3,
    "black soil": 1.3,
    "loam": 1.0,
    "alluvial soil": 1.1,
    "red soil": 0.9,
    "sandy": 0.7,
    "arid soil": 0.65,
    "laterite soil": 0.85,
    "mountain soil": 0.95
}

def _match_crop(crop_name: str) -> tuple:
    name = (crop_name or "").strip().lower()
    for k, v in CROP_AGRONOMY.items():
        if k.lower() in name or name in k.lower():
            return k, v
    return "Maize", CROP_AGRONOMY["Maize"]

# =========================================================================
# 1. FARM HEALTH SCORE ENGINE
# =========================================================================
def calculate_farm_health_score(
    farm: Dict[str, Any],
    recent_scans: Optional[List[Dict[str, Any]]] = None,
    weather: Optional[Dict[str, Any]] = None,
    expenses: Optional[List[Dict[str, Any]]] = None,
    tasks: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Transparently calculates a 0-100 Farm Health Score.
    Factor Weights:
    - Crop Scan Health & Diagnostic History: 30 pts
    - NPK Nutrient Balance: 20 pts
    - Irrigation & Water Source: 15 pts
    - Weather Stress & Environmental Fit: 15 pts
    - Budget / Financial Health: 10 pts
    - Activity & Task Completion: 10 pts
    """
    positives = []
    warnings = []
    breakdown = {}

    crop_name, agronomy = _match_crop(farm.get("crop", ""))

    # -------------------------------------------------------------
    # 1. Diagnostic Scan History (Max 30)
    # -------------------------------------------------------------
    scan_score = 25 # Default baseline when no scans yet
    farm_id = str(farm.get("id") or "")
    
    # Filter scans for this farm (or matching crop if farmId missing)
    matching_scans = []
    for s in (recent_scans or []):
        s_farm_id = str(s.get("farmId") or "")
        s_crop = (s.get("crop") or "").lower()
        if (farm_id and s_farm_id == farm_id) or (s_crop and s_crop in crop_name.lower()):
            matching_scans.append(s)

    if matching_scans:
        recent = matching_scans[:5] # evaluate last 5 scans
        healthy_count = sum(1 for s in recent if "healthy" in (s.get("disease") or "").lower())
        ratio = healthy_count / float(len(recent))
        scan_score = round(ratio * 30, 1)

        if ratio >= 0.8:
            positives.append(f"High crop health: {int(ratio*100)}% of recent scans show healthy foliage.")
        elif ratio <= 0.4:
            warnings.append(f"Disease presence detected: {int((1-ratio)*100)}% of recent scans identified infections.")
        else:
            positives.append(f"Moderate crop health: {int(ratio*100)}% healthy scans.")
    else:
        positives.append("No active disease outbreaks logged in scan records.")
    breakdown["scan_health"] = {"score": scan_score, "max": 30}

    # -------------------------------------------------------------
    # 2. NPK Nutrient Balance (Max 20)
    # -------------------------------------------------------------
    soil = farm.get("soil") or {}
    n = float(soil.get("n", 45))
    p = float(soil.get("p", 30))
    k = float(soil.get("k", 25))

    ideal_n = agronomy["ideal_n"]
    ideal_p = agronomy["ideal_p"]
    ideal_k = agronomy["ideal_k"]

    # Deviations
    n_dev = abs(n - ideal_n) / 100.0
    p_dev = abs(p - ideal_p) / 100.0
    k_dev = abs(k - ideal_k) / 100.0
    avg_dev = (n_dev + p_dev + k_dev) / 3.0

    npk_score = max(0.0, round(20 * (1.0 - (avg_dev * 1.3)), 1))
    npk_score = min(20.0, npk_score)

    if n < ideal_n - 15:
        warnings.append(f"Nitrogen level ({int(n)}%) is below ideal ({ideal_n}%) for {crop_name}.")
    elif n >= ideal_n - 10:
        positives.append(f"Nitrogen level ({int(n)}%) is well-aligned for {crop_name} vegetative vigor.")

    if p < ideal_p - 15:
        warnings.append(f"Phosphorus level ({int(p)}%) is low for {crop_name} root & flower development.")
    if k < ideal_k - 15:
        warnings.append(f"Potassium level ({int(k)}%) is low, increasing drought and disease vulnerability.")

    breakdown["nutrient_balance"] = {"score": npk_score, "max": 20}

    # -------------------------------------------------------------
    # 3. Irrigation & Water Management (Max 15)
    # -------------------------------------------------------------
    irrigation = (farm.get("irrigation") or "").lower()
    water_source = (farm.get("waterSource") or "").lower()
    
    irrig_score = 12.0
    if "drip" in irrigation:
        irrig_score = 15.0
        positives.append("Drip irrigation provides high water efficiency and reduces foliar disease.")
    elif "sprinkler" in irrigation:
        irrig_score = 12.5
        positives.append("Sprinkler irrigation provides consistent coverage.")
    elif "rain" in irrigation:
        irrig_score = 9.5
        warnings.append("Rainfed cultivation is subject to seasonal dry spell vulnerabilities.")
    else:
        irrig_score = 11.0

    if "borehole" in water_source or "river" in water_source:
        positives.append(f"Reliable water source ({water_source.capitalize()}) supports steady irrigation.")

    breakdown["irrigation_management"] = {"score": irrig_score, "max": 15}

    # -------------------------------------------------------------
    # 4. Weather Stress & Environment (Max 15)
    # -------------------------------------------------------------
    weather_score = 13.0
    if weather:
        temp = float(weather.get("temp", agronomy["ideal_temp"]))
        hum = float(weather.get("humidity", agronomy["ideal_hum"]))
        min_t, max_t = agronomy["temp_range"]
        min_h, max_h = agronomy["hum_range"]

        temp_penalty = 0.0
        if temp < min_t or temp > max_t:
            temp_penalty = min(5.0, abs(temp - agronomy["ideal_temp"]) * 0.7)
            warnings.append(f"Current temperature ({int(temp)}°C) is outside the ideal {min_t}-{max_t}°C window for {crop_name}.")
        else:
            positives.append(f"Temperature ({int(temp)}°C) is well-suited for {crop_name} growth.")

        hum_penalty = 0.0
        if hum > 80:
            hum_penalty = 3.5
            warnings.append(f"High relative humidity ({int(hum)}%) creates elevated fungal disease pressure.")
        elif hum < 35:
            hum_penalty = 2.5
            warnings.append(f"Low humidity ({int(hum)}%) may cause plant moisture stress.")
        else:
            positives.append(f"Relative humidity ({int(hum)}%) is balanced.")

        weather_score = max(4.0, round(15.0 - temp_penalty - hum_penalty, 1))
    else:
        positives.append("Weather conditions within normal seasonal parameters.")

    breakdown["weather_adaptation"] = {"score": weather_score, "max": 15}

    # -------------------------------------------------------------
    # 5. Financial / Budget Status (Max 10)
    # -------------------------------------------------------------
    budget = float(farm.get("budget") or 0)
    spent = 0.0
    for exp in (expenses or []):
        exp_farm = str(exp.get("farmId") or "")
        if not farm_id or exp_farm == farm_id:
            spent += float(exp.get("amount") or 0)

    budget_score = 9.0
    if budget > 0:
        ratio = spent / budget
        if ratio > 1.0:
            budget_score = 4.0
            warnings.append(f"Farm spending ({int(ratio*100)}%) has exceeded total allocated budget.")
        elif ratio >= 0.85:
            budget_score = 6.5
            warnings.append(f"Farm spending is near budget limit ({int(ratio*100)}% utilized).")
        else:
            budget_score = 10.0
            positives.append(f"Healthy budget management ({int(ratio*100)}% utilized).")
    else:
        budget_score = 8.5
        positives.append("Operational spending on track.")

    breakdown["budget_health"] = {"score": budget_score, "max": 10}

    # -------------------------------------------------------------
    # 6. Farm Activity & Task Completion (Max 10)
    # -------------------------------------------------------------
    task_score = 8.0
    if tasks:
        matching_tasks = [t for t in tasks if not farm_id or str(t.get("farmId") or "") in [farm_id, ""]]
        if matching_tasks:
            completed = sum(1 for t in matching_tasks if t.get("completed"))
            t_ratio = completed / float(len(matching_tasks))
            task_score = max(3.0, round(t_ratio * 10.0, 1))
            if t_ratio >= 0.7:
                positives.append(f"Great field management: {completed}/{len(matching_tasks)} tasks completed.")
            else:
                warnings.append(f"Pending tasks: {len(matching_tasks) - completed} farm maintenance tasks overdue.")

    breakdown["farm_activity"] = {"score": task_score, "max": 10}

    # Calculate Total
    total_score = round(sum(item["score"] for item in breakdown.values()))
    total_score = max(10, min(100, total_score))

    if total_score >= 85:
        rating = "Excellent"
    elif total_score >= 70:
        rating = "Good"
    elif total_score >= 50:
        rating = "Fair"
    else:
        rating = "Needs Attention"

    return {
        "score": total_score,
        "rating": rating,
        "crop": crop_name,
        "positives": positives[:4],
        "warnings": warnings[:4],
        "breakdown": breakdown
    }

# =========================================================================
# 2. ENVIRONMENTAL DISEASE RISK PREDICTION ENGINE
# =========================================================================
def calculate_disease_risk(
    crop_name: str,
    weather: Dict[str, Any],
    recent_scans: Optional[List[Dict[str, Any]]] = None,
    farm_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Estimates environmental disease risk transparently based on:
    - Temperature range for fungal / bacterial sporulation
    - Relative humidity levels
    - Precipitation (current or forecast)
    - Prior disease detection history
    """
    crop, agronomy = _match_crop(crop_name)
    temp = float(weather.get("temp", 24))
    humidity = float(weather.get("humidity", 65))
    precip = float(weather.get("precipitation", 0) or 0)
    rain_prob = float(weather.get("rain_probability", 0) or 0)

    risk_points = 15 # baseline background risk
    reasons = []

    # 1. Humidity factor (fungal spore germination)
    if humidity >= 85:
        risk_points += 32
        reasons.append(f"Critically high humidity ({int(humidity)}%) creates prolonged leaf wetness favoring fungal blights.")
    elif humidity >= 75:
        risk_points += 22
        reasons.append(f"Elevated humidity ({int(humidity)}%) supports rapid spore germination.")
    elif humidity <= 45:
        risk_points -= 8
        reasons.append(f"Dry atmospheric conditions ({int(humidity)}% humidity) inhibit foliar fungal spread.")

    # 2. Temperature factor (warm temperatures 20-28°C accelerate pathogens)
    if 20 <= temp <= 27:
        risk_points += 18
        reasons.append(f"Warm ambient temperature ({int(temp)}°C) is ideal for pathogen replication.")
    elif temp > 32:
        risk_points -= 5
        reasons.append(f"High heat ({int(temp)}°C) slows down many common leaf spot fungi.")
    elif temp < 14:
        risk_points -= 5
        reasons.append(f"Cool temperature ({int(temp)}°C) retards pathogen incubation.")

    # 3. Rainfall factor
    if precip > 5.0 or rain_prob >= 70:
        risk_points += 20
        reasons.append("Expected rainfall will cause soil splashing and prolonged leaf surface moisture.")
    elif precip > 0.5 or rain_prob >= 40:
        risk_points += 10
        reasons.append("Moderate rain probability keeps canopy wet.")

    # 4. History factor
    if recent_scans:
        recent_diseased = 0
        for s in recent_scans[-6:]:
            d = (s.get("disease") or "").lower()
            if d and "healthy" not in d and "soil" not in d:
                recent_diseased += 1
        if recent_diseased >= 2:
            risk_points += 18
            reasons.append(f"Previous disease symptoms detected in {recent_diseased} recent scans on this farm.")
        elif recent_diseased == 1:
            risk_points += 8
            reasons.append("Active disease previously detected in recent scan record.")

    risk_score = max(5, min(95, risk_points))

    if risk_score >= 80:
        level = "CRITICAL"
        alert = True
        recommendation = "Inspect crops within 24 hours. Apply preventative organic or systemic protection if rain is imminent."
    elif risk_score >= 65:
        level = "HIGH"
        alert = True
        recommendation = "High disease pressure. Avoid overhead irrigation and monitor lower leaves for lesions."
    elif risk_score >= 40:
        level = "MODERATE"
        alert = False
        recommendation = "Moderate environmental risk. Maintain routine field scouting twice weekly."
    else:
        level = "LOW"
        alert = False
        recommendation = "Conditions are unfavorable for major disease outbreaks. Standard monitoring is sufficient."

    return {
        "risk_score": risk_score,
        "risk_level": level,
        "crop": crop,
        "reasons": reasons,
        "recommendation": recommendation,
        "alert_triggered": alert,
        "disclaimer": "This is an environmental risk estimate based on atmospheric and historical data, not a guarantee of disease occurrence."
    }

# =========================================================================
# 3. SMART IRRIGATION ADVISOR ENGINE
# =========================================================================
def calculate_irrigation_advice(
    farm: Dict[str, Any],
    weather: Dict[str, Any],
    forecast_rain_mm: float = 0.0
) -> Dict[str, Any]:
    """
    Computes intelligent irrigation guidance:
    - Action: irrigate now / delay / do not irrigate
    - Irrigation window
    - Estimated water requirement (liters and mm)
    """
    crop_name, agronomy = _match_crop(farm.get("crop", ""))
    farm_size = float(farm.get("size", 1.0) or 1.0)
    soil_type = (farm.get("soilType") or "Loam").lower()
    irrigation_type = (farm.get("irrigation") or "Drip").lower()

    precip = float(weather.get("precipitation", 0) or 0)
    rain_prob = float(weather.get("rain_probability", 0) or 0)
    temp = float(weather.get("temp", 24))
    humidity = float(weather.get("humidity", 60))

    # Base crop requirement mm per day
    base_daily_mm = agronomy["water_needs_mm_week"] / 7.0

    # Evapotranspiration adjustment
    # Higher temp and lower humidity increase water loss
    et_mult = 1.0 + ((temp - 20.0) * 0.03) - ((humidity - 60.0) * 0.01)
    et_mult = max(0.6, min(1.6, et_mult))

    # Soil retention factor
    retention = 1.0
    for s_key, s_val in SOIL_RETENTION.items():
        if s_key in soil_type:
            retention = s_val
            break

    effective_daily_mm = (base_daily_mm * et_mult) / retention

    # 1 mm of rain on 1 acre = 4,046 Liters
    liters_per_acre = round(effective_daily_mm * 4046.86)
    total_liters = round(liters_per_acre * farm_size)

    # Decision logic
    if forecast_rain_mm >= 5.0 or (precip >= 3.0 and rain_prob >= 65):
        action = "Do not irrigate today"
        reason = f"Substantial rainfall ({forecast_rain_mm or precip} mm) is expected. Conserve water and prevent waterlogging."
        window = "Delay irrigation until rain ends and soil is checked"
        liters_needed = 0
    elif forecast_rain_mm >= 2.0 or rain_prob >= 50:
        action = "Reduce irrigation volume by 50%"
        reason = f"Moderate chance of rain ({int(rain_prob)}%). Light watering is sufficient."
        window = "Early morning (06:00 - 08:00)"
        liters_needed = round(total_liters * 0.5)
    elif temp >= 30:
        action = "Irrigate thoroughly"
        reason = f"High temperature ({int(temp)}°C) increases evapotranspiration. Early watering prevents wilt."
        window = "Early morning (06:00 - 08:30) or Evening (17:30 - 19:00)"
        liters_needed = total_liters
    else:
        action = "Standard scheduled irrigation"
        reason = f"Mild conditions ({int(temp)}°C, {int(humidity)}% humidity). Maintain regular root zone moisture."
        window = "Morning (06:30 - 09:00)"
        liters_needed = total_liters

    return {
        "action": action,
        "reason": reason,
        "irrigation_window": window,
        "estimated_water_liters": liters_needed,
        "liters_per_acre": round(liters_needed / farm_size) if farm_size > 0 else liters_needed,
        "expected_rain_mm": round(forecast_rain_mm, 1),
        "soil_type": soil_type.capitalize(),
        "irrigation_type": irrigation_type.capitalize(),
        "disclaimer": "Agricultural water estimates are based on crop evapotranspiration models. Adjust based on physical soil moisture inspection."
    }

# =========================================================================
# 4. SMART NPK / FERTILIZER ADVISOR ENGINE
# =========================================================================
def calculate_fertilizer_advice(
    farm: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates soil NPK parameters against crop demands and provides
    conservative agronomic decision support.
    """
    crop_name, agronomy = _match_crop(farm.get("crop", ""))
    soil = farm.get("soil") or {}
    n = float(soil.get("n", 45))
    p = float(soil.get("p", 30))
    k = float(soil.get("k", 25))

    ideal_n = agronomy["ideal_n"]
    ideal_p = agronomy["ideal_p"]
    ideal_k = agronomy["ideal_k"]

    def _eval(val, ideal):
        if val < ideal - 12:
            return "LOW"
        elif val > ideal + 15:
            return "HIGH"
        return "ADEQUATE"

    n_status = _eval(n, ideal_n)
    p_status = _eval(p, ideal_p)
    k_status = _eval(k, ideal_k)

    recommendations = []
    if n_status == "LOW":
        recommendations.append("Nitrogen Deficiency: Apply urea or well-composted farmyard manure in 2-3 split applications to encourage vegetative vigor.")
    elif n_status == "HIGH":
        recommendations.append("Nitrogen Excess: Withhold nitrogenous fertilizers to avoid vegetative overgrown and weakened resistance to fungal diseases.")

    if p_status == "LOW":
        recommendations.append("Phosphorus Deficiency: Incorporate DAP (Diammonium Phosphate) or Rock Phosphate at root depth to stimulate root development and early flowering.")
    elif p_status == "HIGH":
        recommendations.append("Phosphorus Adequate/High: No additional phosphate needed this season.")

    if k_status == "LOW":
        recommendations.append("Potassium Deficiency: Apply Muriate of Potash (MOP) or wood ash to bolster stalk strength, water regulation, and disease immunity.")
    elif k_status == "HIGH":
        recommendations.append("Potassium Adequate/High: Sufficient potassium available for fruit and tuber quality.")

    if not recommendations:
        recommendations.append("Balanced Nutrition: Current NPK parameters are well-aligned with crop requirements. Maintain organic mulching.")

    return {
        "crop": crop_name,
        "n_status": n_status, "n_value": int(n), "ideal_n": ideal_n,
        "p_status": p_status, "p_value": int(p), "ideal_p": ideal_p,
        "k_status": k_status, "k_value": int(k), "ideal_k": ideal_k,
        "recommendations": recommendations,
        "disclaimer": "Guidance provided as agricultural decision support. Always confirm with accredited local soil testing laboratories before large-scale fertilizer purchases."
    }

# =========================================================================
# 5. PROFIT SIMULATOR ENGINE
# =========================================================================
def simulate_crop_profit(
    farm_size: float,
    crop_name: str,
    yield_per_acre: Optional[float] = None,
    market_price_per_unit: Optional[float] = None,
    seed_cost: Optional[float] = None,
    fertilizer_cost: Optional[float] = None,
    labor_cost: Optional[float] = None,
    irrigation_cost: Optional[float] = None,
    other_cost: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calculates detailed farm financial projections and generates multi-crop comparisons.
    """
    crop, agronomy = _match_crop(crop_name)
    size = max(0.1, float(farm_size or 1.0))

    # Fallback to realistic agronomical baselines if user did not provide custom overrides
    # Yield is in Tons per acre; 1 Ton = 1,000 kg
    est_yield_tons = float(yield_per_acre) if yield_per_acre is not None else agronomy["base_yield_tons"]
    est_price_per_kg = float(market_price_per_unit) if market_price_per_unit is not None else agronomy["base_price_kg"]

    est_seed = float(seed_cost) if seed_cost is not None else (agronomy["base_seed_cost"] * size)
    est_fert = float(fertilizer_cost) if fertilizer_cost is not None else (agronomy["base_fert_cost"] * size)
    est_labor = float(labor_cost) if labor_cost is not None else (agronomy["base_labor_cost"] * size)
    est_irrig = float(irrigation_cost) if irrigation_cost is not None else (3000.0 * size)
    est_other = float(other_cost) if other_cost is not None else (2000.0 * size)

    total_yield_kg = est_yield_tons * 1000.0 * size
    total_revenue = total_yield_kg * est_price_per_kg
    total_costs = est_seed + est_fert + est_labor + est_irrig + est_other
    net_profit = total_revenue - total_costs

    rev_per_acre = round(total_revenue / size)
    cost_per_acre = round(total_costs / size)
    profit_per_acre = round(net_profit / size)
    profit_margin = round((net_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0.0

    # Break-even calculations
    break_even_yield_tons = round((total_costs / est_price_per_kg) / (1000.0 * size), 2) if est_price_per_kg > 0 else 0.0
    break_even_price_kg = round(total_costs / total_yield_kg, 1) if total_yield_kg > 0 else 0.0

    # Multi-crop comparisons using standard baselines
    comparisons = []
    benchmark_crops = ["Maize", "Tomato", "Potato", "Beans"]
    for b_crop in benchmark_crops:
        b_data = CROP_AGRONOMY[b_crop]
        b_rev = (b_data["base_yield_tons"] * 1000.0 * size) * b_data["base_price_kg"]
        b_cost = (b_data["base_seed_cost"] + b_data["base_fert_cost"] + b_data["base_labor_cost"] + 4000) * size
        b_profit = b_rev - b_cost
        comparisons.append({
            "crop": b_crop,
            "revenue": round(b_rev),
            "costs": round(b_cost),
            "profit": round(b_profit),
            "profit_per_acre": round(b_profit / size),
            "roi_pct": round((b_profit / b_cost) * 100, 1) if b_cost > 0 else 0
        })

    return {
        "crop": crop,
        "farm_size_acres": size,
        "total_revenue": round(total_revenue),
        "total_costs": round(total_costs),
        "net_profit": round(net_profit),
        "revenue_per_acre": rev_per_acre,
        "cost_per_acre": cost_per_acre,
        "profit_per_acre": profit_per_acre,
        "profit_margin_pct": profit_margin,
        "break_even_yield_tons_per_acre": break_even_yield_tons,
        "break_even_price_per_kg": break_even_price_kg,
        "cost_breakdown": {
            "seeds": round(est_seed),
            "fertilizer": round(est_fert),
            "labor": round(est_labor),
            "irrigation": round(est_irrig),
            "other": round(est_other)
        },
        "comparisons": comparisons,
        "disclaimer": "Projections are modeled estimates using regional market price averages and standard yields. Actual yields and prices fluctuate with local weather and market dynamics."
    }
