import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import serial
import serial.tools.list_ports
import time
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Page Config
st.set_page_config(
    page_title="EcoSmart AI Bus Stand - AI Dashboard",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Green Theme)
st.markdown("""
    <style>
    .main {
        background-color: #0d1b1e;
        color: #e0f2f1;
    }
    .stApp {
        background-color: #0b1719;
    }
    div[data-testid="stSidebar"] {
        background-color: #112428;
        border-right: 1px solid #1f3a3e;
    }
    .metric-card {
        background: linear-gradient(135deg, #132a2f 0%, #0d1e22 100%);
        border: 1px solid #1d4745;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #80cbc4;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e0f2f1;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
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

# Auto refresh every 1 second when connected
if st.session_state.is_connected:
    st_autorefresh(interval=1000, key="datarefresh")

# Sidebar - Connection Controls
st.sidebar.title("🌿 EcoSmart AI")
st.sidebar.subheader("Bus Stand Control Panel")

ports = [port.device for port in serial.tools.list_ports.comports()]
if not ports:
    ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "/dev/ttyUSB0", "/dev/ttyACM0"]

selected_port = st.sidebar.selectbox("Select COM Port", ports)
baud_rate = st.sidebar.selectbox("Baud Rate", [9600, 115200], index=0)

col_conn1, col_conn2 = st.sidebar.columns(2)

def connect_serial():
    try:
        st.session_state.serial_conn = serial.Serial(selected_port, baud_rate, timeout=1)
        st.session_state.is_connected = True
        st.sidebar.success(f"Connected to {selected_port}")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

def disconnect_serial():
    if st.session_state.serial_conn and st.session_state.serial_conn.is_open:
        st.session_state.serial_conn.close()
    st.session_state.is_connected = False
    st.session_state.serial_conn = None
    st.sidebar.info("Disconnected")

col_conn1.button("Connect", on_click=connect_serial, use_container_width=True)
col_conn2.button("Disconnect", on_click=disconnect_serial, use_container_width=True)

# Connection Status Indicator
if st.session_state.is_connected:
    st.sidebar.markdown("🟢 **Status:** Connected & Stream Reading")
else:
    st.sidebar.markdown("🔴 **Status:** Offline / Simulated Stream Available")
    use_simulation = st.sidebar.checkbox("Enable Demo Simulation Mode", value=True)

# Data Reading Function
def read_data():
    if st.session_state.is_connected and st.session_state.serial_conn and st.session_state.serial_conn.is_open:
        try:
            line = st.session_state.serial_conn.readline().decode('utf-8').strip()
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
                    if fan == "ON" and person == "None":
                        energy_saving -= 30
                    if daynight == "Night" and person == "None":
                        energy_saving -= 20
                    if hightemp == 1:
                        energy_saving -= 10
                        
                    return {
                        'Timestamp': datetime.now().strftime('%H:%M:%S'),
                        'Temperature': temp,
                        'Humidity': hum,
                        'Dustbin': dust,
                        'Person': person,
                        'DayNight': daynight,
                        'Fan': fan,
                        'Score': score,
                        'Status': status,
                        'AirQuality': air_ppm,
                        'AirStatus': air_status,
                        'Recommendation': recom,
                        'Buzzer': buzzer,
                        'HighTemp': hightemp,
                        'MQRaw': mqraw,
                        'AirQualityPercent': air_pct,
                        'EnergySaving': energy_saving
                    }
        except Exception as e:
            pass
            
    if not st.session_state.is_connected and 'use_simulation' in locals() and use_simulation:
        np.random.seed(int(time.time() * 10) % 100000)
        temp = round(28.0 + np.random.normal(2, 3), 1)
        hum = round(55.0 + np.random.normal(0, 5), 1)
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
        score = max(0, min(100, score))
        
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
            'Temperature': temp,
            'Humidity': hum,
            'Dustbin': dust,
            'Person': person,
            'DayNight': daynight,
            'Fan': fan,
            'Score': score,
            'Status': status,
            'AirQuality': air_ppm,
            'AirStatus': air_status,
            'Recommendation': recom,
            'Buzzer': buzzer,
            'HighTemp': hightemp,
            'MQRaw': mqraw,
            'AirQualityPercent': air_pct,
            'EnergySaving': energy_saving
        }
    return None

new_data = read_data()
if new_data:
    df_new = pd.DataFrame([new_data])
    st.session_state.data_history = pd.concat([st.session_state.data_history, df_new], ignore_index=True).tail(50)
    
    file_exists = os.path.isfile(st.session_state.log_file)
    df_new.to_csv(st.session_state.log_file, mode='a', header=not file_exists, index=False)

# Main Title Header
st.title("🌱 EcoSmart AI Bus Stand")
st.caption("National Science Exhibition Project | Real-time IoT & AI Green Energy Monitoring System")

if not st.session_state.data_history.empty:
    latest = st.session_state.data_history.iloc[-1]
    
    rec_color = "#004d40"
    if "full" in latest['Recommendation'].lower(): rec_color = "#b71c1c"
    elif "Poor" in latest['Recommendation'].lower(): rec_color = "#e65100"
    elif "Fan" in latest['Recommendation'].lower(): rec_color = "#0277bd"
    
    st.markdown(f"""
        <div style="background-color: {rec_color}; padding: 12px 20px; border-radius: 10px; margin-bottom: 20px; font-weight: 600; font-size: 1.1rem;">
            🤖 <b>AI System Recommendation:</b> {latest['Recommendation']}
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Passenger</div>
        <div class="metric-value">{"🏃 Yes" if latest['Person']=='Detected' else "🚫 None"}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Ambient</div>
        <div class="metric-value">{"🌙 Night" if latest['DayNight']=='Night' else "☀️ Day"}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Fan Relay</div>
        <div class="metric-value">{"🌀 ON" if latest['Fan']=='ON' else "❄️ OFF"}</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Street Light</div>
        <div class="metric-value">{"💡 ON" if latest['DayNight']=='Night' else "🌑 OFF"}</div></div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Traffic Light</div>
        <div class="metric-value">{"🔴 Red" if latest['Dustbin']>80 else ("🟡 Yel" if latest['Dustbin']>=50 else "🟢 Grn")}</div></div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Buzzer</div>
        <div class="metric-value">{"🔔 ON" if latest['Buzzer']=='ON' else "🔕 OFF"}</div></div>""", unsafe_allow_html=True)
    with col7:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">Heat Alert</div>
        <div class="metric-value">{"🔥 High" if latest['HighTemp']==1 else "✅ Normal"}</div></div>""", unsafe_allow_html=True)
    with col8:
        st.markdown(f"""<div class="metric-card"><div class="metric-title">AI Status</div>
        <div class="metric-value" style="font-size:1.2rem;">{latest['Status']}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Gauges Section
    st.subheader("📊 Operational Gauges & Health Metrics")
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)

    with g_col1:
        fig_temp = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest['Temperature'],
            title={'text': "Temperature (°C)", 'font': {'size': 16, 'color': '#80cbc4'}},
            gauge={
                'axis': {'range': [0, 50], 'tickcolor': "#80cbc4"},
                'bar': {'color': "#26a69a"},
                'steps': [
                    {'range': [0, 30], 'color': "#004d40"},
                    {'range': [30, 50], 'color': "#b71c1c"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 30}
            }
        ))
        fig_temp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_temp, use_container_width=True)

    with g_col2:
        fig_air = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest['AirQualityPercent'],
            title={'text': "Air Quality %", 'font': {'size': 16, 'color': '#80cbc4'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#80cbc4"},
                'bar': {'color': "#66bb6a"},
                'steps': [
                    {'range': [0, 40], 'color': "#b71c1c"},
                    {'range': [40, 70], 'color': "#f57f17"},
                    {'range': [70, 100], 'color': "#1b5e20"}
                ]
            }
        ))
        fig_air.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_air, use_container_width=True)

    with g_col3:
        fig_score = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest['Score'],
            title={'text': "Green AI Score", 'font': {'size': 16, 'color': '#80cbc4'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#80cbc4"},
                'bar': {'color': "#80d8ff"},
                'steps': [
                    {'range': [0, 50], 'color': "#b71c1c"},
                    {'range': [50, 70], 'color': "#f57f17"},
                    {'range': [70, 90], 'color': "#558b2f"},
                    {'range': [90, 100], 'color': "#00c853"}
                ]
            }
        ))
        fig_score.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_score, use_container_width=True)

    with g_col4:
        fig_energy = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest['EnergySaving'],
            title={'text': "Energy Saving %", 'font': {'size': 16, 'color': '#80cbc4'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': "#80cbc4"},
                'bar': {'color': "#a7ffeb"},
                'steps': [
                    {'range': [0, 50], 'color': "#ff6f00"},
                    {'range': [50, 100], 'color': "#00796b"}
                ]
            }
        ))
        fig_energy.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=220, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_energy, use_container_width=True)

    # Real-time Charts Section
    st.subheader("📈 Real-Time Environmental & AI Analytics")
    c_col1, c_col2 = st.columns(2)

    df_hist = st.session_state.data_history

    with c_col1:
        fig_env = go.Figure()
        fig_env.add_trace(go.Scatter(x=df_hist['Timestamp'], y=df_hist['Temperature'], mode='lines+markers', name='Temp (°C)', line=dict(color='#ff7043', width=2)))
        fig_env.add_trace(go.Scatter(x=df_hist['Timestamp'], y=df_hist['Humidity'], mode='lines', name='Humidity (%)', line=dict(color='#26c6da', width=2)))
        fig_env.add_trace(go.Scatter(x=df_hist['Timestamp'], y=df_hist['Dustbin'], mode='lines', name='Dustbin Level (%)', line=dict(color='#ab47bc', width=2)))
        fig_env.update_layout(title="Temperature, Humidity & Dustbin Dynamics", template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_env, use_container_width=True)

    with c_col2:
        fig_ai = go.Figure()
        fig_ai.add_trace(go.Scatter(x=df_hist['Timestamp'], y=df_hist['Score'], mode='lines+markers', name='AI Green Score', line=dict(color='#00e676', width=3)))
        fig_ai.add_trace(go.Scatter(x=df_hist['Timestamp'], y=df_hist['AirQualityPercent'], mode='lines', name='Air Quality %', line=dict(color='#ffca28', width=2)))
        fig_ai.add_trace(go.Scatter(x=df_hist['Timestamp'], y=df_hist['EnergySaving'], mode='lines', name='Energy Saving %', line=dict(color='#29b6f6', width=2)))
        fig_ai.update_layout(title="AI Green Performance & Eco Index", template="plotly_dark", height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_ai, use_container_width=True)

    # Data Table and Export
    st.subheader("📋 Live Telemetry Log & Data Export")
    st.dataframe(df_hist.tail(10), use_container_width=True)

    csv_bytes = df_hist.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Session Telemetry CSV",
        data=csv_bytes,
        file_name=f"EcoSmart_Bus_Stand_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.info("Awaiting sensor data... Connect Arduino or enable Simulation Mode in the sidebar.")