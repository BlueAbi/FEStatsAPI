from pydantic import BaseModel, Field

class BaseStats(BaseModel) :
    class_: str = Field(..., alias="class")
    affinity: str

    lvl: int
    hp: int
    str: int
    mag: int
    skl: int # Renamed to dexterity in Three Houses
    spd: int
    lck: int
    def_: int = Field(..., alias="def")
    res: int
    mov: int
    bld: int  # Also known as constitution in some games
    wgt: int

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