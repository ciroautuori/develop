from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.admin import AdminUser
from app.schemas.admin import AdminUserCreate
from app.core.security import get_password_hash, verify_password


async def get_admin_by_username(db: AsyncSession, username: str) -> Optional[AdminUser]:
    query = select(AdminUser).where(AdminUser.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_admin_user(db: AsyncSession, admin: AdminUserCreate) -> AdminUser:
    hashed_password = get_password_hash(admin.password)
    db_admin = AdminUser(
        username=admin.username,
        hashed_password=hashed_password
    )
    db.add(db_admin)
    await db.commit()
    await db.refresh(db_admin)
    return db_admin


async def authenticate_admin(db: AsyncSession, username: str, password: str) -> Optional[AdminUser]:
    admin = await get_admin_by_username(db, username)
    if not admin:
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin
