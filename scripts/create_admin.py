"""Crea una cuenta administrativa local sin pasar la contraseña por argumentos."""

import argparse
import asyncio
import secrets

from sqlalchemy import select

from src.infrastructure.config.settings import Settings
from src.infrastructure.database.session import DatabaseManager
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

async def create(email: str, name: str) -> None:
    settings = Settings()
    password = secrets.token_urlsafe(24)
    manager = DatabaseManager(settings)
    try:
        async with manager.session_factory() as session:
            existing = await session.scalar(select(UserModel).where(UserModel.email == email))
            if existing:
                raise SystemExit(f"Ya existe una cuenta con el correo {email}; no se modificó.")
            user = UserModel(
                email=email,
                full_name=name,
                password_hash=BcryptPasswordHasher().hash_password(password),
                role="admin",
                permissions=["*"],
                is_active=True,
            )
            session.add(user)
            await session.commit()
            print(f"Cuenta admin creada: {email}\nContraseña temporal: {password}")
    finally:
        await manager.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crear una cuenta con acceso completo al panel")
    parser.add_argument("email", help="Correo de la nueva cuenta")
    parser.add_argument("--name", default="Administrador", help="Nombre visible")
    args = parser.parse_args()
    asyncio.run(create(args.email.strip().lower(), args.name))
