from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ProductModel(BaseModel):
    product_id: str = Field(..., pattern=r"^PRD-\d{4}$")
    product_name: str
    category: str = Field(..., description="BIOLOGICS, VACCINES, FRESH_PRODUCE, PHARMA")
    default_storage_type: str = Field(..., description="FROZEN, REFRIGERATED, AMBIENT")


class ThresholdPolicyModel(BaseModel):
    policy_id: str = Field(..., pattern=r"^POL-\d{4}$")
    product_id: str = Field(..., pattern=r"^PRD-\d{4}$")
    min_temp: float
    max_temp: float
    min_humidity: Optional[float] = None
    max_humidity: Optional[float] = None
    max_permissible_duration_mins: int = Field(..., ge=0)
    effective_start_date: date
    effective_end_date: Optional[date] = None

    @field_validator("max_temp")
    @classmethod
    def validate_temp_range(cls, v, values):
        data = values.data
        if "min_temp" in data and v < data["min_temp"]:
            raise ValueError("max_temp must be greater than or equal to min_temp")
        return v


class ContainerModel(BaseModel):
    container_id: str = Field(..., pattern=r"^CNT-\d{6}$")
    container_type: str
    status: str = Field(..., description="ACTIVE, MAINTENANCE, RETIRED")
    tare_weight_kg: float = Field(..., gt=0)


class ShipmentModel(BaseModel):
    shipment_id: str = Field(..., pattern=r"^SHP-\d{4}-\d{6}$")
    product_id: str = Field(..., pattern=r"^PRD-\d{4}$")
    policy_id: str = Field(..., pattern=r"^POL-\d{4}$")
    origin: str
    destination: str
    status: str = Field(..., description="PLANNED, IN_TRANSIT, DELIVERED, QUARANTINED")
    actual_departure_ts: datetime
    actual_delivery_ts: Optional[datetime] = None


class SensorModel(BaseModel):
    sensor_id: str
    container_id: str = Field(..., pattern=r"^CNT-\d{6}$")
    sensor_type: str = Field(..., description="TEMP, HUMIDITY")
    status: str = Field(..., description="CALIBRATED, EXPIRED, FAULTY")
    calibration_due_date: date


class SensorReadingModel(BaseModel):
    reading_id: str
    sensor_id: str
    shipment_id: str = Field(..., pattern=r"^SHP-\d{4}-\d{6}$")
    timestamp: datetime
    temp_c: float = Field(..., ge=-90.0, le=60.0)
    humidity_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    quality_flag: str = Field(..., description="OK, OUT_OF_RANGE, GAP, SYNTHETIC_ANOMALY")