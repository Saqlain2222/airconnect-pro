# SkyLink Airways - Airline Reservation and Management System

A comprehensive database system for managing airline operations, built using Python, SQLite, and MongoDB.

## Project Overview

This system provides a complete solution for managing:
- Flight scheduling and management
- Passenger reservations and ticketing
- Crew management
- Customer service and support
- Operational analytics and reporting

## Architecture

The system follows a four-tier architecture:
1. Presentation Layer (PL)
2. Business Logic Layer (BLL)
3. Data Access Layer (DAL)
4. Database Layer (DBL)

## Features

- Normalized database design using SQLite
- Hybrid solution incorporating MongoDB for specific use cases
- Secure data access and management
- Comprehensive CRUD operations
- Advanced querying capabilities
- Data integrity constraints
- Performance optimization
- Version control using Git

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python src/init_db.py
   ```
5. Run the application:
   ```bash
   python src/main.py
   ```

## Project Structure

```
project/
├── src/
│   ├── dal/           # Data Access Layer
│   ├── bll/           # Business Logic Layer
│   ├── pl/            # Presentation Layer
│   ├── models/        # Database Models
│   ├── utils/         # Utility Functions
│   └── tests/         # Test Cases
├── data/              # Data Files
├── docs/              # Documentation
├── requirements.txt   # Project Dependencies
└── README.md         # Project Documentation
```

## Testing

Run tests using pytest:
```bash
pytest src/tests/
```

## Security Considerations

- Password hashing
- Input validation
- SQL injection prevention
- Data encryption
- Access control

## Performance Optimization

- Indexed queries
- Connection pooling
- Query optimization
- Caching mechanisms

## License

This project is created for educational purposes as part of the CPS7003B Database Systems module. 