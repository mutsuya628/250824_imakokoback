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
    noise: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_active: bool = True

class PlanType(SQLModel, table=True):
    plan_type_id: int = Field(primary_key=True)
    code: str
    name_ja: str
    unit_days: int

class SpacePlan(SQLModel, table=True):
    space_plan_id: Optional[int] = Field(default=None, primary_key=True)
    space_id: str = Field(foreign_key="space.space_id")
    plan_type_id: int = Field(foreign_key="plantype.plan_type_id")
    price_tax_included: int
    refundable: bool = True
    min_units: int = 1
    max_units: int = 12

class Reservation(SQLModel, table=True):
    reservation_id: Optional[int] = Field(default=None, primary_key=True)
    user_name: str
    user_email: str
    space_id: str = Field(foreign_key="space.space_id")
    plan_type_id: int = Field(foreign_key="plantype.plan_type_id")
    start_date: date
    units: int
    end_date: date
    status: str = "confirmed"
    price_total: int

class SearchParams(BaseModel):
    plan_code: str
    start_date: date
    units: int
    max_price_total: Optional[int] = None
    min_wifi_mbps: Optional[int] = None
    private_room_required: Optional[bool] = None
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

