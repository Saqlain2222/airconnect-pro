from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import os
from dotenv import load_dotenv

from app.entities.database import init_db, get_db, User, Flight, Booking
from app.dto import (
    UserCreate, UserResponse, Token, FlightCreate, FlightResponse,
    BookingCreate, BookingResponse, FlightSearch, BookingHistory
)
from app.security import (
    get_current_active_user, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, verify_password
)
from app.services.flight_service import FlightService
from app.services.booking_service import BookingService
from app.repositories.user_dal import UserDAL

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AirConnect Pro",
    description="Advanced Flight Management and Reservation System",
    version="1.0.0"
)

# Initialize database
init_db()

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Web Routes
@app.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user_repo = UserDAL(db)
    user = user_repo.authenticate(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password"}
        )
    
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/flights", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/flights")
async def flights_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    flight_manager = FlightService(db)
    available_flights = flight_manager.get_all_flights()
    return templates.TemplateResponse(
        "flights.html",
        {"request": request, "flights": available_flights, "user": current_user}
    )

@app.post("/flights/search")
async def search_flights_web(
    request: Request,
    departure_airport: str = Form(...),
    arrival_airport: str = Form(...),
    date: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    flight_manager = FlightService(db)
    search_date = datetime.strptime(date, "%Y-%m-%d")
    available_flights = flight_manager.search_available_flights(
        departure_airport,
        arrival_airport,
        search_date
    )
    return templates.TemplateResponse(
        "flights.html",
        {"request": request, "flights": available_flights, "user": current_user}
    )

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# API Routes
@app.post("/token", response_model=Token)
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user_repo = UserDAL(db)
    user = user_repo.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_expiry = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=token_expiry
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/users/", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserDAL(db)
    existing_user = user_repo.get_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_repo.create_user(
        username=user.username,
        email=user.email,
        password=user.password,
        role=user.role
    )

@app.get("/api/flights/", response_model=List[FlightResponse])
async def get_flights(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    flight_manager = FlightService(db)
    return flight_manager.get_all_flights(skip=skip, limit=limit)

@app.post("/api/flights/search", response_model=List[FlightResponse])
async def search_flights(
    search: FlightSearch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    flight_manager = FlightService(db)
    return flight_manager.search_available_flights(
        search.departure_airport,
        search.arrival_airport,
        search.date
    )

@app.post("/api/flights/", response_model=FlightResponse)
async def create_flight(
    flight: FlightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create flights")
    flight_manager = FlightService(db)
    return flight_manager.create_flight(flight)

@app.post("/api/bookings/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking_manager = BookingService(db)
    return booking_manager.create_booking(
        user_id=current_user.id,
        flight_id=booking.flight_id,
        seat_number=booking.seat_number
    )

@app.get("/api/bookings/", response_model=List[BookingResponse])
async def get_user_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking_manager = BookingService(db)
    return booking_manager.get_user_bookings(current_user.id)

@app.post("/api/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking_manager = BookingService(db)
    result = booking_manager.cancel_booking(booking_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found or cannot be cancelled")
    return result

@app.post("/api/bookings/history", response_model=List[BookingResponse])
async def get_booking_history(
    history: BookingHistory,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    booking_manager = BookingService(db)
    return booking_manager.get_booking_history(
        current_user.id,
        history.start_date,
        history.end_date
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 