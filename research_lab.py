"""
Paryavaran AI - Automated ML Research Suite & Paper Generator
Author: Aditya Kumar Mohanani
"""

import pandas as pd
import numpy as np
import os

# ML Models
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression

def run_research_pipeline(csv_path="paryavaran_ai_research_data.csv"):
    print("🚀 Initializing Paryavaran AI Research Suite...")
    
    if not os.path.exists(csv_path):
        print(f"❌ Error: Dataset '{csv_path}' not found. Generate data via Streamlit dashboard first.")
        return

    df = pd.read_csv(csv_path)
    print(f"📊 Dataset Loaded: {len(df)} samples.")

    # Feature Engineering
    feature_cols = ['Temperature', 'Humidity', 'Dustbin', 'MQRaw', 'PowerWatts']
    X = df[feature_cols].fillna(0)
    y = df['Score'].fillna(100)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    regressors = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(),
        "Random Forest": RandomForestRegressor(n_estimators=50),
        "Gradient Boosting": GradientBoostingRegressor(),
        "AdaBoost": AdaBoostRegressor()
    }

    results = []
    print("\n--- 🧬 ModelArena™ Performance Leaderboard ---")
    for name, model in regressors.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        r2 = r2_score(y_test, preds)
        results.append({"Model": name, "RMSE": round(rmse, 4), "R2 Score": round(r2, 4)})
        print(f"✅ {name:20s} | RMSE: {rmse:.4f} | R²: {r2:.4f}")

    # Generate Research Paper Draft
    generate_ieee_paper_draft(results)

def generate_ieee_paper_draft(results):
    paper_content = f"""
================================================================================
PARYAVARAN AI: AN EXPLAINABLE TERNARY-LOGIC SMART BUS STAND FOR SUSTAINABLE CITIES
Author: Aditya Kumar Mohanani
================================================================================

ABSTRACT
Internet of Things (IoT) edge deployments in municipal smart infrastructures often suffer 
from unexplainable black-box decision models and high continuous power overheads. In this 
paper, we present 'Paryavaran AI', an Explainable AI (XAI) enabled eco-bus stand system 
powered by a Ternary Logic Framework (TriLogic Engine™). Running on resource-constrained 
embedded hardware (Arduino UNO), the system processes multi-sensor metrics to govern energy 
consumption while explaining decision outputs.

I. INTRODUCTION
Smart city deployments require transparent decision-making. Paryavaran AI introduces 
Explainable AI (XAI) feature attribution alongside a ternary framework (-1: ALERT, 0: BALANCED, 
+1: ECO) to replace traditional binary logic.

II. METHODOLOGY & HARDWARE
The system utilizes DHT11 (temperature/humidity), HC-SR04 (ultrasonic waste level), MQ135 
(air quality), IR sensors (occupancy), and LDR modules (ambient lighting). Derived metrics, 
such as power draw and carbon offsets, are estimated mathematically.

III. RESULTS & MODELARENA™ BENCHMARK
The experimental results across ML regressors predicting the EarthScore™ are summarized below:

"""
    for r in results:
        paper_content += f"- {r['Model']}: RMSE = {r['RMSE']}, R² = {r['R2 Score']}\n"

    paper_content += """
IV. CONCLUSION
Paryavaran AI proves that explainability and ternary computing can be deployed effectively 
in edge IoT environments without requiring high-cost hardware additions.
================================================================================
"""
    with open("Paryavaran_AI_Research_Paper_Draft.txt", "w") as f:
        f.write(paper_content)
    print("\n📄 Publication Draft Saved to 'Paryavaran_AI_Research_Paper_Draft.txt'")

if __name__ == "__main__":
    run_research_pipeline()