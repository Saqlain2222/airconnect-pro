from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

class FlightStatus(str, Enum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    BOARDING = "boarding"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CUSTOMER

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AirportBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    name: str
    city: str
    country: str

class AirportResponse(AirportBase):
    id: int

    class Config:
        from_attributes = True

class FlightBase(BaseModel):
    flight_number: str
    departure_airport_id: int
    arrival_airport_id: int
    departure_time: datetime
    arrival_time: datetime
    aircraft_type: str
    total_seats: int
    available_seats: int
    base_price: float

class FlightCreate(FlightBase):
    status: FlightStatus = FlightStatus.SCHEDULED

class FlightResponse(FlightBase):
    id: int
    status: FlightStatus
    departure_airport: AirportResponse
    arrival_airport: AirportResponse

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    flight_id: int
    seat_number: str

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: int
    user_id: int
    booking_date: datetime
    booking_status: str
    total_price: float
    flight: FlightResponse

    class Config:
        from_attributes = True

class FlightSearch(BaseModel):
    departure_airport: str
    arrival_airport: str
    date: datetime

class BookingHistory(BaseModel):
    start_date: datetime
    end_date: datetime 