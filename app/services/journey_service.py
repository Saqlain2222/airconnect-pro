from typing import List, Optional, Dict
from datetime import datetime
from ..entities.database import Journey, JourneyState
from ..repositories.journey_repository import JourneyRepository
from sqlalchemy.orm import Session

class JourneyService:
    def __init__(self, session: Session):
        self.journey_repo = JourneyRepository(session)

    def search_available_journeys(self, departure_terminal: str, arrival_terminal: str, 
                               date: datetime) -> List[Dict]:
        """Search for available journeys with business logic validation."""
        # Validate date is not in the past
        if date < datetime.now():
            return []

        # Search for journeys
        journeys = self.journey_repo.search_journeys(departure_terminal, arrival_terminal, date)
        
        # Filter and format results
        available_journeys = []
        for journey in journeys:
            if journey.available_seats > 0 and journey.status == JourneyState.PLANNED:
                journey_details = self.journey_repo.get_journey_details(journey.id)
                if journey_details:
                    available_journeys.append(journey_details)
        
        return available_journeys

    def update_journey_status(self, journey_id: int, new_status: JourneyState) -> Optional[Dict]:
        """Update journey status with business logic validation."""
        journey = self.journey_repo.get_by_id(journey_id)
        if not journey:
            return None

        # Validate status transition
        valid_transitions = {
            JourneyState.PLANNED: [JourneyState.DEPARTING, JourneyState.LATE, JourneyState.ABORTED],
            JourneyState.DEPARTING: [JourneyState.FINISHED, JourneyState.LATE],
            JourneyState.LATE: [JourneyState.PLANNED, JourneyState.ABORTED],
            JourneyState.ABORTED: [JourneyState.PLANNED],
            JourneyState.FINISHED: []
        }

        if new_status not in valid_transitions.get(journey.status, []):
            return None

        # Update status
        updated_journey = self.journey_repo.update_journey_status(journey_id, new_status)
        if updated_journey:
            return self.journey_repo.get_journey_details(journey_id)
        return None

    def get_journey_availability(self, journey_id: int) -> Optional[Dict]:
        """Get journey availability with business logic."""
        journey = self.journey_repo.get_by_id(journey_id)
        if not journey:
            return None

        # Calculate availability percentage
        availability_percentage = (journey.available_seats / journey.total_seats) * 100

        return {
            'flight_number': journey.flight_number,
            'total_seats': journey.total_seats,
            'available_seats': journey.available_seats,
            'availability_percentage': availability_percentage,
            'status': journey.status.value
        }

    def get_journeys_by_route(self, departure_terminal_id: int, arrival_terminal_id: int) -> List[Dict]:
        """Get journeys by route with business logic."""
        journeys = self.journey_repo.get_journeys_by_route(departure_terminal_id, arrival_terminal_id)
        
        # Format and filter results
        route_journeys = []
        for journey in journeys:
            if journey.status != JourneyState.ABORTED:
                journey_details = self.journey_repo.get_journey_details(journey.id)
                if journey_details:
                    route_journeys.append(journey_details)
        
        return route_journeys

    def calculate_journey_price(self, journey_id: int, seat_count: int = 1) -> Optional[float]:
        """Calculate journey price with business logic."""
        journey = self.journey_repo.get_by_id(journey_id)
        if not journey:
            return None

        # Basic price calculation
        base_price = journey.base_price

        # Apply business rules for pricing
        # 1. Early booking discount (if booking is more than 30 days in advance)
        days_until_journey = (journey.departure_time - datetime.now()).days
        if days_until_journey > 30:
            base_price *= 0.9  # 10% discount

        # 2. Last-minute booking surcharge (if booking is less than 7 days in advance)
        elif days_until_journey < 7:
            base_price *= 1.2  # 20% surcharge

        # 3. Apply seat availability factor
        availability_factor = journey.available_seats / journey.total_seats
        if availability_factor < 0.2:  # Less than 20% seats available
            base_price *= 1.15  # 15% surcharge

        return round(base_price * seat_count, 2) 