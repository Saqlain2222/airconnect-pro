from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy import select

T = TypeVar('T')

class BaseDAL(Generic[T]):
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    def create(self, **kwargs) -> T:
        """Create a new record."""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by its ID."""
        return self.session.get(self.model_class, id)

    def get_all(self) -> List[T]:
        """Get all records."""
        stmt = select(self.model_class)
        return list(self.session.execute(stmt).scalars().all())

    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update a record by its ID."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.session.commit()
        return instance

    def delete(self, id: int) -> bool:
        """Delete a record by its ID."""
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False

    def filter_by(self, **kwargs) -> List[T]:
        """Filter records by given criteria."""
        stmt = select(self.model_class).filter_by(**kwargs)
        return list(self.session.execute(stmt).scalars().all()) 