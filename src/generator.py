import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_synthetic_data(seed: int = 20261022, scale: str = "starter"):
    print(f"[{datetime.now()}] Starting synthetic data generation (Scale: {scale}, Seed: {seed})...")
    np.random.seed(seed)
    random.seed(seed)

    # Scale parameters
    if scale == "starter":
        num_shipments = 50
        num_containers = 20
    else:
        num_shipments = 1000
        num_containers = 300

    # 1. Products & Threshold Policies
    products_data = [
        {"product_id": "PRD-0001", "product_name": "mRNA Covid Vaccine", "category": "VACCINES", "default_storage_type": "FROZEN", "min_temp": -80.0, "max_temp": -60.0, "max_duration": 120},
        {"product_id": "PRD-0002", "product_name": "Insulin Glargine", "category": "BIOLOGICS", "default_storage_type": "REFRIGERATED", "min_temp": 2.0, "max_temp": 8.0, "max_duration": 240},
        {"product_id": "PRD-0003", "product_name": "Fresh Organic Avocados", "category": "FRESH_PRODUCE", "default_storage_type": "AMBIENT", "min_temp": 4.0, "max_temp": 12.0, "max_duration": 360},
        {"product_id": "PRD-0004", "product_name": "Monoclonal Antibodies", "category": "PHARMA", "default_storage_type": "REFRIGERATED", "min_temp": 2.0, "max_temp": 8.0, "max_duration": 180},
    ]
    df_products = pd.DataFrame([ {k: v for k, v in p.items() if k in ["product_id", "product_name", "category", "default_storage_type"]} for p in products_data ])
    
    policies_data = []
    for i, p in enumerate(products_data, start=1):
        policies_data.append({
            "policy_id": f"POL-{i:04d}",
            "product_id": p["product_id"],
            "min_temp": p["min_temp"],
            "max_temp": p["max_temp"],
            "min_humidity": 30.0,
            "max_humidity": 75.0,
            "max_permissible_duration_mins": p["max_duration"],
            "effective_start_date": "2026-01-01",
            "effective_end_date": "2026-12-31"
        })
    df_policies = pd.DataFrame(policies_data)

    # 2. Containers
    container_types = ["ACTIVE_REEFER", "PASSIVE_QUILTED", "DRY_VAN"]
    containers_data = []
    for i in range(1, num_containers + 1):
        containers_data.append({
            "container_id": f"CNT-{i:06d}",
            "container_type": random.choice(container_types),
            "status": "ACTIVE",
            "tare_weight_kg": round(random.uniform(150.0, 650.0), 2)
        })
    df_containers = pd.DataFrame(containers_data)

    # 3. Sensors (2 per container: TEMP and HUM)
    sensors_data = []
    for _, c in df_containers.iterrows():
        c_id = c["container_id"]
        sensors_data.append({
            "sensor_id": f"SNS-{c_id}-TEMP",
            "container_id": c_id,
            "sensor_type": "TEMP",
            "status": "CALIBRATED",
            "calibration_due_date": "2027-06-30"
        })
        sensors_data.append({
            "sensor_id": f"SNS-{c_id}-HUM",
            "container_id": c_id,
            "sensor_type": "HUMIDITY",
            "status": "CALIBRATED",
            "calibration_due_date": "2027-06-30"
        })
    df_sensors = pd.DataFrame(sensors_data)

    # 4. Shipments & Route Stops & Readings
    origins = ["Hyderabad Hub", "Mumbai Port", "Bangalore Bio-Cluster", "Chennai Depot"]
    destinations = ["Delhi Central", "Kolkata Cold-Store", "Pune Pharma Park", "Ahmedabad Hub"]

    shipments_data = []
    bridge_data = []
    stops_data = []
    readings_data = []
    custody_data = []

    base_time = datetime(2026, 10, 1, 8, 0, 0)

    for i in range(1, num_shipments + 1):
        shp_id = f"SHP-2026-{i:06d}"
        prod = random.choice(products_data)
        prod_id = prod["product_id"]
        policy_id = df_policies[df_policies["product_id"] == prod_id]["policy_id"].values[0]
        
        container = df_containers.sample(n=1, random_state=seed + i).iloc[0]
        container_id = container["container_id"]

        departure_ts = base_time + timedelta(hours=random.randint(0, 120))
        trip_days = random.randint(2, 5)
        delivery_ts = departure_ts + timedelta(days=trip_days)

        shipments_data.append({
            "shipment_id": shp_id,
            "product_id": prod_id,
            "policy_id": policy_id,
            "origin": random.choice(origins),
            "destination": random.choice(destinations),
            "status": "DELIVERED",
            "actual_departure_ts": departure_ts.isoformat(),
            "actual_delivery_ts": delivery_ts.isoformat()
        })

        bridge_data.append({
            "assignment_id": f"SHP_CNT-{i:06d}",
            "shipment_id": shp_id,
            "container_id": container_id
        })

        # Route Stops (3 stops per trip)
        for stop_idx in range(1, 4):
            stop_time = departure_ts + timedelta(hours=(trip_days * 24 / 4) * stop_idx)
            stops_data.append({
                "route_stop_id": f"STP-{shp_id}-{stop_idx:02d}",
                "shipment_id": shp_id,
                "stop_sequence": stop_idx,
                "location_name": f"Checkpoint {stop_idx} - Hub",
                "planned_arrival_ts": stop_time.isoformat(),
                "delay_mins": random.choice([0, 15, 45, 120])
            })

        # Custody Events (Chain of custody)
        custody_data.append({
            "custody_id": f"CST-{i:06d}-1",
            "shipment_id": shp_id,
            "container_id": container_id,
            "action": "LOADED",
            "timestamp": departure_ts.isoformat(),
            "actor": "Operator_Alpha"
        })
        custody_data.append({
            "custody_id": f"CST-{i:06d}-2",
            "shipment_id": shp_id,
            "container_id": container_id,
            "action": "DELIVERED",
            "timestamp": delivery_ts.isoformat(),
            "actor": "Operator_Omega"
        })

        # Sensor Readings (every 5 minutes across the journey)
        time_stamps = pd.date_range(start=departure_ts, end=delivery_ts, freq="5min")
        temp_base = (prod["min_temp"] + prod["max_temp"]) / 2
        
        # Introduce occasional excursions in ~10% of shipments
        has_excursion = (i % 10 == 0)

        for ts in time_stamps:
            # Normal fluctuation
            t_val = temp_base + random.uniform(-1.5, 1.5)
            h_val = random.uniform(45.0, 65.0)
            flag = "OK"

            if has_excursion and (departure_ts + timedelta(hours=12) <= ts <= departure_ts + timedelta(hours=24)):
                t_val = prod["max_temp"] + random.uniform(3.0, 8.0) # Breach!
                flag = "OUT_OF_RANGE"

            temp_sensor_id = f"SNS-{container_id}-TEMP"
            readings_data.append({
                "reading_id": f"RDG-{temp_sensor_id}-{int(ts.timestamp())}",
                "sensor_id": temp_sensor_id,
                "shipment_id": shp_id,
                "timestamp": ts.isoformat(),
                "temp_c": round(t_val, 2),
                "humidity_pct": round(h_val, 2),
                "quality_flag": flag
            })

    print(f"[{datetime.now()}] Synthetic generation complete. Generated {num_shipments} shipments and {len(readings_data)} telemetry readings.")
    return {
        "products": df_products,
        "policies": df_policies,
        "containers": df_containers,
        "sensors": df_sensors,
        "shipments": pd.DataFrame(shipments_data),
        "bridge": pd.DataFrame(bridge_data),
        "stops": pd.DataFrame(stops_data),
        "readings": pd.DataFrame(readings_data),
        "custody": pd.DataFrame(custody_data)
    }

if __name__ == "__main__":
    data = generate_synthetic_data(seed=20261022, scale="starter")
    print("Sample Shipments:\n", data["shipments"].head(2))