"""Async Base Repository Pattern Implementation.

Provides async/await support for database operations using SQLAlchemy 2.0 async features.
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import Base

# Generic type for entities
T = TypeVar('T', bound=Base)


class AsyncBaseRepository(Generic[T]):
    """Generic async repository for database operations.
    
    Provides standard async CRUD operations for any SQLAlchemy model.
    Extend this class for domain-specific async repositories.
    
    Example:
        class UserRepository(AsyncBaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(User, db)
            
            async def get_by_email(self, email: str) -> Optional[User]:
                result = await self.db.execute(
                    select(self.model).where(self.model.email == email)
                )
                return result.scalar_one_or_none()
    """

    def __init__(self, model: Type[T], db: AsyncSession):
        """Initialize async repository.
        
        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID asynchronously.
        
        Args:
            id: Entity identifier
            
        Returns:
            Entity if found, None otherwise
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """Get all entities with optional pagination.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities
        """
        query = select(self.model)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Create new entity asynchronously.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity with generated ID
        """
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Update existing entity asynchronously.
        
        Args:
            entity: Entity with updated values
            
        Returns:
            Updated entity
        """
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: T) -> bool:
        """Delete entity asynchronously.
        
        Args:
            entity: Entity to delete
            
        Returns:
            True if deleted successfully
        """
        await self.db.delete(entity)
        await self.db.flush()
        return True

    async def delete_by_id(self, id: int) -> bool:
        """Delete entity by ID asynchronously.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.flush()
        return result.rowcount > 0

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching optional filters asynchronously.
        
        Args:
            filters: Optional dictionary of field->value filters
            
        Returns:
            Count of matching entities
        """
        query = select(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        result = await self.db.execute(query)
        return len(list(result.scalars().all()))

    async def exists(self, id: int) -> bool:
        """Check if entity exists by ID asynchronously.
        
        Args:
            id: Entity identifier
            
        Returns:
            True if exists, False otherwise
        """
        result = await self.db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None

    async def paginate(
        self, 
        page: int = 1, 
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        desc: bool = False
    ) -> Dict[str, Any]:
        """Paginate query results asynchronously.
        
        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page
            filters: Optional dictionary of field->value filters
            order_by: Optional field name to order by
            desc: If True, order descending
            
        Returns:
            Dictionary with pagination data
        """
        query = select(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
        
        # Get total count
        count_result = await self.db.execute(query)
        total = len(list(count_result.scalars().all()))
        
        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            query = query.order_by(order_column.desc() if desc else order_column.asc())
        
        # Calculate pagination
        pages = (total + per_page - 1) // per_page
        page = max(1, min(page, pages if pages > 0 else 1))
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.limit(per_page).offset(offset)
        
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'has_next': page < pages,
            'has_prev': page > 1
        }

    async def get_or_create(
        self,
        filters: Dict[str, Any],
        defaults: Optional[Dict[str, Any]] = None
    ) -> tuple[T, bool]:
        """Get existing entity or create new one asynchronously.
        
        Args:
            filters: Dictionary of field->value to search for
            defaults: Optional dictionary of additional fields for creation
            
        Returns:
            Tuple of (entity, created) where created is True if entity was created
        """
        # Try to find existing
        query = select(self.model)
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)
        
        result = await self.db.execute(query)
        entity = result.scalar_one_or_none()
        
        if entity:
            return entity, False
        
        # Create new entity
        create_data = {**filters}
        if defaults:
            create_data.update(defaults)
        
        entity = self.model(**create_data)
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        
        return entity, True

    async def commit(self) -> None:
        """Commit current transaction asynchronously."""
        await self.db.commit()

    async def rollback(self) -> None:
        """Rollback current transaction asynchronously."""
        await self.db.rollback()

    async def refresh(self, entity: T) -> T:
        """Refresh entity from database asynchronously.
        
        Args:
            entity: Entity instance to refresh
            
        Returns:
            Refreshed entity
        """
        await self.db.refresh(entity)
        return entity
