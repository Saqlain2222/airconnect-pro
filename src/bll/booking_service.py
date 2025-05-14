from typing import List, Optional, Dict
from datetime import datetime
from ..models.database import Booking, Flight, User
from ..dal.booking_dal import BookingDAL
from ..dal.flight_dal import FlightDAL
from sqlalchemy.orm import Session

class BookingService:
    def __init__(self, session: Session):
        self.booking_dal = BookingDAL(session)
        self.flight_dal = FlightDAL(session)

    def create_booking(self, user_id: int, flight_id: int, seat_number: str) -> Optional[Dict]:
        """Create a new booking with business logic validation."""
        # Validate flight exists and has available seats
        flight = self.flight_dal.get_by_id(flight_id)
        if not flight or flight.available_seats < 1:
            return None

        # Validate seat number format and availability
        if not self._is_valid_seat_number(seat_number, flight.aircraft_type):
            return None

        # Check if seat is already booked
        if self._is_seat_taken(flight_id, seat_number):
            return None

        # Calculate total price
        total_price = self._calculate_booking_price(flight_id, user_id)
        if total_price is None:
            return None

        # Create booking
        booking = self.booking_dal.create_booking(
            user_id=user_id,
            flight_id=flight_id,
            seat_number=seat_number,
            total_price=total_price
        )

        if booking:
            return self.booking_dal.get_booking_details(booking.id)
        return None

    def cancel_booking(self, booking_id: int, user_id: int) -> Optional[Dict]:
        """Cancel a booking with business logic validation."""
        booking = self.booking_dal.get_by_id(booking_id)
        if not booking:
            return None

        # Validate user owns the booking
        if booking.user_id != user_id:
            return None

        # Check if cancellation is allowed (e.g., not too close to flight time)
        flight = self.flight_dal.get_by_id(booking.flight_id)
        if not flight:
            return None

        hours_until_flight = (flight.departure_time - datetime.now()).total_seconds() / 3600
        if hours_until_flight < 24:  # Less than 24 hours before flight
            return None

        # Cancel booking
        cancelled_booking = self.booking_dal.cancel_booking(booking_id)
        if cancelled_booking:
            return self.booking_dal.get_booking_details(booking_id)
        return None

    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Get all bookings for a user with business logic."""
        bookings = self.booking_dal.get_user_bookings(user_id)
        
        # Format and filter results
        user_bookings = []
        for booking in bookings:
            booking_details = self.booking_dal.get_booking_details(booking.id)
            if booking_details:
                user_bookings.append(booking_details)
        
        return user_bookings

    def get_booking_history(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get booking history for a user within a date range."""
        bookings = self.booking_dal.get_bookings_by_date_range(start_date, end_date)
        
        # Filter for user's bookings and format results
        history = []
        for booking in bookings:
            if booking.user_id == user_id:
                booking_details = self.booking_dal.get_booking_details(booking.id)
                if booking_details:
                    history.append(booking_details)
        
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

    def _is_seat_taken(self, flight_id: int, seat_number: str) -> bool:
        """Check if a seat is already booked."""
        bookings = self.booking_dal.get_flight_bookings(flight_id)
        return any(booking.seat_number == seat_number and 
                  booking.booking_status == "confirmed" 
                  for booking in bookings)

    def _calculate_booking_price(self, flight_id: int, user_id: int) -> Optional[float]:
        """Calculate booking price with business logic."""
        flight = self.flight_dal.get_by_id(flight_id)
        if not flight:
            return None

        # Get base price
        base_price = flight.base_price

        # Apply business rules
        # 1. Early booking discount
        days_until_flight = (flight.departure_time - datetime.now()).days
        if days_until_flight > 30:
            base_price *= 0.9  # 10% discount
        elif days_until_flight < 7:
            base_price *= 1.2  # 20% surcharge

        # 2. Seat availability factor
        availability_factor = flight.available_seats / flight.total_seats
        if availability_factor < 0.2:
            base_price *= 1.15  # 15% surcharge

        # 3. User loyalty discount (could be implemented based on user's booking history)
        # This is a placeholder for future implementation
        # user = self.session.get(User, user_id)
        # if user and self._is_loyal_customer(user_id):
        #     base_price *= 0.95  # 5% loyalty discount

        return round(base_price, 2) 