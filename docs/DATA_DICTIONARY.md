# Cold-Chain Logistics & Excursion Management — Data Dictionary

This document defines the schema, field types, constraints, units, and validation rules for all entities in the Cold-Chain Excursion Management system.

---

## 1. Product (`Product`)
Defines master catalog items (e.g., Biologics, Vaccines, Fresh Produce, Pharmaceuticals).
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | String | Required | Format: `PRD-0001` onwards | N/A | Primary Key | Must match regex `^PRD-\d{4}$`. |
| `product_name` | String | Required | Any valid descriptive name | N/A | Unique | Non-empty string. |
| `category` | String | Required | `BIOLOGICS`, `VACCINES`, `FRESH_PRODUCE`, `PHARMA` | N/A | Indexed | Must belong to allowed enum set. |
| `default_storage_type` | String | Required | `FROZEN`, `REFRIGERATED`, `AMBIENT` | N/A | None | Must belong to allowed enum set. |

---

## 2. Threshold Policy (`ThresholdPolicy`)
Defines product-specific environmental limits and permissible excursion durations.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `policy_id` | String | Required | Format: `POL-0001` onwards | N/A | Primary Key | Must match regex `^POL-\d{4}$`. |
| `product_id` | String | Required | Existing `product_id` | N/A | Foreign Key | References `Product(product_id)`. |
| `min_temp` | Float | Required | `-80.0` to `25.0` | °C | None | `min_temp` <= `max_temp`. |
| `max_temp` | Float | Required | `-20.0` to `50.0` | °C | None | Must be greater than or equal to `min_temp`. |
| `min_humidity` | Float | Optional | `0.0` to `100.0` | % RH | None | Valid percentage range. |
| `max_humidity` | Float | Optional | `0.0` to `100.0` | % RH | None | `min_humidity` <= `max_humidity`. |
| `max_permissible_duration_mins` | Integer | Required | `>= 0` | Minutes | None | Maximum allowable continuous excursion time before a breach triggers. |
| `effective_start_date` | Date/ISO | Required | Valid ISO 8601 date | N/A | None | Must precede `effective_end_date`. |
| `effective_end_date` | Date/ISO | Optional | Valid ISO 8601 date | N/A | None | Must follow `effective_start_date` if present. |

---

## 3. Container (`Container`)
Insulated transport boxes or reefers.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `container_id` | String | Required | Format: `CNT-000001` | N/A | Primary Key | Must match regex `^CNT-\d{6}$`. |
| `container_type` | String | Required | `ACTIVE_REEFER`, `PASSIVE_QUILTED`, `DRY_VAN` | N/A | None | Must belong to allowed enum set. |
| `status` | String | Required | `ACTIVE`, `MAINTENANCE`, `RETIRED` | N/A | None | Must belong to allowed enum set. |
| `tare_weight_kg` | Float | Required | `> 0` | kg | None | Positive float. |

---

## 4. Shipment (`Shipment`)
Represents an end-to-end transport journey of goods.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `shipment_id` | String | Required | Format: `SHP-2026-000001` | N/A | Primary Key | Must match regex `^SHP-\d{4}-\d{6}$`. |
| `product_id` | String | Required | Existing `product_id` | N/A | Foreign Key | References `Product(product_id)`. |
| `policy_id` | String | Required | Existing `policy_id` | N/A | Foreign Key | References `ThresholdPolicy(policy_id)`. |
| `origin` | String | Required | City/Hub code | N/A | None | Non-empty string. |
| `destination` | String | Required | City/Hub code | N/A | None | Non-empty string. |
| `status` | String | Required | `PLANNED`, `IN_TRANSIT`, `DELIVERED`, `QUARANTINED` | N/A | None | Must belong to allowed enum set. |
| `actual_departure_ts` | ISO Timestamp | Required | Valid ISO 8601 UTC | N/A | None | Must precede `actual_delivery_ts`. |
| `actual_delivery_ts` | ISO Timestamp | Optional | Valid ISO 8601 UTC | N/A | None | Must follow `actual_departure_ts`. |

---

## 5. ShipmentContainer (`ShipmentContainer` — Bridge Table)
Resolves many-to-many relationships between Shipments and Containers across route legs.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `assignment_id` | String | Required | Format: `SHP_CNT-000001` | N/A | Primary Key | Unique assignment ID. |
| `shipment_id` | String | Required | Existing `shipment_id` | N/A | Foreign Key | References `Shipment(shipment_id)`. |
| `container_id` | String | Required | Existing `container_id` | N/A | Foreign Key | References `Container(container_id)`. |

---

