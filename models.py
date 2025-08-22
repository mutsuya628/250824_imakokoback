from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date
from pydantic import BaseModel

class Space(SQLModel, table=True):
    space_id: str = Field(primary_key=True)
    category: str
    name: str
    provider: str
    prefecture: str
    city: str
    address: str
    wifi_mbps: int
    capacity_total: int
    private_room: bool
    noise: Optional[str] = None
    is_active: bool = True

class PlanType(SQLModel, table=True):
    plan_type_id: Optional[int] = Field(default=None, primary_key=True)
    code: str
    name_ja: str
    unit_days: int

class SpacePlan(SQLModel, table=True):
    space_plan_id: Optional[int] = Field(default=None, primary_key=True)
    space_id: str
    plan_type_id: int
    price_tax_included: int
    refundable: bool
    min_units: int
    max_units: int

class Reservation(SQLModel, table=True):
    reservation_id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    user_email: str
    space_id: str
    plan_type_id: int
    start_date: date
    units: int
    end_date: date
    price_total: int
    status: str

class SearchParams(BaseModel):
    plan_code: str
    start_date: date
    units: int
    max_price_total: Optional[int] = None
    min_wifi_mbps: Optional[int] = None
    private_room_required: Optional[bool] = False
    distance_km: Optional[float] = None
    near_lat: Optional[float] = None
    near_lng: Optional[float] = None
    category: Optional[str] = None

class ReservationCreate(BaseModel):
    user_name: str
    user_email: str
    space_id: str
    plan_code: str
    start_date: date
    units: int

