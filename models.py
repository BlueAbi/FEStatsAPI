from pydantic import BaseModel, Field
from typing import Optional

class BaseStats(BaseModel) :
    class_: str = Field(..., alias="class")

    lvl: int
    hp: int
    str: int
    mag: Optional[int] = None
    skl: int # Renamed to dexterity in Three Houses
    spd: int
    lck: int
    def_: int = Field(..., alias="def")
    res: int
    mov: int
    bld: Optional[int] = None  # Also known as constitution in some games
    wgt: Optional[int] = None

    ## Utilized in Genealogy, Thracia, and Radiant Dawn
    authority: Optional[int] = None

    ## Utilized in Path of Radiance and Radiant Dawn
    affinity: Optional[str] = None

    model_config = {
        "populate_by_name": True
    }

class GrowthRates(BaseModel) :
    hp: int
    str: int
    mag: int
    skl: int
    spd: int
    lck: int
    def_: int = Field(..., alias="def")
    res: int

    model_config = {
        "populate_by_name": True
    }