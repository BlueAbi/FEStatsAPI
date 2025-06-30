from fastapi import FastAPI, HTTPException
from models import BaseStats, GrowthRates
from typing import Optional
from pathlib import Path
import json

app = FastAPI()

def get_stat_path(game: int, unit: str, book: Optional[str] = None) -> Path:
    base_path = Path(f"data/FE{game}")
    if book:
        base_path = base_path / book
    return base_path / "PlayerUnits" / f"{unit}.json"

@app.get("/base_stats/{game}/{unit}", response_model=BaseStats)
@app.get("/base_stats/{game}/{book}/{unit}", response_model=BaseStats)
def get_base_stats(game: int, unit: str, book: Optional[str] = None) -> BaseStats:
    stat_path = get_stat_path(game, unit, book)
    print(f"Loading data from {stat_path}")

    if not stat_path.exists():
        raise HTTPException(status_code=404, detail=f"Stats file {stat_path} does not exist")

    try:
        with stat_path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing JSON file")

    if "base_stats" not in data:
        raise HTTPException(status_code=500, detail="Missing 'base_stats' in the data")

    base = data["base_stats"]
    return BaseStats(
        class_=data.get("class"),
        affinity=data.get("affinity"),
        authority=data.get("authority"),
        lvl=data.get("level"),
        hp=base.get("hp"),
        str=base.get("str"),
        mag=base.get("mag"),
        skl=base.get("skl"),
        spd=base.get("spd"),
        lck=base.get("lck"),
        def_=base.get("def"),
        res=base.get("res"),
        mov=base.get("mov"),
        bld=base.get("bld"),
        wgt=base.get("wgt")
    )

@app.get("/growth_rates/{game}/{unit}", response_model=GrowthRates)
@app.get("/growth_rates/{game}/{book}/{unit}", response_model=GrowthRates)
def get_growth_rates(game: int, unit: str, book: Optional[str] = None) -> GrowthRates:
    stat_path = get_stat_path(game, unit, book)

    if not stat_path.exists():
        raise HTTPException(status_code=404, detail=f"Stats file {stat_path} does not exist")

    try:
        with stat_path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing JSON file")

    if "growth_rates" not in data:
        raise HTTPException(status_code=500, detail="Missing 'growth_rates' in the data")

    growth = data["growth_rates"]
    return GrowthRates(
        hp=growth.get("hp"),
        str=growth.get("str"),
        mag=growth.get("mag"),
        skl=growth.get("skl"),
        spd=growth.get("spd"),
        lck=growth.get("lck"),
        def_=growth.get("def"),
        res=growth.get("res"),

        # Only in Thracia/FE5
        bld=growth.get("bld"),
        mov=growth.get("mov")
    )