## 6. Sensor (`Sensor`)
IoT telemetry monitoring probes attached to containers.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sensor_id` | String | Required | Format: `SNS-CNT-000001-TEMP` | N/A | Primary Key | Unique sensor identifier. |
| `container_id` | String | Required | Existing `container_id` | N/A | Foreign Key | References `Container(container_id)`. |
| `sensor_type` | String | Required | `TEMP`, `HUMIDITY` | N/A | None | Must belong to allowed enum set. |
| `status` | String | Required | `CALIBRATED`, `EXPIRED`, `FAULTY` | N/A | None | Must belong to allowed enum set. |
| `calibration_due_date` | Date/ISO | Required | Valid ISO 8601 date | N/A | None | Must be tracked against current inspection date. |

---

## 7. RouteStop (`RouteStop`)
Waypoints and checkpoints along a shipment's route.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `route_stop_id` | String | Required | Format: `STP-<shipment_id>-01` | N/A | Primary Key | Unique stop identifier. |
| `shipment_id` | String | Required | Existing `shipment_id` | N/A | Foreign Key | References `Shipment(shipment_id)`. |
| `stop_sequence` | Integer | Required | `>= 1` | N/A | None | Strictly increasing per shipment. |
| `location_name` | String | Required | Facility/Hub name | N/A | None | Non-empty string. |
| `planned_arrival_ts` | ISO Timestamp| Required | Valid ISO 8601 UTC | N/A | None | Chronological ordering. |
| `delay_mins` | Integer | Required | `>= 0` | Minutes | None | Recorded delay at this stop. |

---

## 8. SensorReading (`SensorReading`)
Fixed 5-minute interval telemetry recordings.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `reading_id` | String | Required | Format: `RDG-<sensor_id>-<timestamp>` | N/A | Primary Key | Unique telemetry record. |
| `sensor_id` | String | Required | Existing `sensor_id` | N/A | Foreign Key | References `Sensor(sensor_id)`. |
| `shipment_id` | String | Required | Existing `shipment_id` | N/A | Foreign Key | References `Shipment(shipment_id)`. |
| `timestamp` | ISO Timestamp| Required | Valid ISO 8601 UTC | N/A | None | 5-minute fixed intervals. |
| `temp_c` | Float | Required | `-90.0` to `60.0` | °C | None | Physical operating sensor range limit. |
| `humidity_pct` | Float | Optional | `0.0` to `100.0` | % RH | None | Valid hygrometer reading range. |
| `quality_flag` | String | Required | `OK`, `OUT_OF_RANGE`, `GAP`, `SYNTHETIC_ANOMALY` | N/A | None | Telemetry confidence flag. |

---

## 9. Excursion (`Excursion`)
Recorded threshold breaches requiring quality review.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `excursion_id` | String | Required | Format: `EXC-2026-000001` | N/A | Primary Key | Unique excursion event ID. |
| `shipment_id` | String | Required | Existing `shipment_id` | N/A | Foreign Key | References `Shipment(shipment_id)`. |
| `policy_id` | String | Required | Existing `policy_id` | N/A | Foreign Key | References `ThresholdPolicy(policy_id)`. |
| `start_ts` | ISO Timestamp| Required | Valid ISO 8601 UTC | N/A | None | Excursion start timestamp. |
| `end_ts` | ISO Timestamp| Required | Valid ISO 8601 UTC | N/A | None | Excursion resolution timestamp. |
| `duration_mins` | Integer | Required | `> 0` | Minutes | None | Calculated total duration in breach. |
| `severity` | String | Required | `BRIEF_WARNING`, `PROLONGED_BREACH` | N/A | None | Classification based on policy limits. |

---

## 10. CustodyEvent (`CustodyEvent`)
Append-only chain-of-custody handoff records.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `custody_id` | String | Required | Format: `CST-2026-000001` | N/A | Primary Key | Unique custody event record. |
| `shipment_id` | String | Required | Existing `shipment_id` | N/A | Foreign Key | References `Shipment(shipment_id)`. |
| `container_id` | String | Required | Existing `container_id` | N/A | Foreign Key | References `Container(container_id)`. |
| `action` | String | Required | `LOADED`, `SEALED`, `HANDOFF`, `INSPECTED`, `DELIVERED` | N/A | None | Append-only state transition. |
| `timestamp` | ISO Timestamp| Required | Valid ISO 8601 UTC | N/A | None | Strict chronological sequence. |
| `actor` | String | Required | Operator/Engineer ID | N/A | None | Non-empty string. |

---

## 11. CorrectiveAction (`CorrectiveAction`)
CAPA records triggered in response to excursions.
| Field Name | Type | Required/Optional | Allowed Values / Range | Units | Uniqueness | Validation Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `capa_id` | String | Required | Format: `CAPA-2026-000001` | N/A | Primary Key | Unique corrective action ID. |
| `excursion_id` | String | Required | Existing `excursion_id` | N/A | Foreign Key | References `Excursion(excursion_id)`. |
| `shipment_id` | String | Required | Existing `shipment_id` | N/A | Foreign Key | References `Shipment(shipment_id)`. |
| `action_type` | String | Required | `QUARANTINE_BATCH`, `RECALIBRATE_SENSOR`, `REJECT_SHIPMENT`, `ACCEPT_WITH_DEVIATION` | N/A | None | Required resolution step. |
| `status` | String | Required | `OPEN`, `IN_REVIEW`, `CLOSED` | N/A | None | CAPA lifecycle state. |