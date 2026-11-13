import pandas as pd

def validate_relations(data_dict):
    errors = []
    
    df_shipments = data_dict["shipments"]
    df_products = data_dict["products"]
    df_policies = data_dict["policies"]
    df_sensors = data_dict["sensors"]
    df_readings = data_dict["readings"]
    df_bridge = data_dict["bridge"]
    df_containers = data_dict["containers"]
    
    valid_products = set(df_products["product_id"])
    valid_policies = set(df_policies["policy_id"])
    valid_sensors = set(df_sensors["sensor_id"])
    valid_shipments = set(df_shipments["shipment_id"])
    valid_containers = set(df_containers["container_id"])
    
    for _, row in df_shipments.iterrows():
        if row["product_id"] not in valid_products:
            errors.append(f"Invalid product_id {row['product_id']} in shipment {row['shipment_id']}")
        if row["policy_id"] not in valid_policies:
            errors.append(f"Invalid policy_id {row['policy_id']} in shipment {row['shipment_id']}")
        
        dep = pd.to_datetime(row["actual_departure_ts"])
        delv = pd.to_datetime(row["actual_delivery_ts"]) if pd.notna(row["actual_delivery_ts"]) else None
        if delv and dep > delv:
            errors.append(f"Temporal violation: departure {dep} after delivery {delv} for shipment {row['shipment_id']}")

    for _, row in df_readings.iterrows():
        if row["sensor_id"] not in valid_sensors:
            errors.append(f"Orphan sensor reading: sensor {row['sensor_id']}")
        if row["shipment_id"] not in valid_shipments:
            errors.append(f"Orphan sensor reading: shipment {row['shipment_id']}")
        if row["temp_c"] < -90.0 or row["temp_c"] > 60.0:
            if row["quality_flag"] != "SYNTHETIC_ANOMALY":
                errors.append(f"Physical range violation: temp {row['temp_c']} in reading {row['reading_id']}")

    for _, row in df_bridge.iterrows():
        if row["shipment_id"] not in valid_shipments or row["container_id"] not in valid_containers:
            errors.append(f"Invalid bridge mapping in assignment {row['assignment_id']}")

    if errors:
        print(f"Validation completed with {len(errors)} anomalies/errors detected.")
        for err in errors[:5]:
            print(f" - {err}")
    else:
        print("Validation passed successfully with zero relational errors.")
        
    return errors

if __name__ == "__main__":
    from generator import generate_synthetic_data
    from rules_engine import process_excursions_and_capas
    from anomalies import inject_ground_truth_anomalies
    
    raw = generate_synthetic_data(seed=20261022, scale="starter")
    processed = process_excursions_and_capas(raw)
    final_data = inject_ground_truth_anomalies(processed)
    validate_relations(final_data)