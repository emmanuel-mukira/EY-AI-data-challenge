#!/usr/bin/env python3
"""
Complete EY AI Data Challenge Benchmark Runner
This script runs the entire benchmark pipeline end-to-end
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from snowflake.snowpark import Session

def main():
    print("🚀 Starting EY AI Data Challenge Benchmark Pipeline")
    print("=" * 60)
    
    # 1. Connect to Snowflake
    print("\n📡 Connecting to Snowflake...")
    try:
        session = Session.builder.configs({
            "account": "jfecknb-lwb72940",
            "user": "EmmanuelMukira",
            "password": "qikcox-kifxe4-xodqIn",
            "warehouse": "COMPUTE_WH",
            "database": "USER$EMMANUELMUKIRA",
            "schema": "PUBLIC"
        }).create()
        print("✅ Connected to Snowflake")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # 2. Load and prepare data
    print("\n📊 Loading training data...")
    try:
        # Load water quality data
        wq_data = pd.read_csv("water_quality_training_dataset.csv")
        
        # Load feature data
        landsat_train = pd.read_csv("landsat_features_training.csv")
        terraclimate_train = pd.read_csv("terraclimate_features_training.csv")
        
        # Merge datasets
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
        
        print(f"✅ Training data loaded: {len(train_data)} samples")
        
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # 3. Train models
    print("\n🤖 Training ML models...")
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import r2_score, mean_squared_error
    
    def run_pipeline(X, y, target_name):
        """Train and evaluate model for a target variable"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train_scaled)
        test_pred = model.predict(X_test_scaled)
        
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        
        print(f"  {target_name}:")
        print(f"    Train R²: {train_r2:.3f}, Test R²: {test_r2:.3f}")
        print(f"    Train RMSE: {train_rmse:.3f}, Test RMSE: {test_rmse:.3f}")
        
        return model, scaler, {
            'Target': target_name,
            'Train_R2': train_r2,
            'Test_R2': test_r2,
            'Train_RMSE': train_rmse,
            'Test_RMSE': test_rmse
        }
    
    # Prepare features and targets
    X = train_data.drop(columns=['Total Alkalinity', 'Electrical Conductance', 'Dissolved Reactive Phosphorus'])
    y_TA = train_data['Total Alkalinity']
    y_EC = train_data['Electrical Conductance']
    y_DRP = train_data['Dissolved Reactive Phosphorus']
    
    # Train all models
    model_TA, scaler_TA, results_TA = run_pipeline(X, y_TA, "Total Alkalinity")
    model_EC, scaler_EC, results_EC = run_pipeline(X, y_EC, "Electrical Conductance")
    model_DRP, scaler_DRP, results_DRP = run_pipeline(X, y_DRP, "Dissolved Reactive Phosphorus")
    
    # 4. Load validation data and make predictions
    print("\n🔮 Making predictions on validation data...")
    try:
        # Load validation data
        test_file = pd.read_csv("submission_template.csv")
        landsat_val = pd.read_csv("landsat_features_validation.csv")
        terraclimate_val = pd.read_csv("terraclimate_features_validation.csv")
        
        # Prepare validation features
        val_data = pd.DataFrame({
            'swir22': landsat_val['swir22'].values,
            'NDMI': landsat_val['NDMI'].values,
            'MNDWI': landsat_val['MNDWI'].values,
            'pet': terraclimate_val['pet'].values,
        })
        
        # Handle missing values
        val_data = val_data.fillna(val_data.median(numeric_only=True))
        
        # Make predictions
        X_val_scaled_TA = scaler_TA.transform(val_data)
        X_val_scaled_EC = scaler_EC.transform(val_data)
        X_val_scaled_DRP = scaler_DRP.transform(val_data)
        
        pred_TA = model_TA.predict(X_val_scaled_TA)
        pred_EC = model_EC.predict(X_val_scaled_EC)
        pred_DRP = model_DRP.predict(X_val_scaled_DRP)
        
        # Create submission dataframe
        submission_df = pd.DataFrame({
            'Longitude': test_file['Longitude'].values,
            'Latitude': test_file['Latitude'].values,
            'Sample Date': test_file['Sample Date'].values,
            'Total Alkalinity': pred_TA,
            'Electrical Conductance': pred_EC,
            'Dissolved Reactive Phosphorus': pred_DRP
        })
        
        print(f"✅ Generated {len(submission_df)} predictions")
        
    except Exception as e:
        print(f"❌ Failed to generate predictions: {e}")
        return
    
    # 5. Save submission
    print("\n💾 Saving submission files...")
    try:
        # Save locally
        submission_df.to_csv("submission.csv", index=False)
        print(f"✅ Saved to: {os.path.abspath('submission.csv')}")
        
        # Save to Snowflake
        submission_snowpark = session.create_dataframe(submission_df)
        submission_snowpark.write.mode("overwrite").save_as_table("SUBMISSION_RESULTS")
        print("✅ Saved to Snowflake table: SUBMISSION_RESULTS")
        
    except Exception as e:
        print(f"⚠️ Could not save to Snowflake: {e}")
        print("✅ Local file saved successfully")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("🎯 BENCHMARK COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    results_summary = pd.DataFrame([results_TA, results_EC, results_DRP])
    print("\n📊 Model Performance Summary:")
    print(results_summary.to_string(index=False))
    
    print(f"\n📤 Submission ready:")
    print(f"  - File: {os.path.abspath('submission.csv')}")
    print(f"  - Size: {os.path.getsize('submission.csv'):,} bytes")
    print(f"  - Predictions: {len(submission_df)}")
    
    print(f"\n🔍 Sample predictions:")
    print(submission_df.head(3).to_string(index=False))
    
    print("\n📤 NEXT STEPS:")
    print("1. Download submission.csv")
    print("2. Upload to EY AI Challenge platform")
    print("3. Check leaderboard!")
    
    # Close session
    session.close()
    print("\n✅ Pipeline completed successfully!")

if __name__ == "__main__":
    # Change to the correct directory
    os.chdir("/home/emmanuel/EY-AI-data-challenge/Snowflake Notebooks Package")
    main()
