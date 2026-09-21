from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.infrastructure.database.models.base import Base


class DevelopmentModel(Base):
    __tablename__ = "desarrollos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    ciudad: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zona: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    propiedades: Mapped[List["PropertyModel"]] = relationship("PropertyModel", back_populates="desarrollo")


class PropertyModel(Base):
    __tablename__ = "propiedades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    recamaras: Mapped[int] = mapped_column(Integer, default=0)
    banos: Mapped[Decimal] = mapped_column(Numeric(3, 1), default=Decimal("0.0"))
    construccion_m2: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    terreno_m2: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    disponibilidad: Mapped[str] = mapped_column(String(50), default="Disponible")
    desarrollo_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("desarrollos.id"), nullable=True)

    desarrollo: Mapped[Optional["DevelopmentModel"]] = relationship("DevelopmentModel", back_populates="propiedades")


class FAQModel(Base):
    __tablename__ = "preguntas_frecuentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pregunta: Mapped[str] = mapped_column(String(255), nullable=False)
    respuesta: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
