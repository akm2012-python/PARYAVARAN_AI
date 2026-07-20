"""
EcoSmart AI Bus Stand - Streamlit Dashboard
Reads Arduino Serial data and displays live sensor information
"""

import serial
import serial.tools.list_ports
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import threading
import queue
import json
import os
from collections import deque

# ===================== CONFIGURATION =====================
SERIAL_BAUD = 9600
MAX_DATA_POINTS = 100
HISTORY_FILE = "sensor_history.json"

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="EcoSmart AI Bus Stand",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-excellent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-good {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-poor {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .recommendation-box {
        background: #f0f8ff;
        border-left: 5px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        font-size: 1.1rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SERIAL READER CLASS =====================
class SerialReader:
    def __init__(self):
        self.ser = None
        self.running = False
        self.data_queue = queue.Queue()
        self.thread = None
        self.connected = False
        
    def find_arduino_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description or "USB-SERIAL" in port.description:
                return port.device
            if port.device in ['/dev/ttyUSB0', '/dev/ttyACM0', 'COM3', 'COM4', 'COM5', 'COM6']:
                return port.device
        if ports:
            return ports[0].device
        return None
    
    def connect(self, port=None):
        if port is None:
            port = self.find_arduino_port()
        if port is None:
            return False
        try:
            self.ser = serial.Serial(port, SERIAL_BAUD, timeout=2)
            time.sleep(2)
            self.connected = True
            return True
        except Exception as e:
            st.error(f"Serial connection failed: {e}")
            return False
    
    def read_loop(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line and ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 8:
                            data = {
                                'temperature': float(parts[0]),
                                'humidity': float(parts[1]),
                                'dustbin': int(parts[2]),
                                'person': int(parts[3]),
                                'daynight': int(parts[4]),
                                'fan': int(parts[5]),
                                'score': int(parts[6]),
                                'status': parts[7]
                            }
                            self.data_queue.put(data)
            except Exception:
                pass
            time.sleep(0.1)
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
    
    def get_data(self):
        data_list = []
        while not self.data_queue.empty():
            try:
                data_list.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return data_list

# ===================== SESSION STATE =====================
if 'serial_reader' not in st.session_state:
    st.session_state.serial_reader = SerialReader()
if 'history' not in st.session_state:
    st.session_state.history = {
        'timestamps': deque(maxlen=MAX_DATA_POINTS),
        'temperature': deque(maxlen=MAX_DATA_POINTS),
        'humidity': deque(maxlen=MAX_DATA_POINTS),
        'dustbin': deque(maxlen=MAX_DATA_POINTS),
        'score': deque(maxlen=MAX_DATA_POINTS)
    }
if 'latest_data' not in st.session_state:
    st.session_state.latest_data = {
        'temperature': 25.0,
        'humidity': 50.0,
        'dustbin': 0,
        'person': 0,
        'daynight': 1,
        'fan': 0,
        'score': 100,
        'status': 'Excellent'
    }
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = "Disconnected"

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("🔌 Connection Settings")
    
    ports = serial.tools.list_ports.comports()
    port_options = [p.device for p in ports] if ports else ["COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyACM0"]
    selected_port = st.selectbox("Select Serial Port", port_options)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect", type="primary"):
            reader = st.session_state.serial_reader
            reader.stop()
            if reader.connect(selected_port):
                reader.start()
                st.session_state.connection_status = f"Connected to {selected_port}"
                st.success("Connected!")
            else:
                st.session_state.connection_status = "Failed"
                st.error("Connection failed")
    with col2:
        if st.button("Disconnect"):
            st.session_state.serial_reader.stop()
            st.session_state.connection_status = "Disconnected"
            st.info("Disconnected")
    
    st.markdown(f"**Status:** {st.session_state.connection_status}")
    
    st.header("📊 Settings")
    refresh_rate = st.slider("Refresh Rate (seconds)", 1, 10, 2)
    
    st.header("ℹ️ About")
    st.markdown("""
    **EcoSmart AI Bus Stand**
    
    Green Energy Monitoring System
    
    - DHT11: Temperature & Humidity
    - HC-SR04: Dustbin Level
    - IR Sensor: Passenger Detection
    - LDR: Day/Night Detection
    - Relay: Fan Control
    - Traffic Light: Status Indicator
    """)

# ===================== MAIN DASHBOARD =====================
st.markdown('<div class="main-header">🚌 EcoSmart AI Bus Stand</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Green Energy Smart Monitoring System</div>', unsafe_allow_html=True)

# Read new data from serial
reader = st.session_state.serial_reader
new_data_list = reader.get_data()
if new_data_list:
    st.session_state.latest_data = new_data_list[-1]
    for d in new_data_list:
        ts = time.strftime("%H:%M:%S")
        st.session_state.history['timestamps'].append(ts)
        st.session_state.history['temperature'].append(d['temperature'])
        st.session_state.history['humidity'].append(d['humidity'])
        st.session_state.history['dustbin'].append(d['dustbin'])
        st.session_state.history['score'].append(d['score'])

data = st.session_state.latest_data

# ===================== METRICS ROW =====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌡️ Temperature", f"{data['temperature']:.1f} °C", "DHT11")
    
with col2:
    st.metric("💧 Humidity", f"{data['humidity']:.1f} %", "DHT11")
    
with col3:
    dustbin_status = "🔴 Full" if data['dustbin'] >= 80 else ("🟡 Medium" if data['dustbin'] >= 50 else "🟢 Low")
    st.metric("🗑️ Dustbin Level", f"{data['dustbin']}%", dustbin_status)
    
with col4:
    person_status = "👤 Present" if data['person'] else "❌ None"
    st.metric("🚶 Passenger", person_status, "IR Sensor")

# ===================== STATUS ROW =====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    day_status = "☀️ Day" if data['daynight'] else "🌙 Night"
    st.metric("🌗 Day/Night", day_status, "LDR Sensor")
    
with col2:
    fan_status = "💨 ON" if data['fan'] else "⏹️ OFF"
    st.metric("🌀 Fan Status", fan_status, "Relay Control")
    
with col3:
    relay_status = "🔌 ACTIVE" if data['fan'] else "⏸️ IDLE"
    st.metric("⚡ Relay", relay_status, "LOW Trigger")
    
with col4:
    traffic_map = {"GREEN": "🟢 GREEN", "YELLOW": "🟡 YELLOW", "RED": "🔴 RED", "Excellent": "🟢 GREEN", "Good": "🟡 YELLOW", "Poor": "🔴 RED"}
    traffic_display = traffic_map.get(data['status'], "🟢 GREEN")
    st.metric("🚦 Traffic Light", traffic_display, "Status Indicator")

# ===================== AI SCORE & RECOMMENDATION =====================
st.markdown("---")
score_col, rec_col = st.columns([1, 2])

with score_col:
    score = data['score']
    if score >= 80:
        status_class = "status-excellent"
        status_emoji = "🌟"
    elif score >= 50:
        status_class = "status-good"
        status_emoji = "⚡"
    else:
        status_class = "status-poor"
        status_emoji = "⚠️"
    
    st.markdown(f'<div class="{status_class}">{status_emoji} AI Green Score: {score}/100</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; margin-top:10px; font-size:1.1rem;"><b>Status: {data["status"]}</b></div>', unsafe_allow_html=True)
    
    energy_saving = score
    st.progress(energy_saving / 100)
    st.markdown(f'<div style="text-align:center;">Estimated Energy Saving: <b>{energy_saving}%</b></div>', unsafe_allow_html=True)

with rec_col:
    st.subheader("🤖 AI System Recommendation")
    
    if not data['person'] and data['fan']:
        rec_text = "No passenger detected. Fan turned OFF."
        rec_icon = "💡"
    elif data['temperature'] > 30 and data['person'] and data['fan']:
        rec_text = "High temperature detected. Fan ON for passenger comfort."
        rec_icon = "🌡️"
    elif data['dustbin'] >= 90:
        rec_text = "Dustbin almost full! Please empty immediately."
        rec_icon = "🚨"
    elif data['dustbin'] > 80:
        rec_text = "Dustbin over 80%. Schedule emptying soon."
        rec_icon = "⚠️"
    elif data['status'] == "Excellent":
        rec_text = "Energy Saving Excellent. System operating at optimal efficiency."
        rec_icon = "🌟"
    elif not data['daynight'] and not data['person']:
        rec_text = "Night mode. Bus stand inactive. Minimal energy consumption."
        rec_icon = "🌙"
    else:
        rec_text = "System operating within normal parameters."
        rec_icon = "✅"
    
    st.markdown(f'<div class="recommendation-box">{rec_icon} <b>{rec_text}</b></div>', unsafe_allow_html=True)

# ===================== LIVE CHARTS =====================
st.markdown("---")
st.subheader("📈 Live Sensor Charts")

hist = st.session_state.history
if len(hist['timestamps']) > 1:
    # Temperature Chart
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=list(hist['timestamps']),
        y=list(hist['temperature']),
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=6)
    ))
    fig_temp.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="Threshold 30°C")
    fig_temp.update_layout(
        title="Temperature Trend",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        height=300,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # Dustbin Chart
    fig_dust = go.Figure()
    fig_dust.add_trace(go.Bar(
        x=list(hist['timestamps']),
        y=list(hist['dustbin']),
        name='Dustbin %',
        marker_color=['#FF6B6B' if v >= 80 else '#FFD93D' if v >= 50 else '#6BCB77' for v in hist['dustbin']]
    ))
    fig_dust.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Critical 80%")
    fig_dust.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Warning 50%")
    fig_dust.update_layout(
        title="Dustbin Fill Level",
        xaxis_title="Time",
        yaxis_title="Fill Percentage (%)",
        height=300,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # AI Score Chart
    fig_score = go.Figure()
    fig_score.add_trace(go.Scatter(
        x=list(hist['timestamps']),
        y=list(hist['score']),
        mode='lines+markers',
        name='AI Score',
        line=dict(color='#4ECDC4', width=2),
        fill='tozeroy',
        fillcolor='rgba(78, 205, 196, 0.2)',
        marker=dict(size=6)
    ))
    fig_score.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Excellent")
    fig_score.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Good")
    fig_score.update_layout(
        title="AI Green Energy Score",
        xaxis_title="Time",
        yaxis_title="Score (0-100)",
        height=300,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(fig_temp, use_container_width=True, key="temp_chart")
    with chart_col2:
        st.plotly_chart(fig_dust, use_container_width=True, key="dust_chart")
    
    st.plotly_chart(fig_score, use_container_width=True, key="score_chart")
else:
    st.info("⏳ Waiting for sensor data... Connect to Arduino and wait for data stream.")
    fig_empty = go.Figure()
    fig_empty.update_layout(
        title="Waiting for data...",
        height=300,
        template="plotly_white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        annotations=[dict(text="Connect Arduino to see live charts", showarrow=False, font_size=16)]
    )
    st.plotly_chart(fig_empty, use_container_width=True, key="empty_chart")

# ===================== RAW DATA TABLE =====================
st.markdown("---")
with st.expander("📋 Raw Sensor Data"):
    st.json(data)
    
    if len(hist['timestamps']) > 0:
        import pandas as pd
        df_data = {
            'Time': list(hist['timestamps']),
            'Temperature': list(hist['temperature']),
            'Humidity': list(hist['humidity']),
            'Dustbin %': list(hist['dustbin']),
            'AI Score': list(hist['score'])
        }
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

# Auto-refresh
st.markdown("---")
st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')} | EcoSmart AI Bus Stand v1.0")

time.sleep(refresh_rate)
st.rerun()
"""
EcoSmart AI Bus Stand - Streamlit Dashboard
Reads Arduino Serial data and displays live sensor information
"""

import serial
import serial.tools.list_ports
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import threading
import queue
import json
import os
from collections import deque

# ===================== CONFIGURATION =====================
SERIAL_BAUD = 9600
MAX_DATA_POINTS = 100
HISTORY_FILE = "sensor_history.json"

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="EcoSmart AI Bus Stand",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-excellent {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-good {
        background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-poor {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .recommendation-box {
        background: #f0f8ff;
        border-left: 5px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        font-size: 1.1rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ===================== SERIAL READER CLASS =====================
class SerialReader:
    def __init__(self):
        self.ser = None
        self.running = False
        self.data_queue = queue.Queue()
        self.thread = None
        self.connected = False
        
    def find_arduino_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "CH340" in port.description or "USB-SERIAL" in port.description:
                return port.device
            if port.device in ['/dev/ttyUSB0', '/dev/ttyACM0', 'COM3', 'COM4', 'COM5', 'COM6']:
                return port.device
        if ports:
            return ports[0].device
        return None
    
    def connect(self, port=None):
        if port is None:
            port = self.find_arduino_port()
        if port is None:
            return False
        try:
            self.ser = serial.Serial(port, SERIAL_BAUD, timeout=2)
            time.sleep(2)
            self.connected = True
            return True
        except Exception as e:
            st.error(f"Serial connection failed: {e}")
            return False
    
    def read_loop(self):
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line and ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 8:
                            data = {
                                'temperature': float(parts[0]),
                                'humidity': float(parts[1]),
                                'dustbin': int(parts[2]),
                                'person': int(parts[3]),
                                'daynight': int(parts[4]),
                                'fan': int(parts[5]),
                                'score': int(parts[6]),
                                'status': parts[7]
                            }
                            self.data_queue.put(data)
            except Exception:
                pass
            time.sleep(0.1)
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
    
    def get_data(self):
        data_list = []
        while not self.data_queue.empty():
            try:
                data_list.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return data_list

# ===================== SESSION STATE =====================
if 'serial_reader' not in st.session_state:
    st.session_state.serial_reader = SerialReader()
if 'history' not in st.session_state:
    st.session_state.history = {
        'timestamps': deque(maxlen=MAX_DATA_POINTS),
        'temperature': deque(maxlen=MAX_DATA_POINTS),
        'humidity': deque(maxlen=MAX_DATA_POINTS),
        'dustbin': deque(maxlen=MAX_DATA_POINTS),
        'score': deque(maxlen=MAX_DATA_POINTS)
    }
if 'latest_data' not in st.session_state:
    st.session_state.latest_data = {
        'temperature': 25.0,
        'humidity': 50.0,
        'dustbin': 0,
        'person': 0,
        'daynight': 1,
        'fan': 0,
        'score': 100,
        'status': 'Excellent'
    }
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = "Disconnected"

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("🔌 Connection Settings")
    
    ports = serial.tools.list_ports.comports()
    port_options = [p.device for p in ports] if ports else ["COM3", "COM4", "/dev/ttyUSB0", "/dev/ttyACM0"]
    selected_port = st.selectbox("Select Serial Port", port_options)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect", type="primary"):
            reader = st.session_state.serial_reader
            reader.stop()
            if reader.connect(selected_port):
                reader.start()
                st.session_state.connection_status = f"Connected to {selected_port}"
                st.success("Connected!")
            else:
                st.session_state.connection_status = "Failed"
                st.error("Connection failed")
    with col2:
        if st.button("Disconnect"):
            st.session_state.serial_reader.stop()
            st.session_state.connection_status = "Disconnected"
            st.info("Disconnected")
    
    st.markdown(f"**Status:** {st.session_state.connection_status}")
    
    st.header("📊 Settings")
    refresh_rate = st.slider("Refresh Rate (seconds)", 1, 10, 2)
    
    st.header("ℹ️ About")
    st.markdown("""
    **EcoSmart AI Bus Stand**
    
    Green Energy Monitoring System
    
    - DHT11: Temperature & Humidity
    - HC-SR04: Dustbin Level
    - IR Sensor: Passenger Detection
    - LDR: Day/Night Detection
    - Relay: Fan Control
    - Traffic Light: Status Indicator
    """)

# ===================== MAIN DASHBOARD =====================
st.markdown('<div class="main-header">🚌 EcoSmart AI Bus Stand</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Green Energy Smart Monitoring System</div>', unsafe_allow_html=True)

# Read new data from serial
reader = st.session_state.serial_reader
new_data_list = reader.get_data()
if new_data_list:
    st.session_state.latest_data = new_data_list[-1]
    for d in new_data_list:
        ts = time.strftime("%H:%M:%S")
        st.session_state.history['timestamps'].append(ts)
        st.session_state.history['temperature'].append(d['temperature'])
        st.session_state.history['humidity'].append(d['humidity'])
        st.session_state.history['dustbin'].append(d['dustbin'])
        st.session_state.history['score'].append(d['score'])

data = st.session_state.latest_data

# ===================== METRICS ROW =====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌡️ Temperature", f"{data['temperature']:.1f} °C", "DHT11")
    
with col2:
    st.metric("💧 Humidity", f"{data['humidity']:.1f} %", "DHT11")
    
with col3:
    dustbin_status = "🔴 Full" if data['dustbin'] >= 80 else ("🟡 Medium" if data['dustbin'] >= 50 else "🟢 Low")
    st.metric("🗑️ Dustbin Level", f"{data['dustbin']}%", dustbin_status)
    
with col4:
    person_status = "👤 Present" if data['person'] else "❌ None"
    st.metric("🚶 Passenger", person_status, "IR Sensor")

# ===================== STATUS ROW =====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    day_status = "☀️ Day" if data['daynight'] else "🌙 Night"
    st.metric("🌗 Day/Night", day_status, "LDR Sensor")
    
with col2:
    fan_status = "💨 ON" if data['fan'] else "⏹️ OFF"
    st.metric("🌀 Fan Status", fan_status, "Relay Control")
    
with col3:
    relay_status = "🔌 ACTIVE" if data['fan'] else "⏸️ IDLE"
    st.metric("⚡ Relay", relay_status, "LOW Trigger")
    
with col4:
    traffic_map = {"GREEN": "🟢 GREEN", "YELLOW": "🟡 YELLOW", "RED": "🔴 RED", "Excellent": "🟢 GREEN", "Good": "🟡 YELLOW", "Poor": "🔴 RED"}
    traffic_display = traffic_map.get(data['status'], "🟢 GREEN")
    st.metric("🚦 Traffic Light", traffic_display, "Status Indicator")

# ===================== AI SCORE & RECOMMENDATION =====================
st.markdown("---")
score_col, rec_col = st.columns([1, 2])

with score_col:
    score = data['score']
    if score >= 80:
        status_class = "status-excellent"
        status_emoji = "🌟"
    elif score >= 50:
        status_class = "status-good"
        status_emoji = "⚡"
    else:
        status_class = "status-poor"
        status_emoji = "⚠️"
    
    st.markdown(f'<div class="{status_class}">{status_emoji} AI Green Score: {score}/100</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; margin-top:10px; font-size:1.1rem;"><b>Status: {data["status"]}</b></div>', unsafe_allow_html=True)
    
    energy_saving = score
    st.progress(energy_saving / 100)
    st.markdown(f'<div style="text-align:center;">Estimated Energy Saving: <b>{energy_saving}%</b></div>', unsafe_allow_html=True)

with rec_col:
    st.subheader("🤖 AI System Recommendation")
    
    if not data['person'] and data['fan']:
        rec_text = "No passenger detected. Fan turned OFF."
        rec_icon = "💡"
    elif data['temperature'] > 30 and data['person'] and data['fan']:
        rec_text = "High temperature detected. Fan ON for passenger comfort."
        rec_icon = "🌡️"
    elif data['dustbin'] >= 90:
        rec_text = "Dustbin almost full! Please empty immediately."
        rec_icon = "🚨"
    elif data['dustbin'] > 80:
        rec_text = "Dustbin over 80%. Schedule emptying soon."
        rec_icon = "⚠️"
    elif data['status'] == "Excellent":
        rec_text = "Energy Saving Excellent. System operating at optimal efficiency."
        rec_icon = "🌟"
    elif not data['daynight'] and not data['person']:
        rec_text = "Night mode. Bus stand inactive. Minimal energy consumption."
        rec_icon = "🌙"
    else:
        rec_text = "System operating within normal parameters."
        rec_icon = "✅"
    
    st.markdown(f'<div class="recommendation-box">{rec_icon} <b>{rec_text}</b></div>', unsafe_allow_html=True)

# ===================== LIVE CHARTS =====================
st.markdown("---")
st.subheader("📈 Live Sensor Charts")

hist = st.session_state.history
if len(hist['timestamps']) > 1:
    # Temperature Chart
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=list(hist['timestamps']),
        y=list(hist['temperature']),
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=6)
    ))
    fig_temp.add_hline(y=30, line_dash="dash", line_color="orange", annotation_text="Threshold 30°C")
    fig_temp.update_layout(
        title="Temperature Trend",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        height=300,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # Dustbin Chart
    fig_dust = go.Figure()
    fig_dust.add_trace(go.Bar(
        x=list(hist['timestamps']),
        y=list(hist['dustbin']),
        name='Dustbin %',
        marker_color=['#FF6B6B' if v >= 80 else '#FFD93D' if v >= 50 else '#6BCB77' for v in hist['dustbin']]
    ))
    fig_dust.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Critical 80%")
    fig_dust.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Warning 50%")
    fig_dust.update_layout(
        title="Dustbin Fill Level",
        xaxis_title="Time",
        yaxis_title="Fill Percentage (%)",
        height=300,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    # AI Score Chart
    fig_score = go.Figure()
    fig_score.add_trace(go.Scatter(
        x=list(hist['timestamps']),
        y=list(hist['score']),
        mode='lines+markers',
        name='AI Score',
        line=dict(color='#4ECDC4', width=2),
        fill='tozeroy',
        fillcolor='rgba(78, 205, 196, 0.2)',
        marker=dict(size=6)
    ))
    fig_score.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Excellent")
    fig_score.add_hline(y=50, line_dash="dash", line_color="orange", annotation_text="Good")
    fig_score.update_layout(
        title="AI Green Energy Score",
        xaxis_title="Time",
        yaxis_title="Score (0-100)",
        height=300,
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(fig_temp, use_container_width=True, key="temp_chart")
    with chart_col2:
        st.plotly_chart(fig_dust, use_container_width=True, key="dust_chart")
    
    st.plotly_chart(fig_score, use_container_width=True, key="score_chart")
else:
    st.info("⏳ Waiting for sensor data... Connect to Arduino and wait for data stream.")
    fig_empty = go.Figure()
    fig_empty.update_layout(
        title="Waiting for data...",
        height=300,
        template="plotly_white",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        annotations=[dict(text="Connect Arduino to see live charts", showarrow=False, font_size=16)]
    )
    st.plotly_chart(fig_empty, use_container_width=True, key="empty_chart")

# ===================== RAW DATA TABLE =====================
st.markdown("---")
with st.expander("📋 Raw Sensor Data"):
    st.json(data)
    
    if len(hist['timestamps']) > 0:
        import pandas as pd
        df_data = {
            'Time': list(hist['timestamps']),
            'Temperature': list(hist['temperature']),
            'Humidity': list(hist['humidity']),
            'Dustbin %': list(hist['dustbin']),
            'AI Score': list(hist['score'])
        }
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

# Auto-refresh
st.markdown("---")
st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')} | EcoSmart AI Bus Stand v1.0")

time.sleep(refresh_rate)
st.rerun()
