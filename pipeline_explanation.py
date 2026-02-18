#!/usr/bin/env python3
"""
Detailed EY AI Challenge Pipeline Explanation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

def explain_pipeline():
    print("=" * 80)
    print("EY AI DATA CHALLENGE - COMPLETE PIPELINE EXPLANATION")
    print("=" * 80)
    
    print("\n🎯 OBJECTIVE:")
    print("Predict 3 water quality parameters for South African river locations")
    print("using satellite and climate data.")
    
    print("\n📊 DATA STRUCTURE:")
    print("-" * 40)
    
    # Load and show training data structure
    wq_data = pd.read_csv("water_quality_training_dataset.csv")
    landsat_train = pd.read_csv("landsat_features_training.csv")
    terraclimate_train = pd.read_csv("terraclimate_features_training.csv")
    
    print(f"Water Quality Data: {wq_data.shape}")
    print("  Columns:", list(wq_data.columns))
    print(f"  Sample:\n{wq_data.head(2)}")
    
    print(f"\nLandsat Features: {landsat_train.shape}")
    print("  Key columns: Longitude, Latitude, Sample Date, nir, green, swir16, swir22, NDMI, MNDWI")
    print(f"  Sample:\n{landsat_train[['Longitude', 'Latitude', 'swir22', 'NDMI', 'MNDWI']].head(2)}")
    
    print(f"\nTerraClimate Features: {terraclimate_train.shape}")
    print("  Key columns: pet (Potential Evapotranspiration)")
    print(f"  Sample:\n{terraclimate_train.head(2)}")
    
    print("\n🔬 FEATURE ENGINEERING:")
    print("-" * 40)
    print("1. SPECTRAL INDICES (from Landsat):")
    print("   - NDMI = (NIR - SWIR) / (NIR + SWIR)")
    print("     → Measures vegetation moisture stress")
    print("   - MNDWI = (Green - SWIR) / (Green + SWIR)")  
    print("     → Enhances water bodies in satellite imagery")
    
    print("\n2. SPECTRAL BANDS:")
    print("   - SWIR22 (Shortwave Infrared 2)")
    print("     → Sensitive to water content, soil moisture")
    print("   - NIR, Green: Used for index calculations")
    
    print("\n3. CLIMATE FEATURE:")
    print("   - PET (Potential Evapotranspiration)")
    print("     → Atmospheric demand for moisture")
    print("     → Affects water concentration in rivers")
    
    print("\n🤖 MODEL TRAINING:")
    print("-" * 40)
    
    # Prepare training data
    train_data = pd.DataFrame({
        'swir22': landsat_train['swir22'].values,
        'NDMI': landsat_train['NDMI'].values,
        'MNDWI': landsat_train['MNDWI'].values,
        'pet': terraclimate_train['pet'].values,
        'Total Alkalinity': wq_data['Total Alkalinity'].values,
        'Electrical Conductance': wq_data['Electrical Conductance'].values,
        'Dissolved Reactive Phosphorus': wq_data['Dissolved Reactive Phosphorus'].values
    })
    
    # Handle missing values
    train_data = train_data.fillna(train_data.median(numeric_only=True))
    
    print(f"Training dataset shape: {train_data.shape}")
    print(f"Features: {list(train_data.columns[:4])}")
    print(f"Targets: {list(train_data.columns[4:])}")
    
    # Show feature statistics
    print("\n📈 FEATURE STATISTICS:")
    print("-" * 40)
    features = ['swir22', 'NDMI', 'MNDWI', 'pet']
    for feature in features:
        print(f"{feature:12}: min={train_data[feature].min():.3f}, max={train_data[feature].max():.3f}, mean={train_data[feature].mean():.3f}")
    
    print("\n🎯 TARGET VARIABLE STATISTICS:")
    print("-" * 40)
    targets = ['Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus']
    for target in targets:
        print(f"{target:25}: min={train_data[target].min():.2f}, max={train_data[target].max():.2f}, mean={train_data[target].mean():.2f}")
    
    print("\n🔄 MODEL ARCHITECTURE:")
    print("-" * 40)
    print("3 Independent Random Forest Models:")
    print("  1. Model_TA → Predicts Total Alkalinity")
    print("  2. Model_EC → Predicts Electrical Conductance") 
    print("  3. Model_DRP → Predicts Dissolved Reactive Phosphorus")
    print("\nEach model uses the same 4 features: [swir22, NDMI, MNDWI, pet]")
    
    print("\n⚙️ TRAINING PROCESS:")
    print("-" * 40)
    print("1. Data Split: 70% train, 30% test (random_state=42)")
    print("2. Feature Scaling: StandardScaler (mean=0, std=1)")
    print("3. Model: RandomForestRegressor(n_estimators=100, random_state=42)")
    print("4. Evaluation: R² score and RMSE")
    
    # Demonstrate with one model
    X = train_data[features]
    y = train_data['Total Alkalinity']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    train_pred = model.predict(X_train_scaled)
    test_pred = model.predict(X_test_scaled)
    
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    print(f"\nExample (Total Alkalinity):")
    print(f"  Train R²: {train_r2:.3f}")
    print(f"  Test R²:  {test_r2:.3f}")
    print(f"  Feature importance: {dict(zip(features, model.feature_importances_.round(3)))}")
    
    print("\n📍 VALIDATION & SUBMISSION:")
    print("-" * 40)
    
    # Load validation data
    test_file = pd.read_csv("submission_template.csv")
    landsat_val = pd.read_csv("landsat_features_validation.csv")
    terraclimate_val = pd.read_csv("terraclimate_features_validation.csv")
    
    print(f"Validation locations: {len(test_file)}")
    print("Each location has:")
    print("  - Longitude, Latitude: Geographic coordinates")
    print("  - Sample Date: When measurement was taken")
    print("  - Features: Same 4 features extracted from satellite/climate data")
    
    print("\n📤 SUBMISSION FILE FORMAT:")
    print("-" * 40)
    print("Required columns:")
    print("  - Longitude: Location identifier")
    print("  - Latitude: Location identifier") 
    print("  - Sample Date: Measurement date")
    print("  - Total Alkalinity: Model prediction")
    print("  - Electrical Conductance: Model prediction")
    print("  - Dissolved Reactive Phosphorus: Model prediction")
    
    print("\n🔍 WHY LAT/LONG IN SUBMISSION?")
    print("-" * 40)
    print("1. IDENTIFICATION: Links predictions to specific river locations")
    print("2. VALIDATION: Platform matches your predictions with ground truth")
    print("3. SPATIAL ANALYSIS: Water quality varies by location")
    print("4. REPRODUCIBILITY: Results can be mapped and verified")
    
    print("\n🌍 PHYSICAL MEANING OF FEATURES:")
    print("-" * 40)
    print("SWIR22 ↑ → More water/turbidity → Lower water quality")
    print("NDMI ↑   → More vegetation moisture → Better water quality")  
    print("MNDWI ↑  → More water surface → Variable effects")
    print("PET ↑    → Higher evaporation → More concentrated pollutants")
    
    print("\n" + "=" * 80)
    print("PIPELINE EXPLANATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import os
    os.chdir("/home/emmanuel/EY-AI-data-challenge/Snowflake Notebooks Package")
    explain_pipeline()
