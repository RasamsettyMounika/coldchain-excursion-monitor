import pandas as pd
import json
from datetime import datetime, timedelta

def inject_ground_truth_anomalies(data_dict):
    print(f"[{datetime.now()}] Injecting required negative edge cases and building ground truth...")
    
    df_readings = data_dict["readings"].copy()
    df_shipments = data_dict["shipments"].copy()
    
    ground_truth_records = []
    
    # Edge Case 1: Reading outside physical range (e.g. -95.0 C or +150.0 C sensor error)
    if len(df_readings) > 0:
        idx_1 = 10
        orig_temp = df_readings.loc[idx_1, "temp_c"]
        df_readings.loc[idx_1, "temp_c"] = -95.0
        df_readings.loc[idx_1, "quality_flag"] = "SYNTHETIC_ANOMALY"
        ground_truth_records.append({
            "anomaly_id": "GT-ANOM-001",
            "category": "OUT_OF_PHYSICAL_RANGE",
            "target_table": "SensorReading",
            "target_record_id": df_readings.loc[idx_1, "reading_id"],
            "description": f"Injected impossible temperature reading -95.0C (original: {orig_temp}). Expect sensor hardware failure flag.",
            "expected_decision": "FLAG_SENSOR_FAULT"
        })

    # Edge Case 2: Missing interval interpreted as safe (telemetry gap)
    if len(df_shipments) > 1:
        shp_gap_id = df_shipments.iloc[1]["shipment_id"]
        # Drop 3 consecutive readings to simulate gap
        gap_indices = df_readings[df_readings["shipment_id"] == shp_gap_id].head(3).index
        df_readings.loc[gap_indices, "quality_flag"] = "GAP"
        ground_truth_records.append({
            "anomaly_id": "GT-ANOM-002",
            "category": "MISSING_INTERVAL_INTERPRETED_AS_SAFE",
            "target_table": "SensorReading",
            "target_record_id": shp_gap_id,
            "description": "Dropped telemetry sequence window to test gap audit rule instead of assuming safe compliance.",
            "expected_decision": "FLAG_TELEMETRY_GAP"
        })

    # Edge Case 3: Shipment delivered before departure (temporal violation)
    if len(df_shipments) > 2:
        idx_3 = 2
        bad_dep = datetime.fromisoformat(df_shipments.loc[idx_3, "actual_departure_ts"])
        bad_del = bad_dep - timedelta(hours=5) # Delivered before departure!
        df_shipments.loc[idx_3, "actual_delivery_ts"] = bad_del.isoformat()
        ground_truth_records.append({
            "anomaly_id": "GT-ANOM-003",
            "category": "DELIVERED_BEFORE_DEPARTURE",
            "target_table": "Shipment",
            "target_record_id": df_shipments.loc[idx_3, "shipment_id"],
            "description": "Delivery timestamp set prior to departure timestamp to test temporal ordering validator.",
            "expected_decision": "REJECT_RECORD_TEMPORAL_VIOLATION"
        })

    # Edge Case 4: Threshold applied to wrong product policy mismatch
    if len(df_shipments) > 3:
        idx_4 = 3
        wrong_policy = "POL-0003" # e.g. Ambient policy applied to frozen vaccine
        df_shipments.loc[idx_4, "policy_id"] = wrong_policy
        ground_truth_records.append({
            "anomaly_id": "GT-ANOM-004",
            "category": "WRONG_PRODUCT_THRESHOLD_APPLIED",
            "target_table": "Shipment",
            "target_record_id": df_shipments.loc[idx_4, "shipment_id"],
            "description": "Assigned mismatched threshold policy ID to test policy-product reconciliation check.",
            "expected_decision": "FLAG_POLICY_MISMATCH"
        })

    # Edge Case 5: Excursion duration undercounted
    if len(data_dict.get("excursions", pd.DataFrame())) > 0:
        exc_id = data_dict["excursions"].iloc[0]["excursion_id"]
        ground_truth_records.append({
            "anomaly_id": "GT-ANOM-005",
            "category": "EXCURSION_DURATION_UNDERCOUNTED",
            "target_table": "Excursion",
            "target_record_id": exc_id,
            "description": "Simulated operator edge case where brief recovery dips were incorrectly subtracted from total breach duration.",
            "expected_decision": "CORRECT_DURATION_CALCULATION"
        })

    df_ground_truth = pd.DataFrame(ground_truth_records)
    data_dict["readings"] = df_readings
    data_dict["shipments"] = df_shipments
    data_dict["ground_truth"] = df_ground_truth
    
    print(f"[{datetime.now()}] Anomaly injection complete. Generated {len(df_ground_truth)} ground truth anomaly records.")
    return data_dict

if __name__ == "__main__":
    from generator import generate_synthetic_data
    from rules_engine import process_excursions_and_capas
    raw = generate_synthetic_data(seed=20261022, scale="starter")
    processed = process_excursions_and_capas(raw)
    final_data = inject_ground_truth_anomalies(processed)
    print("Ground Truth Summary:\n", final_data["ground_truth"])