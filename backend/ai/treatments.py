# Dynamic treatments and diagnoses mapping for crop diseases and pests.
# Supports the 19 standard classes, 38 PlantVillage classes, and 42 archive (2) classes.

PLANTVILLAGE_TREATMENTS = {
    "Apple___Apple_scab": {
        "crop": "Apple",
        "disease": "Apple Scab (Venturia inaequalis)",
        "treatment": "Prune infected leaves and branches to increase air circulation. Apply copper-based fungicide or neem oil. Plant resistant varieties in future seasons."
    },
    "Apple___Black_rot": {
        "crop": "Apple",
        "disease": "Black Rot (Botryosphaeria obtusa)",
        "treatment": "Prune out dead wood, mummified fruit, and cankers during dormancy. Burn or destroy prunings. Apply labeled fungicide during early leaf development."
    },
    "Apple___Cedar_apple_rust": {
        "crop": "Apple",
        "disease": "Cedar Apple Rust (Gymnosporangium juniperi-virginianae)",
        "treatment": "Remove nearby juniper bushes (the alternate host) if possible. Apply preventative fungicides in early spring when orange rust galls appear on junipers."
    },
    "Apple___healthy": {
        "crop": "Apple",
        "disease": "Healthy",
        "treatment": "No treatment required. Maintain standard irrigation, fertilize appropriately, and monitor for pests."
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "crop": "Corn (Maize)",
        "disease": "Gray Leaf Spot (Cercospora zeae-maydis)",
        "treatment": "Rotate crops to non-hosts like soybeans. Use tillage to degrade crop residue. Apply foliar fungicide if disease severity is high."
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn (Maize)",
        "disease": "Common Rust (Puccinia sorghi)",
        "treatment": "Plant rust-resistant hybrids. Avoid overhead irrigation to reduce leaf wetness. Apply preventative fungicides if spotted early in the season."
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "crop": "Corn (Maize)",
        "disease": "Northern Leaf Blight (Exserohilum turcicum)",
        "treatment": "Manage residue with tillage or crop rotation. Plant resistant hybrids. Apply systemic fungicides at first sign of lesions."
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn (Maize)",
        "disease": "Healthy",
        "treatment": "No treatment required. Maintain regular watering, monitor nitrogen levels, and keep fields clear of weeds."
    },
    "Grape___Black_rot": {
        "crop": "Grape",
        "disease": "Grape Black Rot (Guignardia bidwellii)",
        "treatment": "Remove all mummified fruit and diseased canes during winter pruning. Maintain open canopy for airflow. Apply preventative fungicides."
    },
    "Grape___Esca_(Black_Measles)": {
        "crop": "Grape",
        "disease": "Esca / Black Measles (Fungal Complex)",
        "treatment": "Avoid pruning during rainy periods to limit spore entry. Disinfect pruning tools between cuts. Protect pruning wounds with sealants."
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "crop": "Grape",
        "disease": "Leaf Blight (Pseudocercospora vitis)",
        "treatment": "Collect and destroy fallen leaves. Prune lower foliage to reduce humidity. Apply fungicides starting from bud break."
    },
    "Grape___healthy": {
        "crop": "Grape",
        "disease": "Healthy",
        "treatment": "No treatment required. Keep vines pruned, ensure good soil drainage, and water at the base of the plant."
    },
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease": "Early Blight (Alternaria solani)",
        "treatment": "Apply potassium fertilizers. Avoid overhead irrigation. Apply copper-based or chemical fungicides when lower leaves show concentric rings."
    },
    "Potato___Late_blight": {
        "crop": "Potato",
        "disease": "Late Blight (Phytophthora infestans)",
        "treatment": "Destroy infected plants immediately (highly contagious). Apply preventative fungicides weekly during humid weather. Plant certified disease-free seeds."
    },
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease": "Bacterial Spot (Xanthomonas perforans)",
        "treatment": "Apply copper-based sprays combined with mancozeb. Avoid working in wet fields to prevent spread. Remove infected crop debris."
    },
    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease": "Late Blight (Phytophthora infestans)",
        "treatment": "Remove and destroy infected plants. Apply chlorothalonil or copper fungicide. Plant resistant varieties and avoid overhead watering."
    },
    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot (Septoria lycopersici)",
        "treatment": "Water at the soil level, not the foliage. Apply mulch to prevent soil splashing onto leaves. Apply organic copper fungicide."
    },
    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease": "Target Spot (Corynespora cassiicola)",
        "treatment": "Prune lower branches to improve airflow. Maintain balanced soil nutrition. Apply preventative chlorothalonil or copper sprays."
    },
    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease": "Tomato Mosaic Virus (ToMV)",
        "treatment": "No chemical cure. Remove and burn infected plants. Wash hands and tools with soap and water after handling. Plant resistant seeds."
    }
}

