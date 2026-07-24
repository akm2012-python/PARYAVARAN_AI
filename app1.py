import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import serial
import serial.tools.list_ports
import time
import os
from datetime import datetime

# Streamlit autorefresh fallback handling
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False

# Page Configuration
st.set_page_config(
    page_title="Paryavaran AI - Smart Bus Stand Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #070e10; color: #e0f2f1; }
    div[data-testid="stSidebar"] { background-color: #0f1d20; border-right: 1px solid #1e4d48; }
    .metric-card {
        background: linear-gradient(135deg, rgba(17,38,42,0.9) 0%, rgba(11,20,22,0.95) 100%);
        border: 1px solid #1e4d48;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
    }
    .metric-title { font-size: 0.8rem; text-transform: uppercase; color: #80cbc4; font-weight: 600; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: #e0f2f1; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# Session State Initializations
if 'serial_conn' not in st.session_state:
    st.session_state.serial_conn = None
if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False
if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=[
        'Timestamp', 'Temperature', 'Humidity', 'Dustbin', 'Person', 'DayNight',
        'Fan', 'Score', 'Status', 'AirQuality', 'AirStatus', 'Recommendation',
        'Buzzer', 'HighTemp', 'MQRaw', 'AirQualityPercent', 'EnergySaving'
    ])
if 'log_file' not in st.session_state:
    st.session_state.log_file = f"bus_stand_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# Sidebar Connection Panel
st.sidebar.title("🌱 Paryavaran AI")
st.sidebar.caption("Aditya Kumar Mohanani | PM SHRI JNV Burhanpur")

available_ports = [p.device for p in serial.tools.list_ports.comports()]
if not available_ports:
    available_ports = ["COM1", "COM2", "COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyACM0"]

selected_port = st.sidebar.selectbox("Select Port", available_ports)
baud_rate = st.sidebar.selectbox("Baud Rate", [9600, 115200], index=0)

col_c1, col_c2 = st.sidebar.columns(2)

def connect_serial():
    try:
        st.session_state.serial_conn = serial.Serial(selected_port, baud_rate, timeout=1)
        time.sleep(1.5)  # Wait for Arduino reset
        st.session_state.serial_conn.reset_input_buffer()
        st.session_state.is_connected = True
        st.sidebar.success(f"Connected to {selected_port}")
    except Exception as e:
        st.sidebar.error(f"Failed: {e}")

def disconnect_serial():
    if st.session_state.serial_conn and st.session_state.serial_conn.is_open:
        st.session_state.serial_conn.close()
    st.session_state.is_connected = False
    st.session_state.serial_conn = None

col_c1.button("Connect", on_click=connect_serial, use_container_width=True)
col_c2.button("Disconnect", on_click=disconnect_serial, use_container_width=True)

use_sim = False
if st.session_state.is_connected:
    st.sidebar.markdown("🟢 **Status:** Real Serial Stream Active")
else:
    st.sidebar.markdown("🔴 **Status:** Offline")
    use_sim = st.sidebar.checkbox("Enable EcoTwin™ Simulation Mode", value=True)

# Auto Refresh Control
if HAS_AUTOREFRESH:
    st_autorefresh(interval=1000, key="datarefresh")

# Data Ingestion Function
def acquire_telemetry():
    if st.session_state.is_connected and st.session_state.serial_conn and st.session_state.serial_conn.is_open:
        try:
            line = st.session_state.serial_conn.readline().decode('utf-8', errors='ignore').strip()
            if line:
                parts = line.split(',')
                if len(parts) >= 15:
                    temp = float(parts[0])
                    hum = float(parts[1])
                    dust = int(parts[2])
                    person = parts[3]
                    daynight = parts[4]
                    fan = parts[5]
                    score = int(parts[6])
                    status = parts[7]
                    air_ppm = int(parts[8])
                    air_status = parts[9]
                    recom = parts[10]
                    buzzer = parts[11]
                    hightemp = int(parts[12])
                    mqraw = int(parts[13])
                    air_pct = int(parts[14])
                    
                    energy_saving = 100
                    if fan == "ON" and person == "None": energy_saving -= 30
                    if daynight == "Night" and person == "None": energy_saving -= 20
                    if hightemp == 1: energy_saving -= 10
                    
                    return {
                        'Timestamp': datetime.now().strftime('%H:%M:%S'),
                        'Temperature': temp, 'Humidity': hum, 'Dustbin': dust,
                        'Person': person, 'DayNight': daynight, 'Fan': fan,
                        'Score': score, 'Status': status, 'AirQuality': air_ppm,
                        'AirStatus': air_status, 'Recommendation': recom,
                        'Buzzer': buzzer, 'HighTemp': hightemp, 'MQRaw': mqraw,
                        'AirQualityPercent': air_pct, 'EnergySaving': max(0, energy_saving)
                    }
        except Exception:
            pass

    if not st.session_state.is_connected and use_sim:
        np.random.seed(int(time.time() * 10) % 100000)
        temp = round(28.0 + np.random.normal(2, 2), 1)
        hum = round(55.0 + np.random.normal(0, 4), 1)
        dust = int(np.clip(45 + np.random.randint(-10, 15), 0, 100))
        person = "Detected" if np.random.rand() > 0.4 else "None"
        daynight = "Night" if np.random.rand() > 0.7 else "Day"
        fan = "ON" if (temp > 30 and person == "Detected") else "OFF"
        
        mqraw = int(np.clip(220 + np.random.randint(-30, 80), 0, 1023))
        air_ppm = int(mqraw * 0.8 + 100)
        air_pct = int(np.clip(100 - (mqraw / 1023.0 * 100), 0, 100))
        air_status = "Fresh" if mqraw < 250 else ("Moderate" if mqraw < 400 else "Unhealthy")
        
        score = 100
        if temp > 30: score -= 20
        if dust > 80: score -= 20
        if air_status != "Fresh": score -= 15
        if daynight == "Night" and person == "None": score -= 10
        score = int(np.clip(score, 0, 100))
        
        status = "Excellent" if score >= 90 else ("Good" if score >= 70 else ("Average" if score >= 50 else "Poor"))
        buzzer = "ON" if dust >= 90 else "OFF"
        hightemp = 1 if temp > 30 else 0
        
        recom = "Everything Normal"
        if dust >= 80: recom = "Dustbin almost full"
        elif air_status != "Fresh": recom = "Poor Air Quality"
        elif fan == "ON": recom = "Fan ON because passenger detected"
        elif score >= 90: recom = "Energy Saving Excellent"

        energy_saving = 100 - (30 if (fan == "ON" and person == "None") else 0) - (20 if (daynight == "Night" and person == "None") else 0)

        return {
            'Timestamp': datetime.now().strftime('%H:%M:%S'),
            'Temperature': temp, 'Humidity': hum, 'Dustbin': dust,
            'Person': person, 'DayNight': daynight, 'Fan': fan,
            'Score': score, 'Status': status, 'AirQuality': air_ppm,
            'AirStatus': air_status, 'Recommendation': recom,
            'Buzzer': buzzer, 'HighTemp': hightemp, 'MQRaw': mqraw,
            'AirQualityPercent': air_pct, 'EnergySaving': max(0, energy_saving)
        }
    return None

# Append Received Data
new_record = acquire_telemetry()
if new_record:
    df_new = pd.DataFrame([new_record])
    st.session_state.data_history = pd.concat([st.session_state.data_history, df_new], ignore_index=True).tail(50)
    
    file_exists = os.path.isfile(st.session_state.log_file)
    df_new.to_csv(st.session_state.log_file, mode='a', header=not file_exists, index=False)

# UI Display
st.title("🌱 Paryavaran AI - Smart Bus Stand Core")
st.caption("Explainable Edge AI Green Energy Infrastructure | PM SHRI JNV Burhanpur")

if not st.session_state.data_history.empty:
    latest = st.session_state.data_history.iloc[-1]
    
    # Recommendation Header
    banner_bg = "#004d40"
    if "full" in str(latest['Recommendation']).lower(): banner_bg = "#b71c1c"
    elif "poor" in str(latest['Recommendation']).lower(): banner_bg = "#e65100"
    elif "fan" in str(latest['Recommendation']).lower(): banner_bg = "#0277bd"
    
    st.markdown(f"""
        <div style="background-color: {banner_bg}; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px; font-weight: 600;">
            🤖 <b>GreenExplain XAI™:</b> {latest['Recommendation']}
        </div>
    """, unsafe_allow_html=True)

    # 8 KPI Metric Cards
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    metrics = [
        ("Passenger", "🏃 Yes" if latest['Person']=='Detected' else "🚫 None", c1),
        ("Ambient", "🌙 Night" if latest['DayNight']=='Night' else "☀️ Day", c2),
        ("Fan Relay", "🌀 ON" if latest['Fan']=='ON' else "❄️ OFF", c3),
        ("Street Light", "💡 ON" if latest['DayNight']=='Night' else "🌑 OFF", c4),
        ("TriLogic", "🔴 Red" if latest['Dustbin']>80 else ("🟡 Yel" if latest['Dustbin']>=50 else "🟢 Grn"), c5),
        ("Buzzer", "🔔 ON" if latest['Buzzer']=='ON' else "🔕 OFF", c6),
        ("Heat Alert", "🔥 High" if latest['HighTemp']==1 else "✅ Normal", c7),
        ("AI Status", f"{latest['Status']}", c8)
    ]
    
    for label, val, col in metrics:
        with col:
            st.markdown(f"""<div class="metric-card"><div class="metric-title">{label}</div>
            <div class="metric-value">{val}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Gauges Section
    st.subheader("📊 Performance & Environmental Gauges")
    g1, g2, g3, g4 = st.columns(4)

    def draw_gauge(val, title, min_v, max_v, bar_color):
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=val,
            title={'text': title, 'font': {'size': 15, 'color': '#80cbc4'}},
            gauge={'axis': {'range': [min_v, max_v]}, 'bar': {'color': bar_color}}
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=200, margin=dict(l=15, r=15, t=30, b=15))
        return fig

    g1.plotly_chart(draw_gauge(latest['Temperature'], "Temperature (°C)", 0, 50, "#26a69a"), use_container_width=True)
    g2.plotly_chart(draw_gauge(latest['AirQualityPercent'], "Air Quality %", 0, 100, "#66bb6a"), use_container_width=True)
    g3.plotly_chart(draw_gauge(latest['Score'], "Green AI Score", 0, 100, "#80d8ff"), use_container_width=True)
    g4.plotly_chart(draw_gauge(latest['EnergySaving'], "Energy Saving %", 0, 100, "#a7ffeb"), use_container_width=True)

    # Historical Telemetry Charts
    st.subheader("📈 Real-Time Environmental & AI Analytics")
    ch1, ch2 = st.columns(2)
    df_h = st.session_state.data_history

    with ch1:
        f_env = go.Figure()
        f_env.add_trace(go.Scatter(x=df_h['Timestamp'], y=df_h['Temperature'], name='Temp (°C)', line=dict(color='#ff7043')))
        f_env.add_trace(go.Scatter(x=df_h['Timestamp'], y=df_h['Humidity'], name='Humidity (%)', line=dict(color='#26c6da')))
        f_env.add_trace(go.Scatter(x=df_h['Timestamp'], y=df_h['Dustbin'], name='Dustbin Level (%)', line=dict(color='#ab47bc')))
        f_env.update_layout(template="plotly_dark", height=280, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(f_env, use_container_width=True)

    with ch2:
        f_ai = go.Figure()
        f_ai.add_trace(go.Scatter(x=df_h['Timestamp'], y=df_h['Score'], name='Green AI Score', line=dict(color='#00e676', width=2.5)))
        f_ai.add_trace(go.Scatter(x=df_h['Timestamp'], y=df_h['AirQualityPercent'], name='Air Quality %', line=dict(color='#ffca28')))
        f_ai.add_trace(go.Scatter(x=df_h['Timestamp'], y=df_h['EnergySaving'], name='Energy Saving %', line=dict(color='#29b6f6')))
        f_ai.update_layout(template="plotly_dark", height=280, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(f_ai, use_container_width=True)

    # Telemetry Log & Download
    st.subheader("📋 Session Telemetry Log")
    st.dataframe(df_h.tail(10), use_container_width=True)
    
    st.download_button(
        label="📥 Export Session Telemetry CSV",
        data=df_h.to_csv(index=False).encode('utf-8'),
        file_name=f"Paryavaran_AI_Telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.info("Awaiting sensor telemetry... Connect Arduino hardware or enable EcoTwin™ Simulation in the sidebar.")