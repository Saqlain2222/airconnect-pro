from typing import List, Optional, Dict
from datetime import datetime
from ..entities.database import Reservation, Journey, Account
from ..repositories.reservation_repository import ReservationRepository
from ..repositories.journey_repository import JourneyRepository
from sqlalchemy.orm import Session

class ReservationService:
    def __init__(self, session: Session):
        self.reservation_repo = ReservationRepository(session)
        self.journey_repo = JourneyRepository(session)

    def create_reservation(self, account_id: int, journey_id: int, seat_number: str) -> Optional[Dict]:
        """Create a new reservation with business logic validation."""
        # Validate journey exists and has available seats
        journey = self.journey_repo.get_by_id(journey_id)
        if not journey or journey.available_seats < 1:
            return None

        # Validate seat number format and availability
        if not self._is_valid_seat_number(seat_number, journey.aircraft_type):
            return None

        # Check if seat is already reserved
        if self._is_seat_taken(journey_id, seat_number):
            return None

        # Calculate total price
        total_price = self._calculate_reservation_price(journey_id, account_id)
        if total_price is None:
            return None

        # Create reservation
        reservation = self.reservation_repo.create_reservation(
            account_id=account_id,
            journey_id=journey_id,
            seat_number=seat_number,
            total_price=total_price
        )

        if reservation:
            return self.reservation_repo.get_reservation_details(reservation.id)
        return None

    def cancel_reservation(self, reservation_id: int, account_id: int) -> Optional[Dict]:
        """Cancel a reservation with business logic validation."""
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            return None

        # Validate account owns the reservation
        if reservation.account_id != account_id:
            return None

        # Check if cancellation is allowed (e.g., not too close to journey time)
        journey = self.journey_repo.get_by_id(reservation.journey_id)
        if not journey:
            return None

        hours_until_journey = (journey.departure_time - datetime.now()).total_seconds() / 3600
        if hours_until_journey < 24:  # Less than 24 hours before journey
            return None

        # Cancel reservation
        cancelled_reservation = self.reservation_repo.cancel_reservation(reservation_id)
        if cancelled_reservation:
            return self.reservation_repo.get_reservation_details(reservation_id)
        return None

    def get_account_reservations(self, account_id: int) -> List[Dict]:
        """Get all reservations for an account with business logic."""
        reservations = self.reservation_repo.get_account_reservations(account_id)
        
        # Format and filter results
        account_reservations = []
        for reservation in reservations:
            reservation_details = self.reservation_repo.get_reservation_details(reservation.id)
            if reservation_details:
                account_reservations.append(reservation_details)
        
        return account_reservations

    def get_reservation_history(self, account_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get reservation history for an account within a date range."""
        reservations = self.reservation_repo.get_reservations_by_date_range(start_date, end_date)
        
        # Filter for account's reservations and format results
        history = []
        for reservation in reservations:
            if reservation.account_id == account_id:
                reservation_details = self.reservation_repo.get_reservation_details(reservation.id)
                if reservation_details:
                    history.append(reservation_details)
        
        return history

    def _is_valid_seat_number(self, seat_number: str, aircraft_type: str) -> bool:
        """Validate seat number format based on aircraft type."""
        # Basic validation - can be extended based on specific aircraft types
        if not seat_number or len(seat_number) < 2:
            return False
        
        # Check if seat number follows the format: [row][letter]
        row = seat_number[:-1]
        letter = seat_number[-1].upper()
        
        try:
            row_num = int(row)
            if row_num < 1 or row_num > 50:  # Assuming max 50 rows
                return False
            if letter not in 'ABCDEFGHJK':  # Common seat letters (excluding I)
                return False
            return True
        except ValueError:
            return False

    def _is_seat_taken(self, journey_id: int, seat_number: str) -> bool:
        """Check if a seat is already reserved."""
        reservations = self.reservation_repo.get_journey_reservations(journey_id)
        return any(reservation.seat_number == seat_number and 
                  reservation.reservation_status == "confirmed" 
                  for reservation in reservations)

    def _calculate_reservation_price(self, journey_id: int, account_id: int) -> Optional[float]:
        """Calculate reservation price with business logic."""
        journey = self.journey_repo.get_by_id(journey_id)
        if not journey:
            return None

        # Get base price
        base_price = journey.base_price

        # Apply business rules
        # 1. Early reservation discount
        days_until_journey = (journey.departure_time - datetime.now()).days
        if days_until_journey > 30:
            base_price *= 0.9  # 10% discount
        elif days_until_journey < 7:
            base_price *= 1.2  # 20% surcharge

        # 2. Seat availability factor
        availability_factor = journey.available_seats / journey.total_seats
        if availability_factor < 0.2:
            base_price *= 1.15  # 15% surcharge

        # 3. Account loyalty discount (could be implemented based on account's reservation history)
        # This is a placeholder for future implementation
        # account = self.session.get(Account, account_id)
        # if account and self._is_loyal_customer(account_id):
        #     base_price *= 0.95  # 5% loyalty discount

        return round(base_price, 2) 