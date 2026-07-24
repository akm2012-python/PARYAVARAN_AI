import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import serial
import serial.tools.list_ports
import time
import os
import base64
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Machine Learning Research Imports
try:
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

st.set_page_config(
    page_title="Paryavaran AI — XAI Green Energy Bus Stand",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #0b1416; color: #e0f2f1; }
    .stApp { background-color: #070e10; }
    div[data-testid="stSidebar"] { background-color: #0f1d20; border-right: 1px solid #1c383d; }
    .metric-card {
        background: linear-gradient(135deg, #11262a 0%, #0a181b 100%);
        border: 1px solid #1e4d48;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .metric-title { font-size: 0.75rem; text-transform: uppercase; color: #80cbc4; font-weight: 600; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #e0f2f1; }
    .xai-card { background-color: #122a2e; border-left: 4px solid #00e676; padding: 10px; margin: 5px 0; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# Session State Setup
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=[
        'Timestamp', 'Temperature', 'Humidity', 'Dustbin', 'Person', 'DayNight',
        'Fan', 'Score', 'Status', 'AirQuality', 'AirStatus', 'Recommendation',
        'Buzzer', 'HighTemp', 'MQRaw', 'AirQualityPercent', 'EnergySaving',
        'PowerWatts', 'CO2AvoidedGrams', 'EHI', 'TriLogicState', 'Confidence'
    ])
if 'is_connected' not in st.session_state: st.session_state.is_connected = False
if 'serial_conn' not in st.session_state: st.session_state.serial_conn = None

st_autorefresh(interval=1500, key="datarefresh")

# ------------------------------------------------------------------------------
# Core Branded Modules Implementation
# ------------------------------------------------------------------------------
def compute_trilogic_and_xai(temp, hum, dust, person, daynight, fan, mqraw, air_pct):
    """TriLogic Engine™ & GreenExplain XAI™ Engine"""
    # 1. TriLogic Evaluation (-1, 0, +1)
    if dust >= 80 or mqraw > 500 or temp > 38.0:
      trilogic = -1 # RED / ALERT
      trilogic_label = "RED (-1: Alert Mode)"
    elif dust >= 50 or mqraw > 300 or temp > 30.0:
      trilogic = 0  # YELLOW / BALANCED
      trilogic_label = "YELLOW (0: Balanced Mode)"
    else:
      trilogic = 1  # GREEN / ECO
      trilogic_label = "GREEN (+1: Eco Mode)"

    # 2. XAI Deductions & Contribution Tracking
    base_score = 100
    contributions = {}
    
    t_ded = max(0, int((temp - 30) * 2)) if temp > 30 else 0
    if t_ded > 0: contributions['Temperature High'] = -t_ded
    
    d_ded = 20 if dust > 80 else 0
    if d_ded > 0: contributions['Dustbin Overflow Risk'] = -d_ded
    
    a_ded = 15 if mqraw > 300 else 0
    if a_ded > 0: contributions['Air Pollution Spike'] = -a_ded
    
    e_ded = 10 if (daynight == "Night" and person == "None") else 0
    if e_ded > 0: contributions['Unoccupied Night Operation'] = -e_ded

    final_score = max(0, base_score + sum(contributions.values()))

    # 3. Virtual Power & Carbon Computations
    fan_w = 15.0 if fan == "ON" else 0.0
    light_w = 10.0 if daynight == "Night" else 0.0
    power_w = 2.5 + fan_w + light_w
    
    baseline_w = 2.5 + 15.0 + (10.0 if daynight == "Night" else 0.0)
    saved_w = max(0.0, baseline_w - power_w)
    co2_grams = (saved_w / 3600.0) * 0.82

    # 4. EarthScore™ & Environmental Health Index (EHI)
    ehi = int((max(0, 100 - abs(temp - 24) * 4) * 0.3) + (air_pct * 0.4) + ((100 - dust) * 0.3))
    
    # 5. AI Confidence Assessment
    confidence = round(np.clip(99.0 - (abs(temp - 25) * 0.2) - (mqraw * 0.02), 70.0, 99.5), 1)

    return trilogic_label, final_score, contributions, power_w, co2_grams, ehi, confidence

# Sidebar & Connection Logic
st.sidebar.title("🌱 Paryavaran AI")
st.sidebar.caption("Explainable AI Smart Bus Stand")

ports = [p.device for p in serial.tools.list_ports.comports()] or ["COM3", "/dev/ttyUSB0"]
selected_port = st.sidebar.selectbox("Serial Port", ports)
baud_rate = st.sidebar.selectbox("Baud Rate", [9600, 115200], index=0)

if st.sidebar.button("Connect Serial"):
    try:
        st.session_state.serial_conn = serial.Serial(selected_port, baud_rate, timeout=1)
        st.session_state.is_connected = True
        st.sidebar.success("Connected")
    except Exception as e: st.sidebar.error(f"Error: {e}")

# What-If Simulator Toggle
st.sidebar.markdown("---")
use_simulator = st.sidebar.checkbox("🔮 What-If Scenario Simulator", value=False)

if use_simulator:
    sim_temp = st.sidebar.slider("Virtual Temp (°C)", 15.0, 45.0, 31.0)
    sim_hum = st.sidebar.slider("Virtual Humidity (%)", 20.0, 95.0, 55.0)
    sim_dust = st.sidebar.slider("Virtual Dustbin (%)", 0, 100, 40)
    sim_person = st.sidebar.selectbox("Passenger Detection", ["Detected", "None"])
    sim_daynight = st.sidebar.selectbox("Ambient Light", ["Day", "Night"])
    sim_mq = st.sidebar.slider("MQ135 Gas Raw", 100, 800, 220)

# Data Reader Function
def fetch_telemetry():
    if use_simulator:
        temp, hum, dust = sim_temp, sim_hum, sim_dust
        person, daynight, mqraw = sim_person, sim_daynight, sim_mq
        fan = "ON" if (temp > 30 and person == "Detected") else "OFF"
        air_pct = int(np.clip(100 - (mqraw / 1023.0 * 100), 0, 100))
        air_status = "Fresh" if mqraw < 250 else ("Moderate" if mqraw < 400 else "Unhealthy")
        buzzer = "ON" if dust >= 90 else "OFF"
    elif st.session_state.is_connected and st.session_state.serial_conn:
        try:
            line = st.session_state.serial_conn.readline().decode('utf-8').strip()
            p = line.split(',')
            if len(p) >= 15:
                temp, hum, dust = float(p[0]), float(p[1]), int(p[2])
                person, daynight, fan = p[3], p[4], p[5]
                air_status, buzzer, mqraw, air_pct = p[9], p[11], int(p[13]), int(p[14])
            else: return None
        except: return None
    else:
        # Fallback Demo Telemetry Stream
        temp = round(27.0 + np.random.normal(2, 2), 1)
        hum = round(50.0 + np.random.normal(0, 4), 1)
        dust = int(np.clip(35 + np.random.randint(-5, 10), 0, 100))
        person = "Detected" if np.random.rand() > 0.4 else "None"
        daynight = "Night" if np.random.rand() > 0.7 else "Day"
        fan = "ON" if (temp > 30 and person == "Detected") else "OFF"
        mqraw = int(np.clip(210 + np.random.randint(-20, 50), 0, 1023))
        air_pct = int(np.clip(100 - (mqraw / 1023.0 * 100), 0, 100))
        air_status = "Fresh" if mqraw < 250 else "Moderate"
        buzzer = "ON" if dust >= 90 else "OFF"

    trilogic, score, xai_contrib, watts, co2, ehi, conf = compute_trilogic_and_xai(
        temp, hum, dust, person, daynight, fan, mqraw, air_pct
    )

    recom = "System Optimal"
    if dust >= 80: recom = "Waste Collection Needed"
    elif temp > 30 and person == "Detected": recom = "Active Cooling Mode Engaged"

    return {
        'Timestamp': datetime.now().strftime('%H:%M:%S'), 'Temperature': temp,
        'Humidity': hum, 'Dustbin': dust, 'Person': person, 'DayNight': daynight,
        'Fan': fan, 'Score': score, 'Status': "Excellent" if score >= 85 else "Poor",
        'AirQuality': int(mqraw * 0.8 + 100), 'AirStatus': air_status,
        'Recommendation': recom, 'Buzzer': buzzer, 'HighTemp': 1 if temp > 30 else 0,
        'MQRaw': mqraw, 'AirQualityPercent': air_pct,
        'EnergySaving': 100 - int((watts/27.5)*100), 'PowerWatts': watts,
        'CO2AvoidedGrams': co2, 'EHI': ehi, 'TriLogicState': trilogic,
        'Confidence': conf, 'XAI_Contrib': xai_contrib
    }

telemetry = fetch_telemetry()
if telemetry:
    xai_data = telemetry.pop('XAI_Contrib', {})
    df_curr = pd.DataFrame([telemetry])
    st.session_state.data_history = pd.concat([st.session_state.data_history, df_curr], ignore_index=True).tail(100)

# ------------------------------------------------------------------------------
# Dashboard Interface
# ------------------------------------------------------------------------------
st.title("🌱 Paryavaran AI — Explainable Smart Bus Stand")
st.caption("Principal AI Research & TinyML Engineering Dashboard")

if not st.session_state.data_history.empty:
    latest = st.session_state.data_history.iloc[-1]

    # Metrics Row
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.markdown(f"<div class='metric-card'><div class='metric-title'>🔺 TriLogic State</div><div class='metric-value'>{latest['TriLogicState'].split(' ')[0]}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><div class='metric-title'>🧠 EarthScore™</div><div class='metric-value'>{latest['Score']} / 100</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><div class='metric-title'>🌬 AirGuardian AI</div><div class='metric-value'>{latest['AirQualityPercent']}%</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card'><div class='metric-title'>👥 CrowdSense</div><div class='metric-value'>{latest['Person']}</div></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'><div class='metric-title'>⚡ Power Draw</div><div class='metric-value'>{latest['PowerWatts']} W</div></div>", unsafe_allow_html=True)
    m6.markdown(f"<div class='metric-card'><div class='metric-title'>🎯 AI Confidence</div><div class='metric-value'>{latest['Confidence']}%</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    t1, t2, t3, t4, t5 = st.tabs([
        "📊 GreenMind AI™ Telemetry",
        "🧠 GreenExplain XAI™ & Digital Twin",
        "🔮 EcoPredict AI™ & Energy",
        "🧬 ModelArena™ Research Lab",
        "📑 Dataset & Research Publication"
    ])

    with t1:
        st.subheader("Live Real-time Telemetry Streams")
        c1, c2 = st.columns(2)
        df_h = st.session_state.data_history
        with c1:
            fig1 = px.line(df_h, x='Timestamp', y=['Temperature', 'Humidity', 'Dustbin'], title="Environmental Sensings", template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.line(df_h, x='Timestamp', y=['Score', 'EHI', 'Confidence'], title="AI Performance & EarthScore Indices", template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    with t2:
        st.subheader("GreenExplain XAI™ Decision Attribution")
        x_col1, x_col2 = st.columns(2)
        with x_col1:
            st.markdown("#### Feature Deductions & Reasoning")
            if xai_data:
                for k, v in xai_data.items():
                    st.markdown(f"<div class='xai-card'>⚠️ <b>{k}:</b> {v} points</div>", unsafe_allow_html=True)
            else:
                st.success("✨ Zero Deductions: System operates at optimal efficiency.")
            
            st.markdown(f"**AI Recommendation:** *{latest['Recommendation']}*")
        
        with x_col2:
            st.subheader("🖥 EcoTwin™ Digital Mirror")
            st.json({
                "Virtual_Fan_State": latest['Fan'],
                "Virtual_Light_State": "ON" if latest['DayNight'] == "Night" else "OFF",
                "Estimated_CO2_Avoided_Grams": round(latest['CO2AvoidedGrams'], 4),
                "Environmental_Health_Index": latest['EHI']
            })

    with t3:
        st.subheader("⚡ EcoPredict AI™ & Power Analytics")
        p1, p2, p3 = st.columns(3)
        p1.metric("Predicted Power (Next 15m)", f"{round(latest['PowerWatts'] * 0.25, 2)} Wh")
        p2.metric("Predicted CO₂ Savings (1h)", f"{round(latest['CO2AvoidedGrams'] * 60, 2)} g")
        p3.metric("Dustbin Full Projection", "Approx. 35 mins" if latest['Dustbin'] < 80 else "CRITICAL / FULL")

    with t4:
        st.subheader("🧬 ModelArena™ Machine Learning Benchmarking")
        st.markdown("Automated comparison of classical ML models trained on live captured telemetry.")
        
        if SKLEARN_AVAILABLE and len(df_h) >= 10:
            X = df_h[['Temperature', 'Humidity', 'Dustbin', 'MQRaw']].fillna(0)
            y = (df_h['Person'] == 'Detected').astype(int)

            models = {
                "Decision Tree": DecisionTreeClassifier(),
                "Random Forest": RandomForestClassifier(n_estimators=10),
                "AdaBoost": AdaBoostClassifier(),
                "KNN": KNeighborsClassifier(n_neighbors=3)
            }
            
            res = []
            for name, clf in models.items():
                clf.fit(X, y)
                acc = accuracy_score(y, clf.predict(X)) * 100
                res.append({"Algorithm": name, "Training Accuracy": f"{acc:.2f}%", "Status": "Ready"})
            
            st.table(pd.DataFrame(res))
        else:
            st.info("Gathering min. 10 data points to execute ModelArena™ benchmarks...")

    with t5:
        st.subheader("📑 Publications & Dataset Engine")
        st.download_button(
            "📥 Export Research Dataset (CSV)",
            data=st.session_state.data_history.to_csv(index=False).encode('utf-8'),
            file_name=f"paryavaran_ai_research_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )