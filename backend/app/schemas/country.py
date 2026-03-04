"""Country schema."""
from pydantic import BaseModel


class CountryResponse(BaseModel):
    """Country response schema."""
    id: int
    name: str
    capital: str
    region: str
    flag_url: str
    iso_code: str
    alt_names: list[str] = []
    is_independent: bool
    difficulty: str = "medium"
    entity_type: str = "sovereign_state"

    class Config:
        from_attributes = True


class CapitalResponse(BaseModel):
    """Capital response schema (for autocomplete)."""
    name: str
    country: str
