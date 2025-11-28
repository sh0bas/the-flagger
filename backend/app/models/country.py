"""Country model."""
import enum

from sqlalchemy import Boolean, Column, Enum, Integer, String, ARRAY


from app.core.database import Base


class RegionEnum(str, enum.Enum):
    """Geographic region enumeration."""
    AMERICAS = "americas"
    EUROPE = "europe"
    AFRICA = "africa"
    ASIA = "asia"
    OCEANIA = "oceania"


class Country(Base):
    """Country model."""
    
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    capital = Column(String(100), nullable=False)
    region = Column(Enum(RegionEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)
    flag_url = Column(String(500), nullable=False)
    iso_code = Column(String(2), nullable=False, unique=True)
    alt_names = Column(ARRAY(String), nullable=True, default=list)
    is_independent = Column(Boolean, nullable=False, default=True, index=True)
