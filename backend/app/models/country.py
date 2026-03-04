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


class DifficultyEnum(str, enum.Enum):
    """Flag difficulty enumeration."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EntityTypeEnum(str, enum.Enum):
    """Entity type enumeration."""
    SOVEREIGN_STATE = "sovereign_state"
    TERRITORY = "territory"
    US_STATE = "us_state"


class Country(Base):
    """Country model."""

    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    capital = Column(String(100), nullable=False)
    region = Column(Enum(RegionEnum, values_callable=lambda obj: [e.value for e in obj]), nullable=False, index=True)
    flag_url = Column(String(500), nullable=False)
    iso_code = Column(String(10), nullable=False, unique=True)
    alt_names = Column(ARRAY(String), nullable=True, default=list)
    is_independent = Column(Boolean, nullable=False, default=True, index=True)
    difficulty = Column(
        Enum(DifficultyEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=DifficultyEnum.MEDIUM,
        index=True
    )
    entity_type = Column(
        Enum(EntityTypeEnum, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=EntityTypeEnum.SOVEREIGN_STATE,
        index=True
    )
