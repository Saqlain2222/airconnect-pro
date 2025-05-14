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
DB_CONNECTION = os.getenv("DATABASE_URL", "sqlite:///airline.db")
engine = create_engine(DB_CONNECTION, connect_args={"check_same_thread": False})
DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class JourneyState(enum.Enum):
    PLANNED = "scheduled"
    LATE = "delayed"
    ABORTED = "cancelled"
    FINISHED = "completed"
    DEPARTING = "boarding"

class AccountType(enum.Enum):
    ADMINISTRATOR = "admin"
    EMPLOYEE = "staff"
    PASSENGER = "customer"

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = relationship("Reservation", back_populates="account")
    crew_assignments = relationship("CrewAssignment", back_populates="crew_member")

class Terminal(Base):
    __tablename__ = 'terminals'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(3), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    
    # Relationships
    departure_journeys = relationship("Journey", foreign_keys="Journey.departure_terminal_id", back_populates="departure_terminal")
    arrival_journeys = relationship("Journey", foreign_keys="Journey.arrival_terminal_id", back_populates="arrival_terminal")

class Journey(Base):
    __tablename__ = 'journeys'
    
    id = Column(Integer, primary_key=True)
    flight_number = Column(String(10), unique=True, nullable=False)
    departure_terminal_id = Column(Integer, ForeignKey('terminals.id'), nullable=False)
    arrival_terminal_id = Column(Integer, ForeignKey('terminals.id'), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    aircraft_type = Column(String(50), nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    status = Column(Enum(JourneyState), nullable=False)
    base_price = Column(Float, nullable=False)
    
    # Relationships
    departure_terminal = relationship("Terminal", foreign_keys=[departure_terminal_id], back_populates="departure_journeys")
    arrival_terminal = relationship("Terminal", foreign_keys=[arrival_terminal_id], back_populates="arrival_journeys")
    reservations = relationship("Reservation", back_populates="journey")
    crew_assignments = relationship("CrewAssignment", back_populates="journey")

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    journey_id = Column(Integer, ForeignKey('journeys.id'), nullable=False)
    reservation_date = Column(DateTime, default=datetime.utcnow)
    seat_number = Column(String(10), nullable=False)
    reservation_status = Column(String(20), nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="reservations")
    journey = relationship("Journey", back_populates="reservations")

class CrewAssignment(Base):
    __tablename__ = 'crew_assignments'
    
    id = Column(Integer, primary_key=True)
    crew_member_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    journey_id = Column(Integer, ForeignKey('journeys.id'), nullable=False)
    role = Column(String(50), nullable=False)
    assignment_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    crew_member = relationship("Account", back_populates="crew_assignments")
    journey = relationship("Journey", back_populates="crew_assignments")

def initialize_database():
    """Initialize the database with all tables."""
    Base.metadata.create_all(engine)
    return engine

def get_database_session():
    """Get database session."""
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close() 