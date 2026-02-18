# EY AI Data Challenge - Complete Pipeline Explanation

## 🎯 Objective
Predict 3 water quality parameters for South African river locations using satellite and climate data.

## 📊 Data Structure

### Training Data (9,319 samples)
- **water_quality_training_dataset.csv**: Target variables (what we predict)
  - Total Alkalinity, Electrical Conductance, Dissolved Reactive Phosphorus
- **landsat_features_training.csv**: Satellite features from Landsat
- **terraclimate_features_training.csv**: Climate features from TerraClimate

### Validation Data (200 samples)
- **submission_template.csv**: Locations needing predictions
- **landsat_features_validation.csv**: Satellite features for validation
- **terraclimate_features_validation.csv**: Climate features for validation

## 🔬 Feature Engineering

### Satellite Features (Landsat)
- **SWIR22** (Shortwave Infrared 2): Sensitive to water content and turbidity
  - Range: 3,634 - 31,203
  - Higher values = more water content/turbidity

- **NDMI** (Normalized Difference Moisture Index):
  - Formula: (NIR - SWIR) / (NIR + SWIR)
  - Range: -0.328 - 0.568
  - Physical meaning: Vegetation moisture stress
  - Higher values = healthier vegetation, better water quality

- **MNDWI** (Modified Normalized Difference Water Index):
  - Formula: (Green - SWIR) / (Green + SWIR)
  - Range: -0.300 - 0.591
  - Physical meaning: Water body detection
  - Higher values = more open water surface

### Climate Features (TerraClimate)
- **PET** (Potential Evapotranspiration):
  - Range: 52.7 - 270.8 mm
  - Physical meaning: Atmospheric moisture demand
  - Higher values = more evaporation, concentrated pollutants

## 🎯 Target Variables (What We Predict)

### Total Alkalinity (mg/L)
- Range: 4.80 - 361.68 (mean: 119.11)
- Water's capacity to neutralize acids
- Important for aquatic life

### Electrical Conductance (µS/cm)
- Range: 15.12 - 1,506.00 (mean: 485.00)
- Measures dissolved salts and minerals
- Higher = more pollution

### Dissolved Reactive Phosphorus (mg/L)
- Range: 5.00 - 195.00 (mean: 43.53)
- Nutrient that causes algal blooms
- High levels = poor water quality

## 🤖 Model Architecture

### 3 Independent Random Forest Models
1. **Model_TA** → Predicts Total Alkalinity
2. **Model_EC** → Predicts Electrical Conductance
3. **Model_DRP** → Predicts Dissolved Reactive Phosphorus

Each model uses the same 4 features: `[swir22, NDMI, MNDWI, pet]`

### Training Process
1. Data Split: 70% train, 30% test (random_state=42)
2. Feature Scaling: StandardScaler (mean=0, std=1)
3. Model: RandomForestRegressor(n_estimators=100, random_state=42)
4. Evaluation: R² score and RMSE

### Current Performance
- **Total Alkalinity**: R² = 0.546 ✅ (exceeds 0.45 requirement)
- **Electrical Conductance**: R² = 0.585 ✅
- **Dissolved Reactive Phosphorus**: R² = 0.529 ✅

## 📍 Validation & Submission

### Why Latitude/Longitude in Submission File?
1. **Identification**: Links predictions to specific river locations
2. **Validation**: Platform matches your predictions with ground truth
3. **Spatial Analysis**: Water quality varies by location
4. **Reproducibility**: Results can be mapped and verified

### Submission File Format
Required columns:
- **Longitude**: Location identifier
- **Latitude**: Location identifier
- **Sample Date**: Measurement date
- **Total Alkalinity**: Model prediction
- **Electrical Conductance**: Model prediction
- **Dissolved Reactive Phosphorus**: Model prediction

## 🌍 Physical Meaning of Features

- **SWIR22 ↑** → More water/turbidity → Lower water quality
- **NDMI ↑** → More vegetation moisture → Better water quality
- **MNDWI ↑** → More water surface → Variable effects
- **PET ↑** → Higher evaporation → More concentrated pollutants

## 📊 Complete Data Flow

```
TRAINING DATA (9,319 samples)                    VALIDATION DATA (200 samples)
┌─────────────────────────────┐                ┌─────────────────────────────┐
│ Water Quality Measurements │                │   Locations needing         │
│ - Total Alkalinity          │                │   predictions               │
│ - Electrical Conductance    │  ┌────────────►│ - Longitude/Latitude        │
│ - Dissolved Reactive Phos   │  │             │ - Sample Date               │
└─────────────────────────────┘  │             └─────────────────────────────┘
             ▲                    │                        ▲
             │                    │                        │
┌─────────────────────────────┐  │  ┌─────────────────────────────┐
│   Landsat Satellite Data    │  │  │   Landsat Satellite Data    │
│ - SWIR22, NIR, Green        │  │  │ - Same spectral features    │
│ - NDMI, MNDWI indices       │  │  │ - Same indices              │
└─────────────────────────────┘  │  └─────────────────────────────┘
             ▲                    │                        ▲
             │                    │                        │
┌─────────────────────────────┐  │  ┌─────────────────────────────┐
│   TerraClimate Data         │  │  │   TerraClimate Data         │
│ - PET (Evapotranspiration)  │  │  │ - PET values                │
└─────────────────────────────┘  │  └─────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │   FEATURE ENGINEERING       │
                    │ - Select 4 key features      │
                    │ - Handle missing values      │
                    │ - Scale features             │
                    └─────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │   MODEL TRAINING            │
                    │ - 3 Random Forest models     │
                    │ - One per target variable    │
                    │ - R² ≥ 0.45 achieved         │
                    └─────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │   PREDICTION & SUBMISSION   │
                    │ - Generate 200 predictions   │
                    │ - Include lat/long for ID    │
                    │ - Upload to leaderboard     │
                    └─────────────────────────────┘
```

## 🎯 Key Takeaways

1. **Feature Importance**: PET is most influential (43.1%) in current model
2. **Model Performance**: All targets exceed R² ≥ 0.45 requirement
3. **Submission Format**: Lat/long are essential identifiers for validation
4. **Physical Meaning**: Each feature has clear hydrological significance
