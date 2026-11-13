import os
import pandas as pd

def export_datasets(data_dict, output_dir="data/starter"):
    os.makedirs(output_dir, exist_ok=True)
    
    mapping = {
        "products": "products.csv",
        "policies": "threshold_policies.csv",
        "containers": "containers.csv",
        "sensors": "sensors.csv",
        "shipments": "shipments.csv",
        "bridge": "shipment_containers.csv",
        "stops": "route_stops.csv",
        "readings": "sensor_readings.csv",
        "custody": "custody_events.csv",
        "excursions": "excursions.csv",
        "capas": "corrective_actions.csv",
        "ground_truth": "ground_truth_anomalies.csv"
    }
    
    for key, filename in mapping.items():
        if key in data_dict and isinstance(data_dict[key], pd.DataFrame):
            path = os.path.join(output_dir, filename)
            data_dict[key].to_csv(path, index=False)
            print(f"Exported {key} to {path} ({len(data_dict[key])} rows)")

if __name__ == "__main__":
    from generator import generate_synthetic_data
    from rules_engine import process_excursions_and_capas
    from anomalies import inject_ground_truth_anomalies
    
    raw = generate_synthetic_data(seed=20261022, scale="starter")
    processed = process_excursions_and_capas(raw)
    final_data = inject_ground_truth_anomalies(processed)
    export_datasets(final_data)