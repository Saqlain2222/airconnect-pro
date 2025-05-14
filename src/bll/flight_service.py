from typing import List, Optional, Dict
from datetime import datetime
from ..models.database import Flight, FlightStatus
from ..dal.flight_dal import FlightDAL
from sqlalchemy.orm import Session

class FlightService:
    def __init__(self, session: Session):
        self.flight_dal = FlightDAL(session)

    def search_available_flights(self, departure_airport: str, arrival_airport: str, 
                               date: datetime) -> List[Dict]:
        """Search for available flights with business logic validation."""
        # Validate date is not in the past
        if date < datetime.now():
            return []

        # Search for flights
        flights = self.flight_dal.search_flights(departure_airport, arrival_airport, date)
        
        # Filter and format results
        available_flights = []
        for flight in flights:
            if flight.available_seats > 0 and flight.status == FlightStatus.SCHEDULED:
                flight_details = self.flight_dal.get_flight_details(flight.id)
                if flight_details:
                    available_flights.append(flight_details)
        
        return available_flights

    def update_flight_status(self, flight_id: int, new_status: FlightStatus) -> Optional[Dict]:
        """Update flight status with business logic validation."""
        flight = self.flight_dal.get_by_id(flight_id)
        if not flight:
            return None

        # Validate status transition
        valid_transitions = {
            FlightStatus.SCHEDULED: [FlightStatus.BOARDING, FlightStatus.DELAYED, FlightStatus.CANCELLED],
            FlightStatus.BOARDING: [FlightStatus.COMPLETED, FlightStatus.DELAYED],
            FlightStatus.DELAYED: [FlightStatus.SCHEDULED, FlightStatus.CANCELLED],
            FlightStatus.CANCELLED: [FlightStatus.SCHEDULED],
            FlightStatus.COMPLETED: []
        }

        if new_status not in valid_transitions.get(flight.status, []):
            return None

        # Update status
        updated_flight = self.flight_dal.update_flight_status(flight_id, new_status)
        if updated_flight:
            return self.flight_dal.get_flight_details(flight_id)
        return None

    def get_flight_availability(self, flight_id: int) -> Optional[Dict]:
        """Get flight availability with business logic."""
        flight = self.flight_dal.get_by_id(flight_id)
        if not flight:
            return None

        # Calculate availability percentage
        availability_percentage = (flight.available_seats / flight.total_seats) * 100

        return {
            'flight_number': flight.flight_number,
            'total_seats': flight.total_seats,
            'available_seats': flight.available_seats,
            'availability_percentage': availability_percentage,
            'status': flight.status.value
        }

    def get_flights_by_route(self, departure_airport_id: int, arrival_airport_id: int) -> List[Dict]:
        """Get flights by route with business logic."""
        flights = self.flight_dal.get_flights_by_route(departure_airport_id, arrival_airport_id)
        
        # Format and filter results
        route_flights = []
        for flight in flights:
            if flight.status != FlightStatus.CANCELLED:
                flight_details = self.flight_dal.get_flight_details(flight.id)
                if flight_details:
                    route_flights.append(flight_details)
        
        return route_flights

    def calculate_flight_price(self, flight_id: int, seat_count: int = 1) -> Optional[float]:
        """Calculate flight price with business logic."""
        flight = self.flight_dal.get_by_id(flight_id)
        if not flight:
            return None

        # Basic price calculation
        base_price = flight.base_price

        # Apply business rules for pricing
        # 1. Early booking discount (if booking is more than 30 days in advance)
        days_until_flight = (flight.departure_time - datetime.now()).days
        if days_until_flight > 30:
            base_price *= 0.9  # 10% discount

        # 2. Last-minute booking surcharge (if booking is less than 7 days in advance)
        elif days_until_flight < 7:
            base_price *= 1.2  # 20% surcharge

        # 3. Apply seat availability factor
        availability_factor = flight.available_seats / flight.total_seats
        if availability_factor < 0.2:  # Less than 20% seats available
            base_price *= 1.15  # 15% surcharge

        return round(base_price * seat_count, 2) 