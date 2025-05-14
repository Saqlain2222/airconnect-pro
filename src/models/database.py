from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///airline.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class FlightStatus(enum.Enum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    BOARDING = "boarding"

class UserRole(enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")
    crew_assignments = relationship("CrewAssignment", back_populates="crew_member")

class Airport(Base):
    __tablename__ = 'airports'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    
    # Relationships
    departure_flights = relationship("Flight", foreign_keys="Flight.departure_airport_id", back_populates="departure_airport")
    arrival_flights = relationship("Flight", foreign_keys="Flight.arrival_airport_id", back_populates="arrival_airport")

class Flight(Base):
    __tablename__ = 'flights'
    
    id = Column(Integer, primary_key=True)
    flight_number = Column(String(10), unique=True, nullable=False)
    departure_airport_id = Column(Integer, ForeignKey('airports.id'), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey('airports.id'), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    aircraft_type = Column(String(50), nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    status = Column(Enum(FlightStatus), nullable=False)
    base_price = Column(Float, nullable=False)
    
    # Relationships
    departure_airport = relationship("Airport", foreign_keys=[departure_airport_id], back_populates="departure_flights")
    arrival_airport = relationship("Airport", foreign_keys=[arrival_airport_id], back_populates="arrival_flights")
    bookings = relationship("Booking", back_populates="flight")
    crew_assignments = relationship("CrewAssignment", back_populates="flight")

class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    booking_date = Column(DateTime, default=datetime.utcnow)
    seat_number = Column(String(10), nullable=False)
    booking_status = Column(String(20), nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")

class CrewAssignment(Base):
    __tablename__ = 'crew_assignments'
    
    id = Column(Integer, primary_key=True)
    crew_member_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    flight_id = Column(Integer, ForeignKey('flights.id'), nullable=False)
    role = Column(String(50), nullable=False)
    assignment_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    crew_member = relationship("User", back_populates="crew_assignments")
    flight = relationship("Flight", back_populates="crew_assignments")

def init_db():
    """Initialize the database with all tables."""
    Base.metadata.create_all(engine)
    return engine

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 