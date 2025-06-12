from pydantic import BaseModel, Field, AliasChoices
from typing import Optional

class CombatStats(BaseModel):
    """Represents core combat stats."""
    hp: int = Field(ge=1, description="Hit Points")
    str: int = Field(ge=0, description="Strength")
    mag: int = Field(ge=0, description="Magic")
    skl: int = Field(ge=0, description="Skill") # No 'dex' alias needed for FE9 example
    spd: int = Field(ge=0, description="Speed")
    lck: int = Field(ge=0, description="Luck")
    def_: int = Field(ge=0, alias="def", description="Defense")
    res: int = Field(ge=0, description="Resistance")

class BaseStats(CombatStats):
    """A unit's base stats, including Movement and Weight."""
    mov: int = Field(ge=0, description="Movement")
    wgt: int = Field(ge=0, description="Weight")

class GrowthRates(CombatStats):
    """A unit's percentage growth rates per level."""
    pass # Inherits all fields from CombatStats

class Unit(BaseModel):
    """Represents a Fire Emblem unit with their base stats, growths, and other attributes."""
    name: str = Field(description="The unit's name.")
    char_class: str = Field(
        validation_alias=AliasChoices('class', 'char_class'),
        serialization_alias="class",
        description="The unit's starting class."
    )
    affinity: Optional[str] = Field(None, description="Elemental affinity (e.g., Earth, Fire, Thunder).")
    level: int = Field(ge=1, description="Starting level.")
    base_stats: BaseStats = Field(description="Unit's base stats upon recruitment.")
    growth_rates: GrowthRates = Field(description="Unit's growth rates per level.")

    class Config:
        populate_by_name = True