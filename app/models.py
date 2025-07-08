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
    res: Optional[int] = None # Does not exist in Thracia it was merged with magic
    mov: int
    bld: Optional[int] = None  # Also known as constitution in some games
    wgt: Optional[int] = None

    ## Utilized in Genealogy, Thracia, and Radiant Dawn
    authority: Optional[int] = None

    ## Utilized in Path of Radiance and Radiant Dawn
    affinity: Optional[str] = None

    # Used in games with rescue
    aid: Optional[int] = None

    model_config = {
        "populate_by_name": True
    }

class GrowthRates(BaseModel) :
    hp: int
    str: int
    mag: Optional[int] = None
    skl: int
    spd: int
    lck: int
    def_: int = Field(..., alias="def")
    res: Optional[int] = None

    # Only in Thracia/FE5
    bld: Optional[int] = None
    mov: Optional[int] = None

    model_config = {
        "populate_by_name": True
    }