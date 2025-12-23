import asyncio
from app.database.database import async_session_maker
from sqlalchemy import select
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash

async def seed_demo_accounts(): 
    async with async_session_maker() as db:
        # Accounts to create
        accounts = [
            {
                "email": "admin@iss.salerno.it",
                "username": "admin_salerno",
                "password": "AdminISS2025!",
                "role": UserRole.ADMIN,
                "nome": "Admin",
                "cognome": "Salerno"
            },
            {
                "email": "test_1758638182@example.com",
                "username": "test_aps",
                "password": "TestUser2025!",
                "role": UserRole.APS_RESPONSABILE,
                "nome": "Test",
                "cognome": "APS",
                "aps_nome_organizzazione": "Demo APS"
            }
        ]
        
        for acc_data in accounts:
            # Check if exists
            result = await db.execute(select(User).where(User.email == acc_data["email"]))
            existing = result.scalar_one_or_none()
            
            p_hash = get_password_hash(acc_data["password"])
            
            if existing:
                print(f"Updating existing account: {acc_data['email']}")
                existing.hashed_password = p_hash
                existing.role = acc_data["role"]
                existing.status = UserStatus.ACTIVE
                existing.is_email_verified = True
            else:
                print(f"Creating new account: {acc_data['email']}")
                user = User(
                    email=acc_data["email"],
                    username=acc_data["username"],
                    hashed_password=p_hash,
                    role=acc_data["role"],
                    status=UserStatus.ACTIVE,
                    is_email_verified=True,
                    nome=acc_data["nome"],
                    cognome=acc_data["cognome"],
                    aps_nome_organizzazione=acc_data.get("aps_nome_organizzazione")
                )
                db.add(user)
        
        await db.commit()
        print("✅ Demo accounts seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_demo_accounts())