# Legacy fallback mapping for simple crop names and health status
LEGACY_TREATMENTS = {
    "maize": {
        "Healthy": {
            "disease": "Healthy Maize",
            "treatment": "Continue regular watering and monitoring. Ensure soil nitrogen levels are maintained."
        },
        "Risk": {
            "disease": "Potential Leaf Blight or Rust",
            "treatment": "Apply fungicide immediately. Remove infected leaves to prevent spread. Ensure proper spacing for air circulation."
        }
    },
    "tomato": {
        "Healthy": {
            "disease": "Healthy Tomato",
            "treatment": "Support plant with stakes. Water at the base to avoid wet leaves."
        },
        "Risk": {
            "disease": "Potential Blight or Bacterial Spot",
            "treatment": "Copper-based fungicide is recommended. Avoid overhead watering. Rotate crops next season."
        }
    },
    "wheat": {
        "Healthy": {
            "disease": "Healthy Wheat",
            "treatment": "Maintain moisture. Monitor for pests like aphids."
        },
        "Risk": {
            "disease": "Potential Rust or Mildew",
            "treatment": "Apply foliar fungicide. Ensure variety is resistant for future planting. Check for moisture stress."
        }
    },
    "potato": {
        "Healthy": {
            "disease": "Healthy Potato",
            "treatment": "Keep tubers covered with soil. Ensure consistent moisture."
        },
        "Risk": {
            "disease": "Potential Late Blight or Scab",
            "treatment": "Use certified seed tubers. Apply fungicide if blight is suspected. Ensure good drainage."
        }
    },
    "coffee": {
        "Healthy": {
            "disease": "Healthy Coffee",
            "treatment": "Maintain shade and soil mulch. Prune regularly for air flow."
        },
        "Risk": {
            "disease": "Potential Coffee Rust or Berry Disease",
            "treatment": "Apply copper-based fungicides. Remove infected leaves. Ensure proper plant nutrition."
        }
    },
    "rice": {
        "Healthy": {
            "disease": "Healthy Rice",
            "treatment": "Maintain constant water levels in paddies. Monitor nitrogen levels."
        },
        "Risk": {
            "disease": "Potential Blast or Sheath Blight",
            "treatment": "Use blast-resistant varieties. Avoid excessive nitrogen fertilizer. Keep fields clear of weeds."
        }
    }
}

