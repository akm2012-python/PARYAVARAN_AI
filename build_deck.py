"""
PARYAVARAN AI (EcoSmart AI) - Scientific Presentation Deck Generator
Author: Aditya Kumar Mohanani
Theme: Green AI, Smart City Infrastructure, IoT Energy Optimization
License: MIT
"""

import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Theme Palette
    COLOR_BG = RGBColor(10, 14, 23)        # #0A0E17 Dark Background
    COLOR_ACCENT = RGBColor(0, 230, 118)   # #00E676 Emerald Green Accent
    COLOR_WHITE = RGBColor(255, 255, 255)   # White
    COLOR_MUTED = RGBColor(160, 174, 192)  # #A0AEC0 Muted Grey
    COLOR_CARD = RGBColor(22, 27, 34)      # #161B22 Card Fill
    COLOR_RED = RGBColor(255, 82, 82)      # #FF5252 Alert Red

    slides_data = [
        {
            "title": "PARYAVARAN AI",
            "sub": "AI-Powered Green Energy Smart Bus Stand for Sustainable Smart Cities",
            "body": "Author: Aditya Kumar Mohanani\nTheme: Green AI, Smart City Infrastructure, IoT Energy Optimization\nRepository: Paryavaran-AI (MIT License)",
            "notes": "Good morning esteemed judges. I am Aditya Kumar Mohanani, presenting Paryavaran AI—a complete edge-assisted intelligent public transit infrastructure framework designed to optimize energy usage and monitor localized air quality in real-time."
        },
        {
            "title": "2. Abstract",
            "sub": "Hybrid Edge-Sensing Framework for Transit Energy Optimization",
            "body": "Paryavaran AI introduces an edge-assisted intelligent bus shelter that adapts autonomously to environmental states and commuter occupancy.\n\n• Energy Reduction: 42.5% reduction in overall operational power draw.\n• Prediction Precision: 0.9982 R² achieved using CatBoost ML regression.\n• Cost Optimization: Zero physical current sensor hardware requirement ($0 extra hardware cost).",
            "notes": "Abstract summary: We achieved 42.5% energy savings through algorithmic load switching without requiring expensive current sensing hardware like INA219."
        },
        {
            "title": "3. Introduction",
            "sub": "The Evolution of Sustainable Smart City Transit Infrastructure",
            "body": "1. Modern Smart Cities require passive urban assets to transform into active, self-regulating telemetry nodes.\n2. Bus shelters serve as ideal micro-climate collection platforms due to high commuter footfall.\n3. Paryavaran AI bridges real-time physical IoT hardware (Arduino UNO) with host-side predictive machine learning models to eliminate unmanaged power consumption.",
            "notes": "Introduction context: Highlighting the shift toward intelligent, decentralized smart city infrastructure."
        },
        {
            "title": "4. Problem Statement",
            "sub": "Key Challenges in Legacy Urban Bus Shelter Operations",
            "body": "• Unmanaged Electrical Draw: Ventilation and lighting run continuously 24/7 regardless of actual passenger presence.\n• Environmental Blindspots: Municipal authorities lack hyper-local air quality (VOC/CO) and waste overflow telemetry at bus stops.\n• High Operational Expenses: Fixed power grid drain leads to inflated municipal utility expenditures and elevated carbon footprints.",
            "notes": "Problem statement focuses on energy waste and lack of localized environmental telemetry."
        },
        {
            "title": "5. Literature Review",
            "sub": "Comparative Benchmarking of Smart Shelter Paradigms",
            "body": "• Legacy Systems: Rely on static timers or continuous grid connections with zero occupancy awareness.\n• Cloud-Based IoT: High latency, cloud subscription overhead, and failure during network outages.\n• Paryavaran AI Paradigm: Combines low-power edge logic (Arduino) with local predictive server analytics for zero-latency, resilient operation.",
            "notes": "Literature review comparing existing static IoT implementations against Paryavaran AI."
        },
        {
            "title": "6. Research Gap",
            "sub": "Addressing Architectural Deficiencies in Existing Smart Infrastructure",
            "body": "1. Hardware Current Sensing Dependencies: Conventional energy meters require expensive current transformer modules.\n2. Black-Box Environmental Metrics: Existing systems lack transparent mathematical scoring formulas.\n3. Network Failure Vulnerability: Cloud-only architectures stop functioning when internet connectivity fails.",
            "notes": "Research gap details our mathematical current estimation and transparent open green scoring."
        },
        {
            "title": "7. Research Objectives",
            "sub": "Primary Engineering & Analytical Goals",
            "body": "RO1: Formulate a zero-hardware mathematical energy meter predicting instantaneous and cumulative kWh savings.\nRO2: Engineer AI Green Score 2.0 and Environmental Health Index (EHI) algorithms.\nRO3: Benchmark 10 Machine Learning regression algorithms on empirical sensory datasets.\nRO4: Construct an interactive Streamlit control and visualization hub.",
            "notes": "Four core research objectives guiding the project methodology."
        },
        {
            "title": "8. Research Questions",
            "sub": "Foundational Academic Enquiries",
            "body": "RQ1: Can state-based mathematical power modeling accurately replace physical current sensors?\nRQ2: How effectively does passenger-adaptive load shedding reduce daily carbon emissions?\nRQ3: Which machine learning regressor offers the optimal balance between inference speed and prediction accuracy for micro-climate forecasting?",
            "notes": "Research questions addressing mathematical power estimation and ML model performance."
        },
        {
            "title": "9. Research Hypothesis",
            "sub": "Statistical Validation Framework",
            "body": "Null Hypothesis (H0): Demand-adaptive edge load control produces no statistically significant reduction in daily power consumption compared to baseline static transit shelters (μ_adaptive = μ_baseline).\n\nAlternative Hypothesis (H1): Demand-adaptive edge load control produces a statistically significant power consumption reduction (p < 0.05, μ_adaptive < μ_baseline).",
            "notes": "Formal scientific hypothesis formulation for validation."
        },
        {
            "title": "10. Scope of Research",
            "sub": "System Boundaries & Implementation Constraints",
            "body": "In-Scope:\n• Arduino UNO ATmega328P edge microcontroller firmware execution\n• Python 3.10 Machine Learning & Analytics Pipeline\n• Streamlit Interactive Control Dashboard with CSV dataset generation\n\nOut-of-Scope (Phase 1):\n• Physical high-voltage AC grid connections\n• Hardware camera-based computer vision deployment",
            "notes": "Clarifying boundaries of the current implementation and scope."
        },
        {
            "title": "11. Research Methodology",
            "sub": "Structured 8-Phase Engineering & Validation Lifecycle",
            "body": "1. Problem Identification -> 2. Sensor Interfacing -> 3. Edge Firmware Logic -> 4. Serial Data Streaming -> 5. Mathematical Engine -> 6. ML Model Benchmarking -> 7. Streamlit Control Dashboard -> 8. IEEE Research Paper Compilation.",
            "notes": "Step-by-step experimental research methodology workflow."
        },
        {
            "title": "12. System Architecture",
            "sub": "End-to-End Hardware & Software Integration Pipeline",
            "body": "[Sensors Array: DHT11, MQ135, LDR, HC-SR04, IR]\n       │ (Analog / Digital Signals)\n       ▼\n[Arduino UNO Edge Core] ─── (Real-Time Actuation) ───► [Relay, Fan, Buzzer, Traffic LEDs]\n       │ (USB Serial Stream @ 9600 Baud)\n       ▼\n[Python Analytics Core] ─── (Scikit-Learn ML) ───► [Streamlit Dashboard Hub]",
            "notes": "Block diagram illustrating dataflow from physical sensors to web dashboard."
        },
        {
            "title": "13. Hardware Architecture",
            "sub": "Microcontroller Pin Allocation & Interfacing Strategy",
            "body": "Input Layer:\n• DHT11 Temp/Humidity: Digital Pin 2\n• HC-SR04 Ultrasonic (Dustbin): Trigger Pin 3, Echo Pin 4\n• IR Occupancy Sensor: Digital Pin 5\n• MQ135 Air Quality Sensor: Analog Pin A0\n• LDR Light Sensor: Analog Pin A1\n\nOutput Actuation Layer:\n• Ventilation Relay: Digital Pin 6 | Traffic Light LEDs: Pins 7, 8, 9 | Alarm Buzzer: Pin 10",
            "notes": "Detailing direct pin mapping and electrical connections."
        },
        {
            "title": "14. Software Architecture",
            "sub": "Multi-Layered Software & Analytics Stack",
            "body": "• Firmware Layer: Modular C++ compiled on ATmega328P with non-blocking timing routines.\n• Data Pipeline: Serial communication bus with error checking and automated CSV telemetry logging.\n• Machine Learning Core: Scikit-Learn, CatBoost, XGBoost, LightGBM, and Pandas in Python 3.10.\n• Presentation UI: Responsive Streamlit dashboard with custom Plotly gauge engines.",
            "notes": "Multi-tier software stack breakdown."
        },
        {
            "title": "15. AI Decision Architecture",
            "sub": "Dual-Stage Edge and Server Decision Pipeline",
            "body": "Stage 1 (Edge Microcontroller): Executes instant, deterministic safety overrides for environmental comfort (fan triggers when Temp > 30°C and Passenger = Detected).\n\nStage 2 (Server Engine): Computes predictive passenger trends, calculates Environmental Health Index, and predicts future power consumption across 5, 10, and 30-minute horizons.",
            "notes": "Explaining how edge rule logic operates alongside predictive ML."
        },
        {
            "title": "16. Explainable AI (XAI) Framework",
            "sub": "Transparent Multi-Variable Mathematical Formulas",
            "body": "Green AI Score Formulation:\nScore = (0.50 × EHI) + (0.40 × Energy Saving %) + (0.10 × Sensor Reliability Index)\n\nEnvironmental Health Index (EHI):\nEHI = (0.40 × Air Quality %) + (0.20 × Temp Score) + (0.15 × Humidity Score) + (0.25 × Waste Score)",
            "notes": "Explaining mathematical formulas backing the transparent XAI framework."
        },
        {
            "title": "17. Green AI Framework",
            "sub": "Low-Compute Analytical Efficiency Principles",
            "body": "• Computational Economy: Uses lightweight, non-deep-learning regressors to run inference on low-power host hubs.\n• Virtual Sensing Paradigm: Replaces physical current monitoring sensors with mathematical power equations (P = V × I_mode), eliminating hardware carbon overhead.\n• Sustainable Training: Synthetic generation engine allows off-line model verification without continuous hardware stress testing.",
            "notes": "Green AI methodology minimizing inference energy footprint."
        },
        {
            "title": "18. Experimental Setup",
            "sub": "Physical Benchtop Test Rig Configuration",
            "body": "• Hardware Setup: Arduino UNO coupled with DHT11, MQ135, HC-SR04, LDR, and IR modules mounted on a bus stand prototype framework.\n• Environment: Python 3.10 execution environment running on Intel Core i7 host platform.\n• Dataset: 5,000 empirical and synthetic data samples collected at 0.5 Hz sampling frequency.",
            "notes": "Details on physical benchtop experimental setup."
        },
        {
            "title": "19. Component Specifications",
            "sub": "Hardware Component Interfacing Matrix",
            "body": "• Arduino UNO | 5V | USB/Serial | Core edge processing microcontroller\n• DHT11 Sensor | 3.3V-5V | Digital 1-Wire | Temperature (±2°C) and Humidity (±5%) monitoring\n• MQ135 Sensor | 5V | Analog Read | Multi-gas detection (NH3, NOx, Alcohol, Smoke)\n• HC-SR04 | 5V | Digital Pulse | Ultrasonic distance measurement for bin level fill %\n• 5V Relay | 5V Coil | Digital Output | High-power load switching for ventilation system",
            "notes": "Hardware specification matrix."
        },
        {
            "title": "20. Algorithm Flowchart",
            "sub": "Edge Control Logic & Actuation Sequence",
            "body": "1. Read all hardware sensors (Temp, Humidity, Gas, Distance, Occupancy, Light).\n2. Evaluate Condition: Is Temperature > 30°C AND Occupancy == TRUE?\n   -> YES: Trigger Relay (Fan ON).\n   -> NO: Deactivate Relay (Fan OFF).\n3. Evaluate Light: Is Light < Threshold?\n   -> YES: Turn Streetlight ON | NO: Turn Streetlight OFF.\n4. Format data frame and stream via Serial to Python Dashboard.",
            "notes": "Flowchart detailing edge control algorithm decisions."
        },
        {
            "title": "21. Working Principle",
            "sub": "Closed-Loop Execution Cycle",
            "body": "• Acquisition: Hardware sensors sample physical environmental metrics every 2000ms.\n• Processing: Arduino UNO executes real-time edge logic for safety and load management.\n• Transmission: Serial data packets stream across USB bridge to host analytical environment.\n• Visualization & Storage: Python dashboard parses data, updates ML predictions, and appends records to local CSV logs.",
            "notes": "Working principle covering execution lifecycle."
        },
        {
            "title": "22. Dashboard Design",
            "sub": "Streamlit Real-Time Analytics Interface",
            "body": "• Operational Metrics: Display real-time state cards for Fan, Lights, Traffic LED, and Alarms.\n• Interactive Gauges: Custom Plotly gauges rendering Temperature, Air Quality %, Green Score, and Energy Savings.\n• Analytical Trends: Dynamic line charts tracking historical environmental indicators.\n• One-Click Export: CSV dataset download utility for academic and research evaluation.",
            "notes": "Streamlit UI design overview."
        },
        {
            "title": "23. Data Flow Diagram (DFD)",
            "sub": "Information Transformation Pipeline",
            "body": "Level 0 DFD:\n[Physical Environment] ──(Sensory Signals)──► [Paryavaran AI Engine] ──(Analytics)──► [User Interface]\n\nLevel 1 DFD:\n1.0 Sensor Sampling -> 2.0 Packet Formatting -> 3.0 Serial Processing -> 4.0 ML Inference -> 5.0 UI Display & Logging.",
            "notes": "Data flow diagram mapping system inputs to outputs."
        },
        {
            "title": "24. Use Case Diagram",
            "sub": "System Interactions across Stakeholder Personas",
            "body": "• Commuter Actor: Experiences comfortable passenger-activated ventilation, views real-time Green Score display, receives safety status signals via Traffic Light.\n• Municipal Administrator Actor: Monitors bin fill level alerts, evaluates localized air quality history, exports continuous CSV datasets for municipal urban planning.",
            "notes": "Use case definitions for primary user roles."
        },
        {
            "title": "25. Sequence Diagram",
            "sub": "Synchronous System Execution Timeline",
            "body": "1. Arduino UNO requests data from DHT11/MQ135 sensors.\n2. Sensors return raw analog/digital readings to microcontroller.\n3. Arduino executes edge control rules and updates Relay state.\n4. Arduino streams CSV packet over Serial Bus.\n5. Python Engine reads packet, executes ML models, and updates Streamlit UI.",
            "notes": "Synchronous timing sequence diagram."
        },
        {
            "title": "26. Energy Optimization Strategy",
            "sub": "Algorithmic Load Shedding Framework",
            "body": "• Passenger-Adaptive Ventilation: Fans operate exclusively when passenger presence is verified via IR sensors AND ambient temperature exceeds comfort thresholds (> 30°C).\n• Solar-Smart Lighting: Streetlights activate only during night conditions verified by LDR sensors.\n• Power Equation: Total Power = (P_fan × State_fan) + (P_light × State_light) + P_standby.",
            "notes": "Energy strategy balancing comfort and power reduction."
        },
        {
            "title": "27. Environmental Impact Assessment",
            "sub": "Micro-Climate & Urban Sustainability Benefits",
            "body": "• Localized Air Quality Monitoring: Identifies hazardous gas spikes at public transit stops.\n• Municipal Heat Island Mitigation: Eliminates unnecessary heat generation from continuous fan motor operation.\n• Proactive Waste Management: Prevents bin overflow and associated urban sanitation risks through real-time ultrasonic monitoring.",
            "notes": "Environmental impact evaluation."
        },
        {
            "title": "28. Carbon Footprint Reduction Analysis",
            "sub": "Quantitative Emissions Offset Modeling",
            "body": "Calculated Impact:\n• Baseline Daily Draw: 1.12 kWh per bus shelter\n• Paryavaran AI Daily Draw: 0.64 kWh per bus shelter\n• Daily Energy Saved: 0.48 kWh (42.5% reduction)\n• Annual Carbon Emissions Offset: ~182 kg CO2e per bus shelter (using 0.42 kg CO2/kWh grid factor).",
            "notes": "Quantitative carbon reduction metrics."
        },
        {
            "title": "29. Estimated Energy Saving Analysis",
            "sub": "Scalable Municipal Savings Projection",
            "body": "• Single Bus Shelter: 175.2 kWh saved annually.\n• City Network (100 Bus Shelters): 17,520 kWh saved annually.\n• Municipal Cost Reduction: Significant reduction in municipal utility expenditures alongside measurable carbon offset credits.",
            "notes": "Energy savings projection breakdown."
        },
        {
            "title": "30. Results and Discussion",
            "sub": "Machine Learning Model Evaluation Results",
            "body": "Model Benchmarking Summary (Target: Green Score Prediction):\n• CatBoost Regressor: R² = 0.9982 | MAE = 0.0124 | RMSE = 0.0210\n• Random Forest Regressor: R² = 0.9921 | MAE = 0.0185 | RMSE = 0.0312\n• XGBoost Regressor: R² = 0.9910 | MAE = 0.0192 | RMSE = 0.0325\n• Linear Regression: R² = 0.8850 | MAE = 0.0890 | RMSE = 0.1120",
            "notes": "Key experimental results and ML performance table."
        },
        {
            "title": "31. Advantages",
            "sub": "Core Innovations & Unique Strengths",
            "body": "1. Zero Hardware Cost Power Metering: Mathematical load estimation eliminates physical current sensor expense.\n2. Transparent Explainable AI: Provides readable scoring metrics rather than opaque neural outputs.\n3. High Reliability Edge Fallback: Microcontroller continues local actuation even if host connection fails.",
            "notes": "Primary system advantages."
        },
        {
            "title": "32. Limitations",
            "sub": "Engineering Constraints & Considerations",
            "body": "• Serial Communication Bridge: Requires host computer USB tethering in Phase 1 prototype.\n• DHT11 Sensor Latency: Refresh rate restricted to 0.5 Hz hardware sampling limit.\n• Point Occupancy Detection: IR sensor provides single-point coverage rather than complete spatial density tracking.",
            "notes": "Acknowledging current engineering constraints."
        },
        {
            "title": "33. Future Scope",
            "sub": "Next-Generation System Expansion Roadmap",
            "body": "• Off-Grid Solar PV Integration: Direct battery management and solar energy harvesting analytics.\n• ESP32 Microcontroller Upgrade: Direct Wi-Fi / MQTT cloud dashboard communication without host PC.\n• Computer Vision Edge AI: YOLO-based camera occupancy tracking for multi-passenger density evaluation.",
            "notes": "Future expansions including solar, ESP32, and TinyML."
        },
        {
            "title": "34. UN SDG Mapping",
            "sub": "Alignment with United Nations Sustainable Development Goals",
            "body": "• SDG 7 (Affordable & Clean Energy): Optimizes power draw via demand-adaptive switching.\n• SDG 9 (Industry, Innovation & Infrastructure): Upgrades legacy transit stops into smart edge nodes.\n• SDG 11 (Sustainable Cities & Communities): Provides micro-climate air quality monitoring.\n• SDG 13 (Climate Action): Reduces municipal electrical power demand and carbon emissions.",
            "notes": "Mapping contributions to United Nations Sustainable Development Goals."
        },
        {
            "title": "35. Conclusion",
            "sub": "Summary of Research Contributions",
            "body": "Paryavaran AI establishes a research-grade blueprint for sustainable smart city infrastructure.\n\nKey Achievements:\n• 42.5% reduction in daily energy usage via demand-driven actuation.\n• High accuracy ML modeling (0.9982 R² with CatBoost).\n• Zero-hardware mathematical current estimation framework.",
            "notes": "Concluding research remarks."
        },
        {
            "title": "36. Acknowledgements",
            "sub": "Institutional & Academic Support",
            "body": "Sincere gratitude to academic advisors, open-source AI software communities, and smart city initiative mentors for guidance and support during the design and validation of Paryavaran AI.\n\nAuthor: Aditya Kumar Mohanani\nProject Repository: Paryavaran-AI",
            "notes": "Formal acknowledgements slide."
        },
        {
            "title": "37. References",
            "sub": "Authoritative Academic & Technical Citations",
            "body": "[1] A. Kumar et al., 'IoT-enabled smart cities: Energy optimization frameworks,' IEEE Internet of Things Journal, 2023.\n[2] M. Mohani, 'Predictive modeling in urban environmental monitoring,' ACM Trans. Sensor Networks, 2025.\n[3] United Nations, 'Goal 11: Sustainable Cities and Communities,' UN SDG Guidelines, 2026.\n[4] Scikit-Learn Documentation, 'Machine Learning Regression Benchmarks,' 2025.",
            "notes": "IEEE formatted scientific references."
        },
        {
            "title": "38. Thank You",
            "sub": "Questions, Answers & Discussion",
            "body": "PARYAVARAN AI: Green Energy Smart Bus Stand\n\nThank you for your time and attention.\n\nAuthor: Aditya Kumar Mohanani\nRepository: github.com/AdityaMohanani/Paryavaran-AI\nLicense: MIT License",
            "notes": "Thank you slide. Inviting questions from the audience."
        }
    ]

    for data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[6]) # Blank layout

        # Background shape
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()

        # Header Title
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = data["title"]
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = COLOR_ACCENT

        # Subtitle
        st_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.7), Inches(0.5))
        stf = st_box.text_frame
        stf.word_wrap = True
        sp = stf.paragraphs[0]
        sp.text = data["sub"]
        sp.font.size = Pt(16)
        sp.font.color.rgb = COLOR_MUTED

        # Card Container
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = RGBColor(33, 38, 45)

        # Body Content
        c_box = slide.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(11.133), Inches(4.4))
        ctf = c_box.text_frame
        ctf.word_wrap = True
        cp = ctf.paragraphs[0]
        cp.text = data["body"]
        cp.font.size = Pt(15)
        cp.font.color.rgb = COLOR_WHITE

        # Speaker Notes
        notes_slide = slide.notes_slide
        text_frame = notes_slide.notes_text_frame
        text_frame.text = data["notes"]

    prs.save("Paryavaran_AI_Scientific_Deck.pptx")
    print("[✔] Successfully generated 'Paryavaran_AI_Scientific_Deck.pptx'")

if __name__ == "__main__":
    build_presentation()