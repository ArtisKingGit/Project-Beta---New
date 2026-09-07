/**
 * AgroFast Client-Side Intelligence & Offline Resilience Module
 * 
 * Provides transparent agronomic decision support, proactive alert generation,
 * local storage caching, and offline state handling.
 */

(function (root, factory) {
    if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.AgroIntelligence = factory();
    }
}(typeof self !== 'undefined' ? self : this, function () {

    const CROP_AGRONOMY = {
        "Maize": {
            idealTemp: 24, tempRange: [18, 32], idealHum: 60, humRange: [50, 75],
            waterNeedsMm: 35, idealN: 60, idealP: 45, idealK: 40,
            baseYieldTons: 2.5, basePriceKg: 45, baseSeedCost: 4500, baseFertCost: 8000, baseLaborCost: 10000
        },
        "Tomato": {
            idealTemp: 23, tempRange: [18, 28], idealHum: 60, humRange: [50, 70],
            waterNeedsMm: 45, idealN: 50, idealP: 65, idealK: 70,
            baseYieldTons: 12.0, basePriceKg: 75, baseSeedCost: 9000, baseFertCost: 15000, baseLaborCost: 22000
        },
        "Potato": {
            idealTemp: 18, tempRange: [14, 24], idealHum: 65, humRange: [55, 80],
            waterNeedsMm: 35, idealN: 50, idealP: 50, idealK: 75,
            baseYieldTons: 9.0, basePriceKg: 40, baseSeedCost: 12000, baseFertCost: 14000, baseLaborCost: 16000
        },
        "Beans": {
            idealTemp: 21, tempRange: [16, 27], idealHum: 65, humRange: [55, 75],
            waterNeedsMm: 25, idealN: 30, idealP: 50, idealK: 45,
            baseYieldTons: 1.2, basePriceKg: 110, baseSeedCost: 4000, baseFertCost: 5000, baseLaborCost: 8000
        },
        "Coffee": {
            idealTemp: 22, tempRange: [15, 26], idealHum: 75, humRange: [60, 85],
            waterNeedsMm: 30, idealN: 65, idealP: 35, idealK: 65,
            baseYieldTons: 2.0, basePriceKg: 180, baseSeedCost: 8000, baseFertCost: 18000, baseLaborCost: 25000
        },
        "Rice": {
            idealTemp: 28, tempRange: [22, 34], idealHum: 80, humRange: [70, 90],
            waterNeedsMm: 60, idealN: 70, idealP: 50, idealK: 45,
            baseYieldTons: 3.0, basePriceKg: 90, baseSeedCost: 5000, baseFertCost: 11000, baseLaborCost: 14000
        },
        "Wheat": {
            idealTemp: 18, tempRange: [12, 25], idealHum: 55, humRange: [45, 70],
            waterNeedsMm: 28, idealN: 65, idealP: 45, idealK: 40,
            baseYieldTons: 2.2, basePriceKg: 55, baseSeedCost: 4500, baseFertCost: 9000, baseLaborCost: 7500
        }
    };

    function matchCrop(cropName) {
        if (typeof cropName === 'object' && cropName !== null) {
            cropName = cropName.crop || cropName.name || "";
        }
        const name = (typeof cropName === 'string' ? cropName : "").trim().toLowerCase();
        for (const [k, v] of Object.entries(CROP_AGRONOMY)) {
            if (k.toLowerCase().includes(name) || name.includes(k.toLowerCase())) {
                return { name: k, data: v };
            }
        }
        return { name: "Maize", data: CROP_AGRONOMY["Maize"] };
    }

    return {
        // -------------------------------------------------------------
        // 1. Farm Health Score Engine (0-100)
        // -------------------------------------------------------------
        calculateFarmHealthScore: function (farm, recentScans, weather, expenses, tasks) {
            const f = farm || {};
            const { name: cropName, data: agronomy } = matchCrop(f.crop);
            const farmId = String(f.id || "");
            const positives = [];
            const warnings = [];
            const breakdown = {};

            // 1. Diagnostics (30 pts)
            let scanScore = 25;
            const scans = recentScans || [];
            const matchingScans = scans.filter(s => {
                const sFarm = String(s.farmId || "");
                const sCrop = (s.crop || "").toLowerCase();
                return (farmId && sFarm === farmId) || (sCrop && sCrop.includes(cropName.toLowerCase()));
            });

            if (matchingScans.length > 0) {
                const recent = matchingScans.slice(-5);
                const healthyCount = recent.filter(s => (s.disease || "").toLowerCase().includes("healthy")).length;
                const ratio = healthyCount / recent.length;
                scanScore = Math.round(ratio * 30);
                if (ratio >= 0.8) {
                    positives.push(`Strong crop health: ${Math.round(ratio * 100)}% of recent scans are healthy.`);
                } else if (ratio <= 0.4) {
                    warnings.push(`Disease outbreak risk: ${Math.round((1 - ratio) * 100)}% of scans flagged disease symptoms.`);
                } else {
                    positives.push(`Moderate crop health: ${Math.round(ratio * 100)}% healthy scans.`);
                }
            } else {
                positives.push("No active plant diseases recorded in diagnostic logs.");
            }
            breakdown.scanHealth = { score: scanScore, max: 30 };

            // 2. NPK Nutrient Balance (20 pts)
            const soil = f.soil || {};
            const n = parseFloat(soil.n !== undefined ? soil.n : 45);
            const p = parseFloat(soil.p !== undefined ? soil.p : 30);
            const k = parseFloat(soil.k !== undefined ? soil.k : 25);

            const nDev = Math.abs(n - agronomy.idealN) / 100.0;
            const pDev = Math.abs(p - agronomy.idealP) / 100.0;
            const kDev = Math.abs(k - agronomy.idealK) / 100.0;
            const avgDev = (nDev + pDev + kDev) / 3.0;

            let npkScore = Math.max(0, Math.min(20, Math.round(20 * (1.0 - (avgDev * 1.3)))));
            if (n < agronomy.idealN - 15) {
                warnings.push(`Nitrogen (${Math.round(n)}%) is below optimal (${agronomy.idealN}%) for ${cropName}.`);
            } else if (n >= agronomy.idealN - 10) {
                positives.push(`Optimal nitrogen levels for vegetative leaf growth.`);
            }
            if (p < agronomy.idealP - 15) {
                warnings.push(`Phosphorus (${Math.round(p)}%) is low for root and bloom development.`);
            }
            if (k < agronomy.idealK - 15) {
                warnings.push(`Potassium (${Math.round(k)}%) is low, weakening stalk and disease resistance.`);
            }
            breakdown.nutrientBalance = { score: npkScore, max: 20 };

            // 3. Irrigation & Water (15 pts)
            const irrigation = (f.irrigation || "").toLowerCase();
            let irrigScore = 12;
            if (irrigation.includes("drip")) {
                irrigScore = 15;
                positives.push("Drip irrigation provides maximum water efficiency and prevents leaf wetting.");
            } else if (irrigation.includes("sprinkler")) {
                irrigScore = 13;
                positives.push("Sprinkler system active.");
            } else if (irrigation.includes("rain")) {
                irrigScore = 10;
                warnings.push("Rainfed plot is susceptible to seasonal dry spells.");
            }
            breakdown.irrigationManagement = { score: irrigScore, max: 15 };

            // 4. Weather Stress (15 pts)
            let weatherScore = 13;
            if (weather && weather.temp !== undefined) {
                const temp = parseFloat(weather.temp);
                const hum = parseFloat(weather.humidity || 60);
                let tempPenalty = 0;
                if (temp < agronomy.tempRange[0] || temp > agronomy.tempRange[1]) {
                    tempPenalty = Math.min(5, Math.abs(temp - agronomy.idealTemp) * 0.7);
                    warnings.push(`Ambient temperature (${Math.round(temp)}°C) is outside the ideal ${agronomy.tempRange[0]}-${agronomy.tempRange[1]}°C range.`);
                } else {
                    positives.push(`Current temperature (${Math.round(temp)}°C) supports active growth.`);
                }
                let humPenalty = 0;
                if (hum > 80) {
                    humPenalty = 3;
                    warnings.push(`High relative humidity (${Math.round(hum)}%) creates elevated fungal spore risk.`);
                } else if (hum < 35) {
                    humPenalty = 2;
                    warnings.push(`Low humidity (${Math.round(hum)}%) creates moisture stress.`);
                } else {
                    positives.push(`Humidity (${Math.round(hum)}%) is in safe range.`);
                }
                weatherScore = Math.max(4, Math.round(15 - tempPenalty - humPenalty));
            } else {
                positives.push("Seasonal weather conditions within expected parameters.");
            }
            breakdown.weatherAdaptation = { score: weatherScore, max: 15 };

            // 5. Budget Health (10 pts)
            const budget = parseFloat(f.budget || 0);
            let spent = 0;
            for (const exp of (expenses || [])) {
                if (!farmId || String(exp.farmId || "") === farmId) {
                    spent += parseFloat(exp.amount || 0);
                }
            }
            let budgetScore = 9;
            if (budget > 0) {
                const spentRatio = spent / budget;
                if (spentRatio > 1.0) {
                    budgetScore = 4;
                    warnings.push(`Spending has exceeded budget (${Math.round(spentRatio * 100)}% utilized).`);
                } else if (spentRatio >= 0.85) {
                    budgetScore = 7;
                    warnings.push(`Budget utilization is high (${Math.round(spentRatio * 100)}%).`);
                } else {
                    budgetScore = 10;
                    positives.push(`Expenses are well within budget (${Math.round(spentRatio * 100)}% utilized).`);
                }
            } else {
                positives.push("Operational budget is balanced.");
            }
            breakdown.budgetHealth = { score: budgetScore, max: 10 };

            // 6. Farm Activity (10 pts)
            let taskScore = 8;
            if (tasks && tasks.length > 0) {
                const farmTasks = tasks.filter(t => !farmId || String(t.farmId || "") === farmId || !t.farmId);
                if (farmTasks.length > 0) {
                    const completed = farmTasks.filter(t => t.completed).length;
                    const tRatio = completed / farmTasks.length;
                    taskScore = Math.max(3, Math.round(tRatio * 10));
                    if (tRatio >= 0.7) {
                        positives.push(`Strong activity: ${completed}/${farmTasks.length} farm tasks completed.`);
                    } else {
                        warnings.push(`${farmTasks.length - completed} scheduled tasks awaiting completion.`);
                    }
                }
            }
            breakdown.farmActivity = { score: taskScore, max: 10 };

            const totalScore = Math.max(10, Math.min(100, Math.round(
                scanScore + npkScore + irrigScore + weatherScore + budgetScore + taskScore
            )));

            let rating = "Fair";
            if (totalScore >= 85) rating = "Excellent";
            else if (totalScore >= 70) rating = "Good";
            else if (totalScore < 50) rating = "Needs Attention";

            return {
                score: totalScore,
                rating: rating,
                crop: cropName,
                positives: positives.slice(0, 4),
                warnings: warnings.slice(0, 4),
                breakdown: breakdown
            };
        },

        // -------------------------------------------------------------
        // 2. Disease Risk Prediction Engine
        // -------------------------------------------------------------
        calculateDiseaseRisk: function (cropName, weather, recentScans, farmId) {
            const { name: crop } = matchCrop(cropName);
            const w = weather || {};
            const temp = parseFloat(w.temp !== undefined ? w.temp : 24);
            const humidity = parseFloat(w.humidity !== undefined ? w.humidity : 65);
            const precip = parseFloat(w.precipitation || 0);
            const rainProb = parseFloat(w.rain_probability || 0);

            let riskPoints = 15;
            const reasons = [];

            if (humidity >= 85) {
                riskPoints += 32;
                reasons.push(`Critically high humidity (${Math.round(humidity)}%) creates prolonged leaf wetness favoring fungal spores.`);
            } else if (humidity >= 75) {
                riskPoints += 22;
                reasons.push(`Elevated humidity (${Math.round(humidity)}%) supports rapid spore germination.`);
            } else if (humidity <= 45) {
                riskPoints -= 8;
                reasons.push(`Dry ambient air (${Math.round(humidity)}% humidity) restricts fungal spore propagation.`);
            }

            if (temp >= 20 && temp <= 27) {
                riskPoints += 18;
                reasons.push(`Warm temperature (${Math.round(temp)}°C) accelerates pathogen replication.`);
            } else if (temp > 32 || temp < 14) {
                riskPoints -= 5;
                reasons.push(`Temperature (${Math.round(temp)}°C) suppresses common foliar pathogens.`);
            }

            if (precip > 5.0 || rainProb >= 70) {
                riskPoints += 20;
                reasons.push("Expected rainfall causes soil splashing and extended leaf surface moisture.");
            } else if (precip > 0.5 || rainProb >= 40) {
                riskPoints += 10;
                reasons.push("Moderate rain probability maintains moist canopy.");
            }

            if (recentScans && recentScans.length > 0) {
                const diseasedCount = recentScans.slice(-6).filter(s => {
                    const d = (s.disease || "").toLowerCase();
                    return d && !d.includes("healthy") && !d.includes("soil");
                }).length;
                if (diseasedCount >= 2) {
                    riskPoints += 18;
                    reasons.push(`Active disease detected in ${diseasedCount} recent scans on this farm.`);
                } else if (diseasedCount === 1) {
                    riskPoints += 8;
                    reasons.push("Prior disease detected in recent scan.");
                }
            }

            const riskScore = Math.max(5, Math.min(95, riskPoints));
            let level = "LOW";
            let alertTriggered = false;
            let recommendation = "Standard monitoring is sufficient.";

            if (riskScore >= 80) {
                level = "CRITICAL";
                alertTriggered = true;
                recommendation = "Inspect crops within 24 hours. Apply preventative organic or systemic protection if rain is imminent.";
            } else if (riskScore >= 65) {
                level = "HIGH";
                alertTriggered = true;
                recommendation = "High disease pressure. Avoid overhead irrigation and monitor lower leaves for lesions.";
            } else if (riskScore >= 40) {
                level = "MODERATE";
                recommendation = "Moderate environmental risk. Scout fields twice weekly.";
            }

            return {
                riskScore: riskScore,
                risk_score: riskScore,
                riskLevel: level,
                risk_level: level,
                crop: crop,
                reasons: reasons,
                recommendation: recommendation,
                alertTriggered: alertTriggered,
                disclaimer: "This is an environmental risk estimate based on atmospheric and historical data, not a guarantee of disease occurrence."
            };
        },

        // -------------------------------------------------------------
        // 3. Smart Irrigation Advisor Engine
        // -------------------------------------------------------------
        calculateIrrigationAdvice: function (farm, weather, forecastRainMm) {
            const f = farm || {};
            const { data: agronomy } = matchCrop(f.crop);
            const size = parseFloat(f.size || 1.0) || 1.0;
            const soilType = (f.soilType || "Loam").toLowerCase();
            const w = weather || {};
            const precip = parseFloat(w.precipitation || 0);
            const rainProb = parseFloat(w.rain_probability || 0);
            const temp = parseFloat(w.temp !== undefined ? w.temp : 24);
            const humidity = parseFloat(w.humidity !== undefined ? w.humidity : 60);
            const rainForecast = parseFloat(forecastRainMm || 0);

            const baseDailyMm = agronomy.waterNeedsMm / 7.0;
            let etMult = 1.0 + ((temp - 20.0) * 0.03) - ((humidity - 60.0) * 0.01);
            etMult = Math.max(0.6, Math.min(1.6, etMult));

            let retention = 1.0;
            if (soilType.includes("clay") || soilType.includes("black")) retention = 1.3;
            else if (soilType.includes("sandy") || soilType.includes("arid")) retention = 0.7;

            const effectiveDailyMm = (baseDailyMm * etMult) / retention;
            const litersPerAcre = Math.round(effectiveDailyMm * 4046.86);
            const totalLiters = Math.round(litersPerAcre * size);

            let action = "Standard scheduled irrigation";
            let reason = `Mild conditions (${Math.round(temp)}°C, ${Math.round(humidity)}% humidity). Maintain steady root moisture.`;
            let window = "Morning (06:30 - 09:00)";
            let litersNeeded = totalLiters;

            if (rainForecast >= 5.0 || (precip >= 3.0 && rainProb >= 65)) {
                action = "Do not irrigate today";
                reason = `Significant rainfall (${rainForecast || precip} mm) is expected. Conserve water and prevent waterlogging.`;
                window = "Delay irrigation until rain passes and soil moisture is verified";
                litersNeeded = 0;
            } else if (rainForecast >= 2.0 || rainProb >= 50) {
                action = "Reduce irrigation volume by 50%";
                reason = `Moderate rain probability (${Math.round(rainProb)}%). Light watering is sufficient.`;
                window = "Early morning (06:00 - 08:00)";
                litersNeeded = Math.round(totalLiters * 0.5);
            } else if (temp >= 30) {
                action = "Irrigate thoroughly";
                reason = `High temperature (${Math.round(temp)}°C) increases evapotranspiration. Early watering prevents wilt.`;
                window = "Early morning (06:00 - 08:30) or Evening (17:30 - 19:00)";
                litersNeeded = totalLiters;
            }

            return {
                action: action,
                recommendation: action,
                reason: reason,
                irrigationWindow: window,
                recommended_window: window,
                estimatedWaterLiters: litersNeeded,
                litersPerAcre: Math.round(litersNeeded / size),
                expectedRainMm: Math.round(rainForecast * 10) / 10,
                rainfall_expected: rainForecast ? `${Math.round(rainForecast * 10) / 10} mm` : (precip ? `${precip} mm` : '0 mm'),
                soilType: f.soilType || "Loam",
                irrigationType: f.irrigation || "Drip"
            };
        },

        // -------------------------------------------------------------
        // 4. Smart NPK / Fertilizer Advisor
        // -------------------------------------------------------------
        calculateFertilizerAdvice: function (farm) {
            const f = farm || {};
            const { name: cropName, data: agronomy } = matchCrop(f.crop);
            const soil = f.soil || {};
            const n = parseFloat(soil.n !== undefined ? soil.n : 45);
            const p = parseFloat(soil.p !== undefined ? soil.p : 30);
            const k = parseFloat(soil.k !== undefined ? soil.k : 25);

            function evalNutrient(val, ideal) {
                if (val < ideal - 12) return "LOW";
                if (val > ideal + 15) return "HIGH";
                return "ADEQUATE";
            }

            const nStatus = evalNutrient(n, agronomy.idealN);
            const pStatus = evalNutrient(p, agronomy.idealP);
            const kStatus = evalNutrient(k, agronomy.idealK);

            const recommendations = [];
            if (nStatus === "LOW") {
                recommendations.push("Nitrogen Deficiency: Apply urea or well-composted farmyard manure in 2-3 split applications to encourage vegetative vigor.");
            } else if (nStatus === "HIGH") {
                recommendations.push("Nitrogen Excess: Withhold nitrogenous fertilizers to prevent excessive foliage and increased disease vulnerability.");
            }

            if (pStatus === "LOW") {
                recommendations.push("Phosphorus Deficiency: Incorporate DAP (Diammonium Phosphate) or rock phosphate at root zone depth to stimulate root development and flowering.");
            }

            if (kStatus === "LOW") {
                recommendations.push("Potassium Deficiency: Apply Muriate of Potash (MOP) or wood ash to bolster stalk strength, water regulation, and disease resistance.");
            }

            if (recommendations.length === 0) {
                recommendations.push("Balanced Nutrition: Current soil NPK parameters align with crop needs. Maintain organic mulching.");
            }

            return {
                crop: cropName,
                nStatus, nValue: Math.round(n), idealN: agronomy.idealN,
                pStatus, pValue: Math.round(p), idealP: agronomy.idealP,
                kStatus, kValue: Math.round(k), idealK: agronomy.idealK,
                nitrogen_status: nStatus,
                phosphorus_status: pStatus,
                potassium_status: kStatus,
                recommendations,
                disclaimer: "Guidance provided as decision support. Confirm with local soil testing laboratories before high-rate application."
            };
        },

        // -------------------------------------------------------------
        // 5. Profitability Simulator
        // -------------------------------------------------------------
        simulateProfit: function (farmSize, cropName, customParams) {
            const { name: crop, data: agronomy } = matchCrop(cropName);
            const size = Math.max(0.1, parseFloat(farmSize) || 1.0);
            const p = customParams || {};

            const yieldTons = p.yieldPerAcre !== undefined && p.yieldPerAcre !== "" ? parseFloat(p.yieldPerAcre) : agronomy.baseYieldTons;
            const priceKg = p.marketPrice !== undefined && p.marketPrice !== "" ? parseFloat(p.marketPrice) : agronomy.basePriceKg;

            const seedCost = p.seedCost !== undefined && p.seedCost !== "" ? parseFloat(p.seedCost) : (agronomy.baseSeedCost * size);
            const fertCost = p.fertCost !== undefined && p.fertCost !== "" ? parseFloat(p.fertCost) : (agronomy.baseFertCost * size);
            const laborCost = p.laborCost !== undefined && p.laborCost !== "" ? parseFloat(p.laborCost) : (agronomy.baseLaborCost * size);
            const irrigCost = p.irrigCost !== undefined && p.irrigCost !== "" ? parseFloat(p.irrigCost) : (3000 * size);
            const otherCost = p.otherCost !== undefined && p.otherCost !== "" ? parseFloat(p.otherCost) : (2000 * size);

            const totalYieldKg = yieldTons * 1000.0 * size;
            const totalRevenue = totalYieldKg * priceKg;
            const totalCosts = seedCost + fertCost + laborCost + irrigCost + otherCost;
            const netProfit = totalRevenue - totalCosts;

            const revPerAcre = Math.round(totalRevenue / size);
            const costPerAcre = Math.round(totalCosts / size);
            const profitPerAcre = Math.round(netProfit / size);
            const profitMargin = totalRevenue > 0 ? Math.round((netProfit / totalRevenue) * 1000) / 10 : 0;

            const breakEvenYield = priceKg > 0 ? Math.round((totalCosts / priceKg) / (1000.0 * size) * 100) / 100 : 0;
            const breakEvenPrice = totalYieldKg > 0 ? Math.round((totalCosts / totalYieldKg) * 10) / 10 : 0;

            const comparisons = [];
            const benchmarks = ["Maize", "Tomato", "Potato", "Beans"];
            for (const b of benchmarks) {
                const bData = CROP_AGRONOMY[b];
                const bRev = (bData.baseYieldTons * 1000.0 * size) * bData.basePriceKg;
                const bCost = (bData.baseSeedCost + bData.baseFertCost + bData.baseLaborCost + 4000) * size;
                const bProfit = bRev - bCost;
                comparisons.push({
                    crop: b,
                    revenue: Math.round(bRev),
                    costs: Math.round(bCost),
                    profit: Math.round(bProfit),
                    profitPerAcre: Math.round(bProfit / size),
                    roiPct: bCost > 0 ? Math.round((bProfit / bCost) * 100) : 0
                });
            }

            return {
                crop,
                farmSizeAcres: size,
                totalRevenue: Math.round(totalRevenue),
                totalCosts: Math.round(totalCosts),
                netProfit: Math.round(netProfit),
                revenuePerAcre: revPerAcre,
                costPerAcre: costPerAcre,
                profitPerAcre: profitPerAcre,
                profitMarginPct: profitMargin,
                breakEvenYieldTons: breakEvenYield,
                breakEvenPriceKg: breakEvenPrice,
                costBreakdown: {
                    seeds: Math.round(seedCost),
                    fertilizer: Math.round(fertCost),
                    labor: Math.round(laborCost),
                    irrigation: Math.round(irrigCost),
                    other: Math.round(otherCost)
                },
                comparisons: comparisons
            };
        },

        // -------------------------------------------------------------
        // 6. Proactive Alert Generation
        // -------------------------------------------------------------
        generateProactiveAlerts: function (farms, weather, scans, expenses, tasks) {
            const alerts = [];
            const farmList = farms ? Object.entries(farms).map(([id, f]) => ({ id, ...f })) : [];
            const now = new Date();

            // 1. Weather Alerts
            if (weather) {
                const precip = parseFloat(weather.precipitation || 0);
                const rainProb = parseFloat(weather.rain_probability || 0);
                const temp = parseFloat(weather.temp || 24);

                if (precip >= 15.0 || rainProb >= 85) {
                    alerts.push({
                        id: `weather_heavy_rain_${now.toDateString()}`,
                        type: "weather",
                        severity: "warning",
                        title: "Heavy Rainfall Expected",
                        message: `High precipitation expected today (${precip}mm, ${rainProb}% probability). Delay irrigation and ensure furrow drainage.`,
                        timestamp: now.toISOString(),
                        action: "Delay irrigation"
                    });
                } else if (temp >= 33) {
                    alerts.push({
                        id: `weather_heatwave_${now.toDateString()}`,
                        type: "weather",
                        severity: "warning",
                        title: "Extreme Heat Advisory",
                        message: `Temperature reaching ${Math.round(temp)}°C. Irrigate early in the morning and apply organic mulch to protect roots.`,
                        timestamp: now.toISOString(),
                        action: "Early morning irrigation"
                    });
                }
            }

            // 2. Farm-Specific Alerts (Disease Risk, Budget, NPK)
            farmList.forEach(farm => {
                const risk = this.calculateDiseaseRisk(farm.crop, weather, scans, farm.id);
                if (risk.alertTriggered) {
                    alerts.push({
                        id: `risk_${farm.id}_${now.toDateString()}`,
                        type: "disease",
                        severity: risk.riskLevel === "CRITICAL" ? "danger" : "warning",
                        title: `${risk.riskLevel} Disease Pressure on ${farm.name}`,
                        message: `Environmental conditions favor fungal sporulation on ${farm.crop || 'crops'}. ${risk.recommendation}`,
                        relatedFarm: farm.name,
                        farmId: farm.id,
                        timestamp: now.toISOString(),
                        action: "Inspect crop leaves"
                    });
                }

                // Budget Alert
                const budget = parseFloat(farm.budget || 0);
                if (budget > 0 && expenses) {
                    const farmExpenses = expenses.filter(e => String(e.farmId || "") === farm.id);
                    const spent = farmExpenses.reduce((sum, e) => sum + parseFloat(e.amount || 0), 0);
                    const ratio = spent / budget;
                    if (ratio >= 0.85) {
                        alerts.push({
                            id: `budget_${farm.id}`,
                            type: "budget",
                            severity: ratio > 1.0 ? "danger" : "warning",
                            title: `Budget Notice: ${farm.name}`,
                            message: ratio > 1.0 
                                ? `Spending on ${farm.name} has exceeded budget by ${Math.round((ratio - 1) * 100)}%.`
                                : `Farm spending on ${farm.name} has reached ${Math.round(ratio * 100)}% of total allocated budget.`,
                            relatedFarm: farm.name,
                            farmId: farm.id,
                            timestamp: now.toISOString(),
                            action: "Review expenses"
                        });
                    }
                }

                // NPK Alert
                const fert = this.calculateFertilizerAdvice(farm);
                if (fert.nStatus === "LOW" || fert.pStatus === "LOW" || fert.kStatus === "LOW") {
                    const deficient = [];
                    if (fert.nStatus === "LOW") deficient.push("Nitrogen");
                    if (fert.pStatus === "LOW") deficient.push("Phosphorus");
                    if (fert.kStatus === "LOW") deficient.push("Potassium");
                    alerts.push({
                        id: `npk_${farm.id}`,
                        type: "npk",
                        severity: "info",
                        title: `Low ${deficient.join('/')} in ${farm.name}`,
                        message: `Soil levels are below optimal for ${farm.crop || 'crops'}. Consider top-dressing with balanced amendments.`,
                        relatedFarm: farm.name,
                        farmId: farm.id,
                        timestamp: now.toISOString(),
                        action: "View NPK recommendation"
                    });
                }
            });

            // 3. Task Alerts
            if (tasks) {
                const pendingTasks = tasks.filter(t => !t.completed);
                if (pendingTasks.length > 0) {
                    const highPri = pendingTasks.find(t => t.priority === "High");
                    if (highPri) {
                        alerts.push({
                            id: `task_urgent_${highPri.id || '1'}`,
                            type: "task",
                            severity: "info",
                            title: `Priority Task: ${highPri.title}`,
                            message: `Scheduled task awaiting action: ${highPri.title} (Due: ${highPri.date || 'Today'}).`,
                            timestamp: now.toISOString(),
                            action: "Open farming calendar"
                        });
                    }
                }
            }

            return alerts;
        },

        // -------------------------------------------------------------
        // 7. CSV Export Utility
        // -------------------------------------------------------------
        exportToCSV: function (filename, rows, headers) {
            if (!rows || !rows.length) {
                alert("No records to export.");
                return;
            }
            const processRow = function (row) {
                let finalVal = '';
                for (let j = 0; j < row.length; j++) {
                    let innerValue = row[j] === null || row[j] === undefined ? '' : row[j].toString();
                    if (row[j] instanceof Date) {
                        innerValue = row[j].toLocaleString();
                    }
                    let result = innerValue.replace(/"/g, '""');
                    if (result.search(/("|,|\n)/g) >= 0)
                        result = '"' + result + '"';
                    if (j > 0)
                        finalVal += ',';
                    finalVal += result;
                }
                return finalVal + '\n';
            };

            let csvFile = '';
            if (headers) {
                csvFile += processRow(headers);
            }
            for (let i = 0; i < rows.length; i++) {
                csvFile += processRow(rows[i]);
            }

            const blob = new Blob([csvFile], { type: 'text/csv;charset=utf-8;' });
            if (navigator.msSaveBlob) {
                navigator.msSaveBlob(blob, filename);
            } else {
                const link = document.createElement("a");
                if (link.download !== undefined) {
                    const url = URL.createObjectURL(blob);
                    link.setAttribute("href", url);
                    link.setAttribute("download", filename);
                    link.style.visibility = 'hidden';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            }
        },

        // -------------------------------------------------------------
        // 7. Crop Health Timeline Engine
        // -------------------------------------------------------------
        generateCropTimeline: function (scans, selectedFarmId, selectedCrop) {
            let filtered = Array.isArray(scans) ? [...scans] : [];
            if (selectedFarmId && selectedFarmId !== 'all') {
                filtered = filtered.filter(s => s.farmId === selectedFarmId);
            }
            if (selectedCrop && selectedCrop !== 'all') {
                filtered = filtered.filter(s => (s.crop || '').toLowerCase().includes(selectedCrop.toLowerCase()));
            }

            // Sort chronologically ascending for timeline flow
            filtered.sort((a, b) => new Date(a.time || 0) - new Date(b.time || 0));

            let previousStatus = null;
            const timeline = filtered.map((scan, idx) => {
                const dateObj = new Date(scan.time || Date.now());
                const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' });
                const disease = scan.disease || 'Healthy';
                const isHealthy = disease.toLowerCase().includes('healthy') || disease.toLowerCase().includes('no issue');
                const confidence = scan.confidence || '95%';
                const confVal = parseInt(confidence) || 90;

                let healthStatus = 'Healthy';
                let statusBadgeClass = 'status-healthy';
                let icon = 'fa-check-circle';
                let color = '#22c55e';

                if (isHealthy) {
                    healthStatus = 'Healthy';
                    statusBadgeClass = 'status-healthy';
                    icon = 'fa-check-circle';
                    color = '#22c55e';
                } else {
                    if (previousStatus === 'Disease Detected' || previousStatus === 'Infected') {
                        healthStatus = confVal < 80 ? 'Improving' : 'Disease Detected';
                        statusBadgeClass = healthStatus === 'Improving' ? 'status-warning' : 'status-infected';
                        icon = healthStatus === 'Improving' ? 'fa-arrow-trend-up' : 'fa-triangle-exclamation';
                        color = healthStatus === 'Improving' ? '#f59e0b' : '#ef4444';
                    } else {
                        healthStatus = 'Disease Detected';
                        statusBadgeClass = 'status-infected';
                        icon = 'fa-triangle-exclamation';
                        color = '#ef4444';
                    }
                }

                previousStatus = healthStatus;

                return {
                    id: scan.id || `scan-${idx}`,
                    rawDate: scan.time,
                    formattedDate: dateStr,
                    crop: scan.crop || 'Unknown Crop',
                    disease: disease,
                    confidence: confidence,
                    confidenceVal: confVal,
                    severity: scan.severity || (isHealthy ? 'Healthy' : 'Moderate'),
                    healthStatus: healthStatus,
                    statusBadgeClass: statusBadgeClass,
                    icon: icon,
                    color: color,
                    treatment: scan.treatment || 'Maintain standard agronomic care.',
                    why: scan.why_agrofast_thinks_this || '',
                    steps: scan.recommended_steps || [],
                    rescanDays: scan.rescan_days || 7,
                    farmName: scan.farmName || 'General Plot',
                    modelVersion: scan.model_version || 'AgroFast Vision v1.1',
                    boxes: scan.boxes || []
                };
            });

            const total = timeline.length;
            const healthyCount = timeline.filter(t => t.healthStatus === 'Healthy').length;
            const diseaseCount = timeline.filter(t => t.healthStatus === 'Disease Detected').length;
            
            let overallTrend = 'STABLE';
            if (timeline.length >= 2) {
                const latest = timeline[timeline.length - 1];
                const prev = timeline[timeline.length - 2];
                if (latest.healthStatus === 'Healthy' && prev.healthStatus !== 'Healthy') {
                    overallTrend = 'IMPROVING';
                } else if (latest.healthStatus !== 'Healthy' && prev.healthStatus === 'Healthy') {
                    overallTrend = 'NEEDS_ATTENTION';
                }
            }

            return {
                timeline: timeline,
                total_scans: total,
                healthy_count: healthyCount,
                disease_count: diseaseCount,
                overall_trend: overallTrend
            };
        },
        getCachedData: function (key) {
            try {
                const val = localStorage.getItem(`agrofast_cache_${key}`);
                return val ? JSON.parse(val) : null;
            } catch (e) {
                return null;
            }
        },

        setCachedData: function (key, value) {
            try {
                localStorage.setItem(`agrofast_cache_${key}`, JSON.stringify(value));
            } catch (e) {}
        },

        initOfflineDetector: function (onStatusChange) {
            const updateStatus = () => {
                const isOnline = navigator.onLine;
                let banner = document.getElementById('agrofast-offline-banner');
                if (!isOnline) {
                    if (!banner) {
                        banner = document.createElement('div');
                        banner.id = 'agrofast-offline-banner';
                        banner.style.cssText = 'position:fixed;top:0;left:0;right:0;background:#f59e0b;color:#18181b;font-weight:600;font-size:13px;padding:8px 16px;text-align:center;z-index:99999;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 2px 8px rgba(0,0,0,0.2);';
                        banner.innerHTML = '<i class="fas fa-wifi-slash"></i> Offline Mode — displaying last updated data. Actions will sync when connection returns.';
                        document.body.prepend(banner);
                    } else {
                        banner.style.display = 'flex';
                    }
                } else if (banner) {
                    banner.style.display = 'none';
                }
                if (typeof onStatusChange === 'function') {
                    onStatusChange(isOnline);
                }
            };

            window.addEventListener('online', updateStatus);
            window.addEventListener('offline', updateStatus);
            updateStatus();
        }
    };
}));