def parse_class_name(class_name):
    """
    Parses complex directory names into clean, readable Crop and Disease names.
    Examples:
      - Tomato___Tomato_mosaic_virus -> Crop: Tomato, Disease: Tomato Mosaic Virus
      - American Bollworm on Cotton -> Crop: Cotton, Disease: American Bollworm
      - Sugarcane Healthy -> Crop: Sugarcane, Disease: Healthy
      - Wheat black rust -> Crop: Wheat, Disease: Black Rust
    """
    # Check if it is a soil type class
    if "soil" in class_name.lower():
        # E.g. "Alluvial_Soil" -> "Alluvial Soil"
        soil_name = class_name.replace("_", " ").strip().title()
        return soil_name, "Soil Scan"

    # Split crop and disease using standard separators
    if "___" in class_name:
        crop, disease = class_name.split("___", 1)
    elif "__" in class_name:
        crop, disease = class_name.split("__", 1)
    else:
        name_lower = class_name.lower()
        known_crops = ["apple", "cassava", "coffee", "maize", "mango", "pepper", "potato", "rice", "tea", "tomato", "wheat", "cotton", "grape", "sugarcane"]
        matched_crop = None
        for kc in known_crops:
            if name_lower.startswith(kc):
                matched_crop = kc
                break
        
        if matched_crop:
            crop = class_name[:len(matched_crop)]
            disease = class_name[len(matched_crop):].lstrip("_")
        else:
            crop = "Unknown"
            disease = class_name

    # Standardize crop name
    crop = crop.replace("_", " ").replace("  ", " ").strip().title()
    if crop.lower() in ["corn", "maize"]:
        crop = "Maize"
    elif "pepper" in crop.lower():
        crop = "Bell Pepper"

    # Standardize disease name
    disease = disease.replace("_", " ").replace("  ", " ").strip()
    
    # Correct common spelling issues
    if "becterial" in disease.lower():
        disease = disease.replace("Becterial", "Bacterial").replace("becterial", "Bacterial")
    if "thirps" in disease.lower():
        disease = disease.replace("Thirps", "Thrips").replace("thirps", "Thrips")
    if "redrot" in disease.lower():
        disease = disease.replace("RedRot", "Red Rot").replace("redrot", "Red Rot")
    if "redrust" in disease.lower():
        disease = disease.replace("RedRust", "Red Rust").replace("redrust", "Red Rust")
    if "brownspot" in disease.lower():
        disease = "Brown Spot"
        
    if not disease or disease.lower() in ["healthy", ""]:
        disease = "Healthy"
    else:
        disease = disease.title()

    # Avoid duplicate crop prefix in disease name
    if disease.startswith(crop) and len(disease) > len(crop):
        disease = disease[len(crop):].strip().lstrip("_").strip().title()

    return crop, disease

