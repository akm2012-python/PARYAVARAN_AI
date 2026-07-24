"""
EcoSmart AI Bus Stand - Green Energy Dashboard
Python Streamlit Dashboard for Arduino Serial Data
With MQ-135 Air Quality Sensor Support

Requirements:
- Python 3.8+
- streamlit
- pyserial
- plotly
- pandas

Installation:
    pip install streamlit pyserial plotly pandas

Run:
    streamlit run dashboard.py

Serial Format from Arduino:
    temperature,humidity,dustbin,person,daynight,fan,score,status,airquality,airstatus,recommendation,buzzer,high_temp,mq135raw,airqualitypercent
"""

import serial
import serial.tools.list_ports
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time
import threading
import queue
from datetime import datetime
import json
import os

# ==================== CONFIGURATION ====================
SERIAL_BAUD = 9600
MAX_DATA_POINTS = 100
CSV_LOG_FILE = "ecosmart_data_log.csv"

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="EcoSmart AI Bus Stand - Green Energy Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
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
        color: #558B2F;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f8f0;
        border-radius: 10px;
        padding: 1rem;
        border-left: 5px solid #4CAF50;
    }
    .status-excellent {
        color: #2E7D32;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-good {
        color: #F9A825;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-poor {
        color: #C62828;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .recommendation-box {
        background-color: #E8F5E9;
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid #66BB6A;
        margin-top: 1rem;
    }
    .air-fresh { color: #2E7D32; font-weight: bold; }
    .air-moderate { color: #F9A825; font-weight: bold; }
    .air-unhealthy { color: #FF5722; font-weight: bold; }
    .air-hazardous { color: #C62828; font-weight: bold; }
    .traffic-green { color: #2E7D32; font-weight: bold; }
    .traffic-yellow { color: #F9A825; font-weight: bold; }
    .traffic-red { color: #C62828; font-weight: bold; }
    .fan-on { color: #1976D2; font-weight: bold; }
    .fan-off { color: #757575; }
    .day-mode { color: #FF8F00; }
    .night-mode { color: #3F51B5; }
    .person-yes { color: #2E7D32; }
    .person-no { color: #C62828; }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SERIAL READER CLASS ====================
class SerialReader:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.data_queue = queue.Queue()
        self.thread = None
        self.connected = False
        self.port_name = None

    def list_ports(self):
        """List available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    def connect(self, port, baudrate=SERIAL_BAUD):
        """Connect to serial port"""
        try:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            time.sleep(2)
            self.serial_port.flushInput()
            self.is_running = True
            self.connected = True
            self.port_name = port
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            st.error(f"Failed to connect to {port}: {str(e)}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from serial port"""
        self.is_running = False
        self.connected = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def _read_loop(self):
        """Background thread to read serial data"""
        while self.is_running and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line and not line.startswith("EcoSmart") and not line.startswith("Format"):
                        self.data_queue.put(line)
                time.sleep(0.05)
            except Exception as e:
                time.sleep(0.1)

    def get_data(self):
        """Get latest data from queue"""
        data_lines = []
        while not self.data_queue.empty():
            try:
                data_lines.append(self.data_queue.get_nowait())
            except queue.Empty:
                break
        return data_lines

    def send_command(self, command):
        """Send command to Arduino"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(f"{command}\n".encode())

# ==================== DATA PARSER ====================
def parse_serial_data(line):
    """Parse CSV data from Arduino
    Format: temperature,humidity,dustbin,person,daynight,fan,score,status,airquality,airstatus,recommendation,buzzer,high_temp,mq135raw,airqualitypercent
    """
    try:
        parts = line.split(',')
        if len(parts) >= 11:
            return {
                'timestamp': datetime.now(),
                'temperature': float(parts[0]),
                'humidity': float(parts[1]),
                'dustbin': float(parts[2]),
                'person': int(parts[3]),
                'daynight': int(parts[4]),
                'fan': int(parts[5]),
                'score': int(parts[6]),
                'status': parts[7],
                'airquality': float(parts[8]) if len(parts) > 8 else 0.0,
                'airstatus': parts[9] if len(parts) > 9 else "Unknown",
                'recommendation': parts[10] if len(parts) > 10 else "",
                'buzzer': int(parts[11]) if len(parts) > 11 else 0,
                'high_temp': int(parts[12]) if len(parts) > 12 else 0,
                'mq135raw': int(parts[13]) if len(parts) > 13 else 0,
                'airqualitypercent': int(parts[14]) if len(parts) > 14 else 100
            }
    except Exception as e:
        pass
    return None

# ==================== INITIALIZE SESSION STATE ====================
if 'serial_reader' not in st.session_state:
    st.session_state.serial_reader = SerialReader()
if 'data_history' not in st.session_state:
    st.session_state.data_history = []
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'selected_port' not in st.session_state:
    st.session_state.selected_port = None
if 'auto_scroll' not in st.session_state:
    st.session_state.auto_scroll = True

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## Connection Settings")

    available_ports = st.session_state.serial_reader.list_ports()

    if available_ports:
        selected_port = st.selectbox(
            "Select Serial Port:",
            available_ports,
            index=0 if st.session_state.selected_port is None else available_ports.index(st.session_state.selected_port) if st.session_state.selected_port in available_ports else 0
        )
    else:
        st.warning("No serial ports detected!")
        selected_port = None

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Connect", type="primary", disabled=(selected_port is None)):
            if st.session_state.serial_reader.connect(selected_port):
                st.session_state.connected = True
                st.session_state.selected_port = selected_port
                st.success(f"Connected to {selected_port}")
                time.sleep(1)
                st.rerun()

    with col2:
        if st.button("Disconnect"):
            st.session_state.serial_reader.disconnect()
            st.session_state.connected = False
            st.session_state.selected_port = None
            st.info("Disconnected")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    st.markdown("### Dashboard Settings")
    st.session_state.auto_scroll = st.checkbox("Auto-scroll Charts", value=st.session_state.auto_scroll)

    if st.button("Clear Data"):
        st.session_state.data_history = []
        st.success("Data cleared!")
        time.sleep(0.5)
        st.rerun()

    st.markdown("---")
    st.markdown("### Data Export")
    if st.session_state.data_history:
        df_export = pd.DataFrame(st.session_state.data_history)
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=CSV_LOG_FILE,
            mime="text/csv"
        )

    st.markdown("---")
    st.markdown("### System Info")
    st.markdown(f"**Status:** {'Connected' if st.session_state.connected else 'Disconnected'}")
    if st.session_state.connected:
        st.markdown(f"**Port:** {st.session_state.selected_port}")
    st.markdown(f"**Data Points:** {len(st.session_state.data_history)}")
    st.markdown(f"**Baud Rate:** {SERIAL_BAUD}")

# ==================== MAIN DASHBOARD ====================
st.markdown('<div class="main-header">EcoSmart AI Bus Stand</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Green Energy Monitoring Dashboard with Air Quality</div>', unsafe_allow_html=True)

# Read new data from serial
if st.session_state.connected:
    new_lines = st.session_state.serial_reader.get_data()
    for line in new_lines:
        parsed = parse_serial_data(line)
        if parsed:
            st.session_state.data_history.append(parsed)
            if len(st.session_state.data_history) > MAX_DATA_POINTS:
                st.session_state.data_history = st.session_state.data_history[-MAX_DATA_POINTS:]

# Get latest data
latest_data = st.session_state.data_history[-1] if st.session_state.data_history else None

# ==================== TOP METRICS ROW ====================
if latest_data:
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Temperature", f"{latest_data['temperature']:.1f}C")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Humidity", f"{latest_data['humidity']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Dustbin Fill", f"{latest_data['dustbin']:.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        fan_text = "ON" if latest_data['fan'] else "OFF"
        st.metric("Fan Status", fan_text)
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        score = latest_data['score']
        st.metric("AI Score", f"{score}/100")
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        aq = latest_data['airquality']
        st.metric("Air Quality", f"{aq:.0f} PPM")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ==================== STATUS ROW ====================
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("#### Passenger Detection")
        if latest_data['person']:
            st.markdown('<div class="person-yes">PERSON DETECTED</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="person-no">NO PERSON</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Day/Night Status")
        if latest_data['daynight']:
            st.markdown('<div class="day-mode">DAYTIME</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="night-mode">NIGHTTIME</div>', unsafe_allow_html=True)

    with col3:
        st.markdown("#### Traffic Light")
        dustbin = latest_data['dustbin']
        if dustbin < 50:
            st.markdown('<div class="traffic-green">GREEN (Excellent)</div>', unsafe_allow_html=True)
        elif dustbin < 80:
            st.markdown('<div class="traffic-yellow">YELLOW (Moderate)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="traffic-red">RED (Critical)</div>', unsafe_allow_html=True)

    with col4:
        st.markdown("#### Buzzer Status")
        if latest_data['buzzer']:
            st.markdown('<div class="status-poor">BUZZER ACTIVE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: #757575;">Buzzer OFF</div>', unsafe_allow_html=True)

    with col5:
        st.markdown("#### Air Quality")
        airstatus = latest_data['airstatus']
        if airstatus == "Fresh Air":
            st.markdown('<div class="air-fresh">FRESH AIR</div>', unsafe_allow_html=True)
        elif airstatus == "Moderate":
            st.markdown('<div class="air-moderate">MODERATE</div>', unsafe_allow_html=True)
        elif airstatus == "Unhealthy":
            st.markdown('<div class="air-unhealthy">UNHEALTHY</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="air-hazardous">HAZARDOUS</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ==================== AI SCORE & RECOMMENDATION ====================
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Green AI Score")
        score = latest_data['score']

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "AI Score", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#4CAF50" if score >= 80 else "#FFC107" if score >= 50 else "#F44336"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': '#FFEBEE'},
                    {'range': [50, 80], 'color': '#FFF8E1'},
                    {'range': [80, 100], 'color': '#E8F5E9'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

        status = latest_data['status']
        if status == "Excellent":
            st.markdown(f'<div class="status-excellent">Status: {status}</div>', unsafe_allow_html=True)
        elif status == "Good":
            st.markdown(f'<div class="status-good">Status: {status}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-poor">Status: {status}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### System Recommendation")
        st.markdown(f'<div class="recommendation-box">{latest_data["recommendation"]}</div>', unsafe_allow_html=True)

        st.markdown("### Estimated Energy Saving")
        energy_saving = latest_data['score']
        st.progress(energy_saving / 100)
        st.markdown(f"**{energy_saving}%** Energy Efficiency Achieved")

        st.markdown("### System Summary")
        summary_col1, summary_col2 = st.columns(2)
        with summary_col1:
            st.markdown(f"- Temperature: **{latest_data['temperature']:.1f}C**")
            st.markdown(f"- Humidity: **{latest_data['humidity']:.1f}%**")
            st.markdown(f"- Dustbin: **{latest_data['dustbin']:.1f}%**")
            st.markdown(f"- Air Quality: **{latest_data['airquality']:.0f} PPM**")
        with summary_col2:
            st.markdown(f"- Passenger: **{'Yes' if latest_data['person'] else 'No'}**")
            st.markdown(f"- Day/Night: **{'Day' if latest_data['daynight'] else 'Night'}**")
            st.markdown(f"- Fan: **{'ON' if latest_data['fan'] else 'OFF'}**")
            st.markdown(f"- Air Status: **{latest_data['airstatus']}**")

    st.markdown("---")

    # ==================== LIVE CHARTS ====================
    st.markdown("### Live Sensor Charts")

    if len(st.session_state.data_history) >= 2:
        df = pd.DataFrame(st.session_state.data_history)
        df['time_str'] = df['timestamp'].dt.strftime('%H:%M:%S')

        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Temperature (C)', 'Dustbin Fill Level (%)', 'AI Green Score'),
            vertical_spacing=0.1,
            row_heights=[0.33, 0.33, 0.34]
        )

        # Temperature chart
        fig.add_trace(
            go.Scatter(
                x=df['time_str'],
                y=df['temperature'],
                mode='lines+markers',
                name='Temperature',
                line=dict(color='#FF5722', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(255, 87, 34, 0.1)'
            ),
            row=1, col=1
        )

        fig.add_hline(y=30, line_dash="dash", line_color="red", 
                      annotation_text="Threshold (30C)", row=1, col=1)

        # Dustbin chart
        colors = []
        for val in df['dustbin']:
            if val < 50:
                colors.append('#4CAF50')
            elif val < 80:
                colors.append('#FFC107')
            else:
                colors.append('#F44336')

        fig.add_trace(
            go.Scatter(
                x=df['time_str'],
                y=df['dustbin'],
                mode='lines+markers',
                name='Dustbin %',
                line=dict(color='#2196F3', width=2),
                marker=dict(size=6, color=colors),
                fill='tozeroy',
                fillcolor='rgba(33, 150, 243, 0.1)'
            ),
            row=2, col=1
        )

        fig.add_hline(y=50, line_dash="dash", line_color="green", 
                      annotation_text="Green Limit", row=2, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                      annotation_text="Yellow Limit", row=2, col=1)
        fig.add_hline(y=90, line_dash="dash", line_color="red", 
                      annotation_text="Red Limit", row=2, col=1)

        # AI Score chart
        score_colors = []
        for val in df['score']:
            if val >= 80:
                score_colors.append('#4CAF50')
            elif val >= 50:
                score_colors.append('#FFC107')
            else:
                score_colors.append('#F44336')

        fig.add_trace(
            go.Scatter(
                x=df['time_str'],
                y=df['score'],
                mode='lines+markers',
                name='AI Score',
                line=dict(color='#9C27B0', width=2),
                marker=dict(size=6, color=score_colors),
                fill='tozeroy',
                fillcolor='rgba(156, 39, 176, 0.1)'
            ),
            row=3, col=1
        )

        fig.add_hline(y=80, line_dash="dash", line_color="green", 
                      annotation_text="Excellent", row=3, col=1)
        fig.add_hline(y=50, line_dash="dash", line_color="orange", 
                      annotation_text="Good", row=3, col=1)

        fig.update_layout(
            height=700,
            showlegend=False,
            template='plotly_white',
            margin=dict(l=50, r=50, t=80, b=50)
        )

        fig.update_xaxes(tickangle=45, nticks=10)
        fig.update_yaxes(range=[0, 60], row=1, col=1)
        fig.update_yaxes(range=[0, 105], row=2, col=1)
        fig.update_yaxes(range=[0, 105], row=3, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Air Quality Chart
        st.markdown("### Air Quality Chart")
        fig_aq = go.Figure()

        aq_colors = []
        for val in df['airquality']:
            if val < 150:
                aq_colors.append('#4CAF50')
            elif val < 350:
                aq_colors.append('#FFC107')
            elif val < 550:
                aq_colors.append('#FF5722')
            else:
                aq_colors.append('#F44336')

        fig_aq.add_trace(
            go.Scatter(
                x=df['time_str'],
                y=df['airquality'],
                mode='lines+markers',
                name='Air Quality (PPM)',
                line=dict(color='#795548', width=2),
                marker=dict(size=6, color=aq_colors),
                fill='tozeroy',
                fillcolor='rgba(121, 85, 72, 0.1)'
            )
        )

        fig_aq.add_hline(y=150, line_dash="dash", line_color="green", annotation_text="Fresh")
        fig_aq.add_hline(y=350, line_dash="dash", line_color="orange", annotation_text="Moderate")
        fig_aq.add_hline(y=550, line_dash="dash", line_color="red", annotation_text="Hazardous")

        fig_aq.update_layout(
            height=300,
            template='plotly_white',
            yaxis_title='Air Quality (PPM)',
            xaxis_title='Time',
            margin=dict(l=50, r=50, t=30, b=50)
        )
        fig_aq.update_xaxes(tickangle=45, nticks=10)
        st.plotly_chart(fig_aq, use_container_width=True)

        # Humidity Chart
        st.markdown("### Humidity Chart")
        fig_hum = go.Figure()
        fig_hum.add_trace(
            go.Scatter(
                x=df['time_str'],
                y=df['humidity'],
                mode='lines+markers',
                name='Humidity',
                line=dict(color='#00BCD4', width=2),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(0, 188, 212, 0.1)'
            )
        )
        fig_hum.update_layout(
            height=300,
            template='plotly_white',
            yaxis_title='Humidity (%)',
            xaxis_title='Time',
            margin=dict(l=50, r=50, t=30, b=50)
        )
        fig_hum.update_xaxes(tickangle=45, nticks=10)
        st.plotly_chart(fig_hum, use_container_width=True)

    else:
        st.info("Collecting data... Please wait for more data points to display charts.")

    st.markdown("---")

    # ==================== DATA TABLE ====================
    st.markdown("### Recent Data Log")
    if st.session_state.data_history:
        df_display = pd.DataFrame(st.session_state.data_history)
        df_display['Time'] = df_display['timestamp'].dt.strftime('%H:%M:%S')
        df_display = df_display[['Time', 'temperature', 'humidity', 'dustbin', 'person', 
                                'daynight', 'fan', 'score', 'status', 'airquality', 'airstatus', 'recommendation']]
        df_display.columns = ['Time', 'Temp(C)', 'Humidity(%)', 'Dustbin(%)', 'Passenger', 
                             'Day/Night', 'Fan', 'AI Score', 'Status', 'AirQ(PPM)', 'Air Status', 'Recommendation']

        df_display['Passenger'] = df_display['Passenger'].map({1: 'Yes', 0: 'No'})
        df_display['Day/Night'] = df_display['Day/Night'].map({1: 'Day', 0: 'Night'})
        df_display['Fan'] = df_display['Fan'].map({1: 'ON', 0: 'OFF'})

        st.dataframe(df_display.tail(20), use_container_width=True, hide_index=True)

else:
    # Not connected state
    st.warning("Not connected to Arduino. Please connect to a serial port from the sidebar.")

    st.markdown("""
    ### Getting Started

    1. **Upload the Arduino code** to your Arduino UNO
    2. **Connect the Arduino** via USB to your laptop
    3. **Select the serial port** from the sidebar (e.g., COM3, COM4 on Windows or /dev/ttyUSB0 on Linux)
    4. **Click Connect** to start monitoring

    ### Expected Serial Format
    ```
    temperature,humidity,dustbin,person,daynight,fan,score,status,airquality,airstatus,recommendation,buzzer,high_temp,mq135raw,airqualitypercent
    ```

    ### Hardware Checklist
    - Arduino UNO
    - HC-SR04 Ultrasonic Sensor
    - DHT11 Temperature & Humidity Sensor
    - IR Obstacle Sensor
    - LDR Module
    - Traffic Light Module
    - 2-Channel Relay Module
    - 5V DC Motor (Fan)
    - TMB12A05 Active Buzzer
    - MQ-135 Air Quality Sensor
    - Breadboard & Jumper Wires
    - 5V 1A Power Adapter
    """)

    # Show demo placeholder
    st.markdown("---")
    st.markdown("### Demo Preview")

    demo_col1, demo_col2, demo_col3, demo_col4, demo_col5, demo_col6 = st.columns(6)
    demo_col1.metric("Temperature", "28.5C")
    demo_col2.metric("Humidity", "65.0%")
    demo_col3.metric("Dustbin Fill", "45.0%")
    demo_col4.metric("Fan Status", "OFF")
    demo_col5.metric("AI Score", "95/100")
    demo_col6.metric("Air Quality", "85 PPM")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>EcoSmart AI Bus Stand - Green Energy System with Air Quality | Built with Streamlit & Plotly</div>", unsafe_allow_html=True)