from src.models.database import init_db, User, Flight, Airport, Booking, UserRole
from src.dal.user_dal import UserDAL
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_data(session: Session):
    """Create sample data for testing."""
    # Create airports
    airports = [
        Airport(code="LHR", name="London Heathrow", city="London", country="UK"),
        Airport(code="JFK", name="John F. Kennedy", city="New York", country="USA"),
        Airport(code="CDG", name="Charles de Gaulle", city="Paris", country="France"),
        Airport(code="FRA", name="Frankfurt Airport", city="Frankfurt", country="Germany"),
        Airport(code="SIN", name="Changi Airport", city="Singapore", country="Singapore")
    ]
    session.add_all(airports)
    session.commit()

    # Create admin user
    user_dal = UserDAL(session)
    admin = user_dal.create_user(
        username="admin",
        email="admin@skylink.com",
        password="admin123",
        role=UserRole.ADMIN
    )

    # Create sample flights
    flights = [
        Flight(
            flight_number="SK101",
            departure_airport_id=1,  # LHR
            arrival_airport_id=2,    # JFK
            departure_time=datetime.now() + timedelta(days=1),
            arrival_time=datetime.now() + timedelta(days=1, hours=8),
            aircraft_type="Boeing 777",
            total_seats=300,
            available_seats=300,
            base_price=500.00,
            status="scheduled"
        ),
        Flight(
            flight_number="SK102",
            departure_airport_id=2,  # JFK
            arrival_airport_id=1,    # LHR
            departure_time=datetime.now() + timedelta(days=2),
            arrival_time=datetime.now() + timedelta(days=2, hours=7),
            aircraft_type="Boeing 787",
            total_seats=250,
            available_seats=250,
            base_price=450.00,
            status="scheduled"
        ),
        Flight(
            flight_number="SK201",
            departure_airport_id=1,  # LHR
            arrival_airport_id=3,    # CDG
            departure_time=datetime.now() + timedelta(days=1, hours=2),
            arrival_time=datetime.now() + timedelta(days=1, hours=3, minutes=30),
            aircraft_type="Airbus A320",
            total_seats=180,
            available_seats=180,
            base_price=150.00,
            status="scheduled"
        )
    ]
    session.add_all(flights)
    session.commit()

def main():
    """Initialize the database and create sample data."""
    print("Initializing database...")
    engine = init_db()
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create sample data
        print("Creating sample data...")
        create_sample_data(session)
        print("Sample data created successfully!")
    except Exception as e:
        print(f"Error creating sample data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main() 