def get_dynamic_treatment(crop, disease):
    """Generates agronomic treatment guidelines based on parsed crop and disease/pest terms."""
    if disease == "Healthy":
        return "No treatment required. Maintain standard irrigation, fertilize appropriately, and monitor for pests."
        
    disease_lower = disease.lower()
    crop_lower = crop.lower()

    # Cassava diseases
    if crop_lower == "cassava":
        if "bacterial blight" in disease_lower:
            return "Use disease-free planting materials and resistant varieties. Prune and destroy infected plants. Rotate crops. Apply copper-based fungicides if necessary."
        if "brown streak" in disease_lower:
            return "No chemical treatment available. Uproot and burn infected plants immediately to prevent whitefly transmission. Plant certified virus-free cuttings and resistant cassava varieties."
        if "green mottle" in disease_lower:
            return "Plant clean, virus-free cuttings. Remove and destroy infected plants. Control weed hosts and sap-sucking insect vectors in and around the field."
        if "mosaic" in disease_lower:
            return "No cure for viral infections. Plant CMV-resistant varieties. Use disease-free cuttings. Control whiteflies (the virus vector) using neem oil sprays or systemic insecticides."

    # Coffee diseases
    if crop_lower == "coffee":
        if "cercospora" in disease_lower or "brown eye" in disease_lower:
            return "Maintain proper shade tree density to ensure balanced sunlight. Apply copper fungicides. Ensure adequate nitrogen and potassium fertilization to increase plant resistance."
        if "spider mite" in disease_lower:
            return "Spray overhead irrigation to dislodge mites. Apply sulfur-based miticides or neem oil. Avoid excessive nitrogen which encourages vegetative growth preferred by mites."
        if "rust" in disease_lower:
            return "Plant rust-resistant cultivars (e.g., Ruiru 11, Batian). Apply copper-based preventative fungicides before the onset of rains. Prune canopy to improve airflow."

    # Tea diseases
    if crop_lower == "tea":
        if "algal" in disease_lower or "red rust" in disease_lower:
            return "Improve drainage and reduce shade to increase sunlight penetration. Prune affected branches. Spray copper-based fungicides (e.g., copper oxychloride)."
        if "anthracnose" in disease_lower:
            return "Remove and destroy fallen leaves. Prune tea bushes to improve air circulation. Apply copper or chlorothalonil fungicides during new shoot development."
        if "bird eye" in disease_lower:
            return "Prune lower branches to improve ventilation. Ensure adequate potassium fertilizer. Apply preventative copper fungicides if spotting becomes severe."
        if "brown blight" in disease_lower:
            return "Maintain balanced nutrition (avoid nitrogen excess). Prune infected twigs and leaves. Apply systemic fungicides or copper oxychloride after pruning."
        if "red leaf spot" in disease_lower:
            return "Ensure proper field sanitation by clearing weeds. Prune infected bushes. Apply preventative copper-based sprays during the monsoon/rainy season."

    # Cotton pests/diseases
    if crop_lower == "cotton":
        if "bollworm" in disease_lower:
            return "Apply Bt cotton traits or spray appropriate insecticides (e.g., spinosad or chlorantraniliprole) at threshold levels. Destroy crop residues after harvest."
        if "aphid" in disease_lower:
            return "Apply insecticidal soaps or neem oil. Encourage natural predators like ladybugs. Use chemical control (e.g., imidacloprid) if infestation is severe."
        if "mealy" in disease_lower:
            return "Use biological controls (e.g., ladybird beetles). Remove weeds that harbor mealybugs. Spray soap solution or localized neem oil."
        if "whitefly" in disease_lower:
            return "Use yellow sticky traps. Encourage natural predators. Spray neem oil, or apply systemic insecticides like dinotefuran in severe cases."
        if "thrips" in disease_lower:
            return "Maintain field sanitation. Spray neem-based formulations, or use systemic insecticides like thiamethoxam if thresholds are exceeded."
        if "red cotton bug" in disease_lower:
            return "Collect and destroy bugs manually. Apply neem seed kernel extract (NSKE). Keep fields clean of debris."
        if "anthracnose" in disease_lower:
            return "Treat seeds with fungicides. Remove and burn crop residues. Apply copper-based or systemic fungicides during early vegetative stages."
        if "blight" in disease_lower:
            return "Use disease-free seeds and resistant varieties. Avoid overhead irrigation. Apply copper fungicides if symptoms appear early."
        if "rot" in disease_lower:
            return "Ensure proper plant spacing for air circulation. Avoid excessive nitrogen fertilizer. Spray copper fungicides to reduce rot."

    # Sugarcane diseases
    if crop_lower == "sugarcane":
        if "red rot" in disease_lower:
            return "Plant healthy seed canes from certified nurseries. Remove and burn infected clumps. Rotate sugarcane with non-host crops like rice."
        if "rust" in disease_lower:
            return "Plant resistant sugarcane varieties. Apply foliar fungicides like triazoles (e.g., propiconazole) if rust covers significant leaf area."
        if "mosaic" in disease_lower:
            return "Use virus-free seed cane. Control aphid vectors using neem oil. Remove and destroy infected plants promptly."
        if "yellow" in disease_lower:
            return "Plant disease-resistant clones. Monitor vector aphids and apply neem oil. Remove and destroy early infected crop clumps."

    # Rice diseases
    if crop_lower == "rice":
        if "leaf blast" in disease_lower or "neck blast" in disease_lower or "blast" in disease_lower:
            return "Avoid excessive nitrogen fertilizers. Maintain proper water levels in paddies. Apply foliar fungicides like tricyclazole or carbendazim."
        if "brown spot" in disease_lower or "brownspot" in disease_lower:
            return "Improve soil fertility (especially potassium and nitrogen). Use certified disease-free seeds. Treat seeds with fungicides."
        if "blight" in disease_lower:
            return "Grow resistant rice varieties. Avoid high nitrogen levels. Maintain proper field drainage. Apply copper hydroxide sprays if necessary."
        if "hispa" in disease_lower:
            return "Manual collection of beetles. Cut leaf tips during early infestation to destroy eggs. Spray carbofuran or chlorpyrifos if threshold is exceeded."
        if "tungro" in disease_lower:
            return "Control green leafhopper vectors using systemic insecticides. Plant resistant varieties. Remove infected stubble."

    # Wheat diseases/pests
    if crop_lower == "wheat":
        if "yellow rust" in disease_lower or "stripe rust" in disease_lower:
            return "Plant stripe rust-resistant cultivars. Apply systemic fungicides like propiconazole or tebuconazole immediately at first sign of yellow stripes."
        elif "brown rust" in disease_lower or "leaf rust" in disease_lower or "rust" in disease_lower:
            return "Plant rust-resistant wheat varieties. Apply foliar triazole fungicides (e.g., tebuconazole) when rust pustules appear on upper leaves."
        if "septoria" in disease_lower:
            return "Practice crop rotation with non-cereal crops. Bury crop residues with deep tillage. Apply preventative or curative triazole fungicides at flag leaf emergence."
        if "powdery" in disease_lower:
            return "Use resistant wheat varieties. Avoid thick sowing to allow air circulation. Apply sulfur-based or systemic triazole fungicides."
        if "smut" in disease_lower:
            return "Use certified clean seed. Treat seeds with systemic fungicides (e.g., carboxin or tebuconazole) before sowing."
        if "scab" in disease_lower:
            return "Rotate crops with non-grasses. Avoid sowing wheat directly into corn residue. Apply preventative triazole fungicides at early flowering."
        if "blight" in disease_lower:
            return "Use clean seed. Apply foliar fungicides if lesions reach upper leaves before heading. Keep fields free of volunteer grasses."
        if "aphid" in disease_lower or "mite" in disease_lower or "stem fly" in disease_lower:
            return "Spray appropriate insecticides/miticides (e.g., dimethoate or spiromesifen) if thresholds are reached. Promote natural predators."

    # Maize/Corn pests/diseases
    if crop_lower in ["corn (maize)", "corn", "maize"]:
        if "armyworm" in disease_lower or "army worm" in disease_lower:
            return "Monitor fields early. Apply chemical sprays (e.g., emamectin benzoate or spinetoram) into the crop whorl. Use pheromone traps."
        if "borer" in disease_lower:
            return "Practice crop rotation and intercropping with repellent plants. Destroy crop residues. Apply granular insecticides in the whorl."
        if "ear rot" in disease_lower:
            return "Use insect-resistant hybrids to prevent ear damage. Ensure crop is dried properly before storage. Control ear-feeding insects."

    # Generic Fallbacks based on disease name keywords
    if "mildew" in disease_lower:
        return "Prune to increase airflow. Apply sulfur or potassium bicarbonate sprays. Avoid watering leaves directly."
    if "wilt" in disease_lower:
        return "Ensure good soil drainage. Avoid overwatering. Plant resistant crop varieties. Treat soil with bio-fungicides like Trichoderma."
    if "virus" in disease_lower or "mosaic" in disease_lower:
        return "No chemical cure. Remove and burn infected plants. Control insect vectors (aphids/whiteflies) using neem oil or insecticidal soap."
    if "blight" in disease_lower or "rot" in disease_lower or "spot" in disease_lower:
        return "Prune lower branches to improve airflow. Water at the soil level, not the foliage. Apply copper-based or systemic fungicides."

    return f"Monitor the {crop} plants daily for symptom progression. Prune severely infected parts and destroy them. Consult a local agricultural officer for specific {disease} treatments."

