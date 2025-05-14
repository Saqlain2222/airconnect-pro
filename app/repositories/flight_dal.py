from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from typing import List, Optional
from datetime import datetime
from ..models.database import Flight, FlightStatus, Airport
from .base_dal import BaseDAL

class FlightDAL(BaseDAL[Flight]):
    def __init__(self, session: Session):
        super().__init__(session, Flight)

    def get_flights_by_route(self, departure_airport_id: int, arrival_airport_id: int) -> List[Flight]:
        """Get all flights between two airports."""
        return self.filter_by(
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id
        )

    def get_flights_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Flight]:
        """Get all flights within a date range."""
        stmt = select(Flight).where(
            and_(
                Flight.departure_time >= start_date,
                Flight.departure_time <= end_date
            )
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_available_flights(self) -> List[Flight]:
        """Get all flights with available seats."""
        stmt = select(Flight).where(Flight.available_seats > 0)
        return list(self.session.execute(stmt).scalars().all())

    def get_flights_by_status(self, status: FlightStatus) -> List[Flight]:
        """Get all flights with a specific status."""
        return self.filter_by(status=status)

    def search_flights(self, departure_airport: str, arrival_airport: str, date: datetime) -> List[Flight]:
        """Search flights by departure airport, arrival airport, and date."""
        stmt = select(Flight).join(
            Airport, Flight.departure_airport_id == Airport.id
        ).join(
            Airport, Flight.arrival_airport_id == Airport.id
        ).where(
            and_(
                Airport.code == departure_airport,
                Airport.code == arrival_airport,
                Flight.departure_time >= date,
                Flight.departure_time < date.replace(hour=23, minute=59, second=59)
            )
        )
        return list(self.session.execute(stmt).scalars().all())

    def update_flight_status(self, flight_id: int, new_status: FlightStatus) -> Optional[Flight]:
        """Update the status of a flight."""
        return self.update(flight_id, status=new_status)

    def update_available_seats(self, flight_id: int, seats_to_reserve: int) -> Optional[Flight]:
        """Update the number of available seats on a flight."""
        flight = self.get_by_id(flight_id)
        if flight and flight.available_seats >= seats_to_reserve:
            new_available_seats = flight.available_seats - seats_to_reserve
            return self.update(flight_id, available_seats=new_available_seats)
        return None

    def get_flight_details(self, flight_id: int) -> Optional[dict]:
        """Get detailed information about a flight including airport details."""
        flight = self.get_by_id(flight_id)
        if flight:
            return {
                'flight_number': flight.flight_number,
                'departure_airport': flight.departure_airport.name,
                'arrival_airport': flight.arrival_airport.name,
                'departure_time': flight.departure_time,
                'arrival_time': flight.arrival_time,
                'status': flight.status.value,
                'available_seats': flight.available_seats,
                'base_price': flight.base_price
            }
        return None 