import pandas as pd
from datetime import datetime

def process_excursions_and_capas(data_dict):
    print(f"[{datetime.now()}] Running business rules engine (Excursions & CAPAs)...")
    
    df_readings = data_dict["readings"]
    df_policies = data_dict["policies"]
    df_shipments = data_dict["shipments"]
    
    # Merge readings with shipment and policy info
    df_merged = df_readings.merge(df_shipments[["shipment_id", "policy_id"]], on="shipment_id")
    df_merged = df_merged.merge(df_policies, on="policy_id")
    
    excursions = []
    capas = []
    
    exc_counter = 1
    capa_counter = 1
    
    # Group by shipment to evaluate continuous breaches
    for shp_id, group in df_merged.groupby("shipment_id"):
        group = group.sort_values("timestamp")
        policy = group.iloc[0]
        
        min_t = policy["min_temp"]
        max_t = policy["max_temp"]
        max_allowed_mins = policy["max_permissible_duration_mins"]
        
        in_excursion = False
        exc_start = None
        breach_count = 0
        
        for _, row in group.iterrows():
            temp = row["temp_c"]
            is_breach = (temp < min_t) or (temp > max_t) or (row["quality_flag"] == "OUT_OF_RANGE")
            
            if is_breach:
                if not in_excursion:
                    in_excursion = True
                    exc_start = pd.to_datetime(row["timestamp"])
                    breach_count = 1
                else:
                    breach_count += 1
            else:
                if in_excursion:
                    # Excursion ended
                    exc_end = pd.to_datetime(row["timestamp"])
                    duration_mins = int((exc_end - exc_start).total_seconds() / 60)
                    
                    if duration_mins >= max_allowed_mins:
                        exc_id = f"EXC-2026-{exc_counter:06d}"
                        severity = "PROLONGED_BREACH" if duration_mins > 180 else "BRIEF_WARNING"
                        
                        excursions.append({
                            "excursion_id": exc_id,
                            "shipment_id": shp_id,
                            "policy_id": policy["policy_id"],
                            "start_ts": exc_start.isoformat(),
                            "end_ts": exc_end.isoformat(),
                            "duration_mins": duration_mins,
                            "severity": severity
                        })
                        
                        # Generate corresponding CAPA
                        capas.append({
                            "capa_id": f"CAPA-2026-{capa_counter:06d}",
                            "excursion_id": exc_id,
                            "shipment_id": shp_id,
                            "action_type": "QUARANTINE_BATCH" if severity == "PROLONGED_BREACH" else "ACCEPT_WITH_DEVIATION",
                            "status": "OPEN"
                        })
                        
                        exc_counter += 1
                        capa_counter += 1
                        
                    in_excursion = False
                    breach_count = 0

    df_excursions = pd.DataFrame(excursions)
    df_capas = pd.DataFrame(capas)
    
    print(f"[{datetime.now()}] Rules engine complete. Detected {len(df_excursions)} excursions and generated {len(df_capas)} CAPAs.")
    
    data_dict["excursions"] = df_excursions
    data_dict["capas"] = df_capas
    return data_dict

if __name__ == "__main__":
    from generator import generate_synthetic_data
    raw_data = generate_synthetic_data(seed=20261022, scale="starter")
    processed_data = process_excursions_and_capas(raw_data)
    print("Sample Excursions:\n", processed_data["excursions"].head(2))