SOIL_DATABASE = {
    "Alluvial_Soil": {
        "soil_type": "Alluvial Soil",
        "npk": {"N": "Low (25%)", "P": "Medium (45%)", "K": "High (75%)"},
        "ph": 6.8,
        "ph_label": "Neutral to Slightly Acidic",
        "suitable_crops": ["Rice", "Wheat", "Sugarcane", "Maize", "Cotton", "Potatoes"],
        "balancing_advice": "Add nitrogen-rich fertilizers (like Urea) and organic compost to boost soil structure. Avoid over-applying potassium as levels are already sufficient.",
        "treatment": "Soil is highly fertile but nitrogen-deficient. Apply organic manure or compost (5 tons/acre) and integrate a nitrogen-balancing fertilizer plan."
    },
    "Arid_Soil": {
        "soil_type": "Arid Soil",
        "npk": {"N": "Very Low (10%)", "P": "Low (20%)", "K": "Medium (50%)"},
        "ph": 8.2,
        "ph_label": "Alkaline / Basic",
        "suitable_crops": ["Sorghum", "Millet", "Cotton", "Sunflower", "Barley"],
        "balancing_advice": "Incorporate sulfur or gypsum to reduce soil alkalinity. Add heavy organic matter and slow-release nitrogenous fertilizers.",
        "treatment": "Soil has low water retention and high alkalinity. Apply organic mulch to retain moisture, use drip irrigation, and balance pH using elemental sulfur."
    },
    "Black_Soil": {
        "soil_type": "Black Soil",
        "npk": {"N": "Medium (50%)", "P": "Low (30%)", "K": "High (80%)"},
        "ph": 7.8,
        "ph_label": "Slightly Alkaline",
        "suitable_crops": ["Cotton", "Wheat", "Sunflower", "Sorghum", "Maize", "Tomatoes"],
        "balancing_advice": "Apply phosphate fertilizers (such as DAP or Single Super Phosphate) to balance phosphorus. Nitrogen is moderate; maintain standard nitrogen inputs.",
        "treatment": "Excellent moisture retention but requires phosphorus supplementation. Use phosphorus-rich fertilizers and practice deep tillage before sowing."
    },
    "Laterite_Soil": {
        "soil_type": "Laterite Soil",
        "npk": {"N": "Low (20%)", "P": "Very Low (15%)", "K": "Low (25%)"},
        "ph": 5.0,
        "ph_label": "Strongly Acidic",
        "suitable_crops": ["Tea", "Coffee", "Bananas", "Mangoes", "Cashew Nuts"],
        "balancing_advice": "Apply agricultural lime (calcium carbonate) or dolomite to neutralize high acidity. Use balanced NPK fertilizers and organic manure.",
        "treatment": "Highly leached and acidic soil. Apply dolomite lime to raise pH, and feed regularly with organic matter and complete micro-nutrients."
    },
    "Mountain_Soil": {
        "soil_type": "Mountain Soil",
        "npk": {"N": "Medium (55%)", "P": "Low (35%)", "K": "Medium (50%)"},
        "ph": 5.8,
        "ph_label": "Moderately Acidic",
        "suitable_crops": ["Tea", "Coffee", "Apples", "Potatoes", "Barley"],
        "balancing_advice": "Check crop sensitivity to acid. For non-acid crops, apply lime. Apply well-composted manure to enhance organic carbon.",
        "treatment": "Rich in organic matter but acidic. Maintain soil cover with mulching to prevent erosion, and use lime to bring pH closer to neutral if needed."
    },
    "Red_Soil": {
        "soil_type": "Red Soil",
        "npk": {"N": "Low (30%)", "P": "Low (25%)", "K": "Medium (60%)"},
        "ph": 6.2,
        "ph_label": "Slightly Acidic",
        "suitable_crops": ["Wheat", "Beans", "Potatoes", "Mangoes", "Peppers", "Maize"],
        "balancing_advice": "Apply balanced NPK fertilizers. Supplement with nitrogen and phosphate to compensate for mineral deficiencies. Add organic compost.",
        "treatment": "Soil has poor water holding capacity and moderate acidity. Mix in bio-char or organic compost, and apply phosphate fertilizer (DAP)."
    },
    "Yellow_Soil": {
        "soil_type": "Yellow Soil",
        "npk": {"N": "Low (35%)", "P": "Low (30%)", "K": "Low (35%)"},
        "ph": 6.0,
        "ph_label": "Slightly Acidic",
        "suitable_crops": ["Rice", "Wheat", "Potatoes", "Maize", "Beans", "Cabbage"],
        "balancing_advice": "Requires comprehensive fertilizing. Apply complete NPK fertilizers along with farmyard manure to supply secondary micronutrients.",
        "treatment": "Leached clayey texture. Improve drainage and apply well-balanced NPK starters. Add lime if pH falls below 5.5 to release bound nutrients."
    }
}

