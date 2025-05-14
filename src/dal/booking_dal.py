from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime
from ..models.database import Booking, Flight, User
from .base_dal import BaseDAL

class BookingDAL(BaseDAL[Booking]):
    def __init__(self, session: Session):
        super().__init__(session, Booking)

    def create_booking(self, user_id: int, flight_id: int, seat_number: str, total_price: float) -> Optional[Booking]:
        """Create a new booking and update flight availability."""
        # Check if the flight exists and has available seats
        flight = self.session.get(Flight, flight_id)
        if not flight or flight.available_seats < 1:
            return None

        # Create the booking
        booking = self.create(
            user_id=user_id,
            flight_id=flight_id,
            seat_number=seat_number,
            booking_status="confirmed",
            total_price=total_price
        )

        # Update flight availability
        flight.available_seats -= 1
        self.session.commit()

        return booking

    def get_user_bookings(self, user_id: int) -> List[Booking]:
        """Get all bookings for a specific user."""
        return self.filter_by(user_id=user_id)

    def get_flight_bookings(self, flight_id: int) -> List[Booking]:
        """Get all bookings for a specific flight."""
        return self.filter_by(flight_id=flight_id)

    def get_active_bookings(self) -> List[Booking]:
        """Get all active bookings."""
        return self.filter_by(booking_status="confirmed")

    def cancel_booking(self, booking_id: int) -> Optional[Booking]:
        """Cancel a booking and update flight availability."""
        booking = self.get_by_id(booking_id)
        if booking and booking.booking_status == "confirmed":
            # Update booking status
            booking = self.update(booking_id, booking_status="cancelled")
            
            # Update flight availability
            flight = self.session.get(Flight, booking.flight_id)
            if flight:
                flight.available_seats += 1
                self.session.commit()
            
            return booking
        return None

    def get_booking_details(self, booking_id: int) -> Optional[dict]:
        """Get detailed information about a booking."""
        booking = self.get_by_id(booking_id)
        if booking:
            return {
                'booking_id': booking.id,
                'user': {
                    'id': booking.user.id,
                    'username': booking.user.username,
                    'email': booking.user.email
                },
                'flight': {
                    'flight_number': booking.flight.flight_number,
                    'departure_airport': booking.flight.departure_airport.name,
                    'arrival_airport': booking.flight.arrival_airport.name,
                    'departure_time': booking.flight.departure_time
                },
                'seat_number': booking.seat_number,
                'booking_status': booking.booking_status,
                'total_price': booking.total_price,
                'booking_date': booking.booking_date
            }
        return None

    def get_bookings_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Booking]:
        """Get all bookings within a date range."""
        stmt = select(Booking).where(
            and_(
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date
            )
        )
        return list(self.session.execute(stmt).scalars().all()) 