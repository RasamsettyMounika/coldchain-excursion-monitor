import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cold-Chain Excursion Monitor", layout="wide")

@st.cache_data
def load_data():
    data_dir = "data/starter"
    if not os.path.exists(data_dir):
        return None
    
    files = {
        "shipments": "shipments.csv",
        "readings": "sensor_readings.csv",
        "excursions": "excursions.csv",
        "capas": "corrective_actions.csv",
        "ground_truth": "ground_truth_anomalies.csv",
        "sensors": "sensors.csv"
    }
    
    data = {}
    for k, v in files.items():
        path = os.path.join(data_dir, v)
        if os.path.exists(path):
            data[k] = pd.read_csv(path)
        else:
            data[k] = pd.DataFrame()
    return data

data = load_data()

st.title("Cold-Chain Logistics & Excursion Management")
st.markdown("YottaFlex AI 72-Hour Code Challenge Dashboard")

if data is None or data["shipments"].empty:
    st.warning("No dataset found in data/starter/. Please run python src/exporter.py first.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Shipments", len(data["shipments"]))
    with col2:
        st.metric("Active Sensors", len(data["sensors"]))
    with col3:
        st.metric("Excursions Detected", len(data["excursions"]))
    with col4:
        st.metric("Ground Truth Anomalies", len(data["ground_truth"]))

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Shipments & Telemetry", "Excursions & CAPAs", "Ground Truth Anomalies"])

    with tab1:
        st.subheader("Shipment Overview")
        st.dataframe(data["shipments"], use_container_width=True)
        
        st.subheader("Sensor Readings Sample")
        st.dataframe(data["readings"].head(100), use_container_width=True)

    with tab2:
        st.subheader("Detected Excursions")
        if not data["excursions"].empty:
            st.dataframe(data["excursions"], use_container_width=True)
        else:
            st.info("No excursions recorded.")

        st.subheader("Corrective Actions (CAPAs)")
        if not data["capas"].empty:
            st.dataframe(data["capas"], use_container_width=True)
        else:
            st.info("No CAPAs generated.")

    with tab3:
        st.subheader("Injected Ground Truth Anomalies (Edge Cases)")
        if not data["ground_truth"].empty:
            st.dataframe(data["ground_truth"], use_container_width=True)
        else:
            st.info("No ground truth anomalies found.")