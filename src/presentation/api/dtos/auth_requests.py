from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, Field


# Pydantic Schemas
class LoginBody(BaseModel):
    email: str = Field(..., min_length=3, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, description="Contraseña")


class RegisterBody(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, description="Contraseña")
    full_name: str = Field(..., min_length=2, max_length=255, description="Nombre completo")
    role: str = Field(default="customer", description="Rol del usuario (admin, agent, customer)")


# Encapsulated Presentation DTOs with @dataclass
@dataclass
class LoginRequestDTO:
    email: str
    password: str


@dataclass
class RegisterRequestDTO:
    email: str
    password: str
    full_name: str
    role: str
