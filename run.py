import uvicorn
from app.app import app
from app.entities.database import initialize_database

if __name__ == "__main__":
    # Initialize the database
    initialize_database()
    
    # Run the application
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 