"""Base Repository Pattern Implementation
Generic repository for database operations following DDD principles.

This provides:
- CRUD operations abstraction
- Type-safe queries with generics
- Testability through interface
- Centralized data access logic
"""

from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.infrastructure.database.session import Base

# Generic type for entities
T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository for database operations.
    
    Provides standard CRUD operations for any SQLAlchemy model.
    Extend this class for domain-specific repositories.
    
    Example:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: Session):
                super().__init__(User, db)
            
            def get_by_email(self, email: str) -> Optional[User]:
                return self.db.query(self.model).filter(
                    self.model.email == email
                ).first()
    """

    def __init__(self, model: type[T], db: Session):
        """Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> T | None:
        """Get entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity instance or None if not found
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int | None = None, offset: int | None = None) -> list[T]:
        """Get all entities with optional pagination.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of entities
        """
        query = self.db.query(self.model)

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def get_by_filters(self, filters: dict[str, Any]) -> list[T]:
        """Get entities matching filters.
        
        Args:
            filters: Dictionary of field->value filters
            
        Returns:
            List of matching entities
            
        Example:
            repo.get_by_filters({"is_active": True, "role": "admin"})
        """
        query = self.db.query(self.model)

        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        return query.all()

    def create(self, entity: T) -> T:
        """Create new entity.
        
        Args:
            entity: Entity instance to create
            
        Returns:
            Created entity with ID populated
            
        Note:
            Does NOT commit transaction. Call db.commit() explicitly.
        """
        self.db.add(entity)
        self.db.flush()  # Flush to get ID without committing
        self.db.refresh(entity)
        return entity

    def create_many(self, entities: list[T]) -> list[T]:
        """Bulk create entities.
        
        Args:
            entities: List of entities to create
            
        Returns:
            List of created entities
        """
        self.db.add_all(entities)
        self.db.flush()
        return entities

    def update(self, entity: T) -> T:
        """Update existing entity.
        
        Args:
            entity: Entity instance with updated values
            
        Returns:
            Updated entity
            
        Note:
            Entity must be attached to session.
            Does NOT commit transaction.
        """
        self.db.flush()
        self.db.refresh(entity)
        return entity

    def update_by_id(self, id: int, data: dict[str, Any]) -> T | None:
        """Update entity by ID with dict of values.
        
        Args:
            id: Entity identifier
            data: Dictionary of field->value updates
            
        Returns:
            Updated entity or None if not found
        """
        entity = self.get_by_id(id)
        if not entity:
            return None

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.db.flush()
        self.db.refresh(entity)
        return entity

    def delete(self, entity: T) -> None:
        """Delete entity.
        
        Args:
            entity: Entity instance to delete
            
        Note:
            Does NOT commit transaction.
        """
        self.db.delete(entity)
        self.db.flush()

    def delete_by_id(self, id: int) -> bool:
        """Delete entity by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(id)
        if not entity:
            return False

        self.delete(entity)
        return True

    def exists(self, id: int) -> bool:
        """Check if entity exists by ID.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(self.model.id).filter(self.model.id == id).scalar() is not None

    def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count entities matching optional filters.
        
        Args:
            filters: Optional dictionary of field->value filters
            
        Returns:
            Count of matching entities
        """
        query = self.db.query(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.count()

    def commit(self) -> None:
        """Commit current transaction.
        
        Note:
            Use this when repository manages transaction lifecycle.
            For service-level transaction management, commit from service.
        """
        self.db.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.db.rollback()

    def refresh(self, entity: T) -> T:
        """Refresh entity from database.
        
        Args:
            entity: Entity instance to refresh
            
        Returns:
            Refreshed entity
        """
        self.db.refresh(entity)
        return entity

    def paginate(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        desc: bool = False
    ) -> dict[str, Any]:
        """Paginate query results with optional filters and ordering.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            filters: Optional dictionary of field->value filters
            order_by: Optional field name to order by
            desc: If True, order descending (default: ascending)
            
        Returns:
            Dictionary with:
                - items: List of entities for current page
                - total: Total number of entities
                - page: Current page number
                - per_page: Items per page
                - pages: Total number of pages
                - has_next: Boolean indicating if next page exists
                - has_prev: Boolean indicating if previous page exists
        
        Example:
            result = repo.paginate(page=2, per_page=10, order_by='created_at', desc=True)
            items = result['items']
            total_pages = result['pages']
        """
        # Build base query
        query = self.db.query(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        # Get total count
        total = query.count()

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(order_column.desc() if desc else order_column.asc())

        # Calculate pagination
        pages = (total + per_page - 1) // per_page  # Ceiling division
        page = max(1, min(page, pages if pages > 0 else 1))  # Clamp page number

        # Apply pagination
        offset = (page - 1) * per_page
        items = query.limit(per_page).offset(offset).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1
        }

    def get_or_create(
        self,
        filters: dict[str, Any],
        defaults: dict[str, Any] | None = None
    ) -> tuple[T, bool]:
        """Get existing entity or create new one if not found.
        
        Args:
            filters: Dictionary of field->value to search for
            defaults: Optional dictionary of additional fields for creation
            
        Returns:
            Tuple of (entity, created) where created is True if entity was created
            
        Example:
            user, created = repo.get_or_create(
                filters={'email': 'test@example.com'},
                defaults={'full_name': 'Test User', 'role': 'user'}
            )
        """
        # Try to find existing
        query = self.db.query(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)

        entity = query.first()

        if entity:
            return entity, False

        # Create new entity
        create_data = {**filters}
        if defaults:
            create_data.update(defaults)

        entity = self.model(**create_data)
        self.db.add(entity)
        self.db.flush()  # Flush to get ID without committing

        return entity, True