CROP_SOIL_REQUIREMENTS = {
    "Apple": {
        "preferred_soils": ["Mountain Soil", "Red Soil", "Alluvial Soil"],
        "ideal_npk": "Balanced N-P-K (e.g., 10-10-10)",
        "ideal_ph": "6.0 to 7.0 (Slightly Acidic to Neutral)"
    },
    "Maize": {
        "preferred_soils": ["Alluvial Soil", "Black Soil", "Red Soil"],
        "ideal_npk": "High Nitrogen (N), Moderate P & K",
        "ideal_ph": "5.8 to 7.0 (Slightly Acidic to Neutral)"
    },
    "Corn (Maize)": {
        "preferred_soils": ["Alluvial Soil", "Black Soil", "Red Soil"],
        "ideal_npk": "High Nitrogen (N), Moderate P & K",
        "ideal_ph": "5.8 to 7.0 (Slightly Acidic to Neutral)"
    },
    "Mango": {
        "preferred_soils": ["Red Soil", "Laterite Soil", "Alluvial Soil"],
        "ideal_npk": "Low Nitrogen, Moderate P & K (Avoid high N during flowering)",
        "ideal_ph": "5.5 to 7.5 (Acidic to Neutral)"
    },
    "Pepper": {
        "preferred_soils": ["Red Soil", "Alluvial Soil", "Yellow Soil"],
        "ideal_npk": "Moderate N, High Phosphorus (P) for rooting",
        "ideal_ph": "6.0 to 6.8 (Slightly Acidic)"
    },
    "Potato": {
        "preferred_soils": ["Red Soil", "Yellow Soil", "Alluvial Soil", "Mountain Soil"],
        "ideal_npk": "High Potassium (K), Moderate N & P",
        "ideal_ph": "5.0 to 6.0 (Moderately Acidic - suppresses Potato Scab)"
    },
    "Tomato": {
        "preferred_soils": ["Black Soil", "Red Soil", "Alluvial Soil"],
        "ideal_npk": "High Phosphorus (P) and Potassium (K), Moderate Nitrogen (N)",
        "ideal_ph": "6.0 to 6.8 (Slightly Acidic)"
    },
    "Coffee": {
        "preferred_soils": ["Laterite Soil", "Mountain Soil", "Red Soil"],
        "ideal_npk": "High Nitrogen (N) and Potassium (K), Low Phosphorus (P)",
        "ideal_ph": "5.2 to 6.0 (Acidic)"
    },
    "Tea": {
        "preferred_soils": ["Laterite Soil", "Mountain Soil"],
        "ideal_npk": "High Nitrogen (N) (for leaf growth), Moderate P & K",
        "ideal_ph": "4.5 to 5.5 (Highly Acidic - Tea thrives in acid soil)"
    },
    "Rice": {
        "preferred_soils": ["Alluvial Soil", "Yellow Soil", "Red Soil"],
        "ideal_npk": "High Nitrogen (N) and Phosphorus (P)",
        "ideal_ph": "6.0 to 7.0 (Neutral)"
    },
    "Wheat": {
        "preferred_soils": ["Black Soil", "Alluvial Soil", "Red Soil"],
        "ideal_npk": "High Nitrogen (N) (during vegetative phase), Moderate P",
        "ideal_ph": "6.0 to 7.5 (Neutral)"
    },
    "Cotton": {
        "preferred_soils": ["Black Soil", "Alluvial Soil", "Arid Soil"],
        "ideal_npk": "Moderate N, High Potassium (K)",
        "ideal_ph": "6.0 to 8.0 (Neutral to Alkaline)"
    },
    "Beans": {
        "preferred_soils": ["Red Soil", "Yellow Soil", "Alluvial Soil"],
        "ideal_npk": "Low Nitrogen (N fixes itself), High P & K",
        "ideal_ph": "6.0 to 7.0 (Slightly Acidic)"
    }
}

