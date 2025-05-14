from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AccountType(str, Enum):
    ADMINISTRATOR = "admin"
    EMPLOYEE = "staff"
    PASSENGER = "customer"

class JourneyState(str, Enum):
    PLANNED = "scheduled"
    LATE = "delayed"
    ABORTED = "cancelled"
    FINISHED = "completed"
    DEPARTING = "boarding"

class AccountBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class AccountRegistration(AccountBase):
    password: str = Field(..., min_length=8)
    account_type: AccountType = AccountType.PASSENGER

class AccountInfo(AccountBase):
    id: int
    account_type: AccountType
    created_at: datetime

    class Config:
        from_attributes = True

class AuthToken(BaseModel):
    access_token: str
    token_type: str

class TokenInfo(BaseModel):
    username: Optional[str] = None

class TerminalBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    name: str
    city: str
    country: str

class TerminalInfo(TerminalBase):
    id: int

    class Config:
        from_attributes = True

class JourneyBase(BaseModel):
    flight_number: str
    departure_terminal_id: int
    arrival_terminal_id: int
    departure_time: datetime
    arrival_time: datetime
    aircraft_type: str
    total_seats: int
    available_seats: int
    base_price: float

class JourneyCreation(JourneyBase):
    status: JourneyState = JourneyState.PLANNED

class JourneyInfo(JourneyBase):
    id: int
    status: JourneyState
    departure_terminal: TerminalInfo
    arrival_terminal: TerminalInfo

    class Config:
        from_attributes = True

class ReservationBase(BaseModel):
    journey_id: int
    seat_number: str

class ReservationCreation(ReservationBase):
    pass

class ReservationInfo(ReservationBase):
    id: int
    account_id: int
    reservation_date: datetime
    reservation_status: str
    total_price: float
    journey: JourneyInfo

    class Config:
        from_attributes = True

class JourneySearch(BaseModel):
    departure_terminal: str
    arrival_terminal: str
    date: datetime

class ReservationHistory(BaseModel):
    start_date: datetime
    end_date: datetime 