def get_treatment(crop_or_class, health_status=None):
    """
    Looks up treatment and disease details.
    Can be called with:
      - get_treatment(class_name) -> e.g. get_treatment("Tomato___Late_blight")
      - get_treatment(crop_name, health_status) -> e.g. get_treatment("tomato", "Unhealthy")
    """
    # Check if the class is soil
    if "soil" in crop_or_class.lower():
        clean_key = crop_or_class.replace(" ", "_").title()
        soil_info = SOIL_DATABASE.get(clean_key)
        if not soil_info:
            for key, info in SOIL_DATABASE.items():
                if key.lower() == clean_key.lower() or key.replace("_", " ").lower() == crop_or_class.lower():
                    soil_info = info
                    break
        if soil_info:
            return {
                "crop": soil_info["soil_type"],
                "disease": "Soil Scan",
                "treatment": soil_info["treatment"],
                "is_soil": True,
                "soil_type": soil_info["soil_type"],
                "npk_status": soil_info["npk"],
                "ph": soil_info["ph"],
                "ph_label": soil_info["ph_label"],
                "suitable_crops": soil_info["suitable_crops"],
                "balancing_advice": soil_info["balancing_advice"]
            }

    # Case 1: Single argument lookup (PlantVillage or custom class name)
    if health_status is None:
        # Standardize and parse the input class name
        crop, disease = parse_class_name(crop_or_class)
        
        # Check standard dictionary first by looking for a matching parsed representation
        matched_val = None
        for key, value in PLANTVILLAGE_TREATMENTS.items():
            pv_crop, pv_disease = parse_class_name(key)
            if pv_crop.lower() == crop.lower() and (pv_disease.lower() in disease.lower() or disease.lower() in pv_disease.lower()):
                matched_val = value.copy()
                break
        
        if matched_val:
            crop = matched_val["crop"]
            disease = matched_val["disease"]
            treatment = matched_val["treatment"]
        else:
            # Parse dynamically
            treatment = get_dynamic_treatment(crop, disease)
            
        # Format user-friendly disease name
        if disease.lower() == "healthy":
            user_friendly_disease = f"Healthy {crop}"
        elif crop.lower() not in disease.lower():
            user_friendly_disease = f"{crop} {disease}"
        else:
            user_friendly_disease = disease

        return {
            "crop": crop,
            "disease": user_friendly_disease,
            "treatment": treatment
        }

    # Case 2: Legacy two-argument lookup (Crop Name + Health Status)
    crop = crop_or_class.lower()
    status = "Risk" if health_status in ["Unhealthy", "Risk"] else "Healthy"
    
    legacy_data = None
    if crop in LEGACY_TREATMENTS:
        legacy_data = LEGACY_TREATMENTS[crop][status]
        crop_name = crop.capitalize()
        disease_name = legacy_data["disease"]
        treatment = legacy_data["treatment"]
    else:
        # Try finding in PlantVillage dataset by starting crop and matching health
        for class_name, data in PLANTVILLAGE_TREATMENTS.items():
            if class_name.lower().startswith(crop):
                is_healthy_class = "healthy" in class_name.lower()
                if (status == "Healthy" and is_healthy_class) or (status == "Risk" and not is_healthy_class):
                    crop_name = data["crop"]
                    disease_name = data["disease"]
                    treatment = data["treatment"]
                    break
        else:
            # Parse dynamically if not found
            crop_name = crop.capitalize()
            disease_name = "Healthy" if status == "Healthy" else "Disease Risk"
            treatment = get_dynamic_treatment(crop_name, disease_name)

    # Format user-friendly disease name
    if disease_name.lower() == "healthy":
        user_friendly_disease = f"Healthy {crop_name}"
    elif crop_name.lower() not in disease_name.lower():
        user_friendly_disease = f"{crop_name} {disease_name}"
    else:
        user_friendly_disease = disease_name

    return {
        "crop": crop_name,
        "disease": user_friendly_disease,
        "treatment": treatment
    }
