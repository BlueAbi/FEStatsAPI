from fastapi import FastAPI, HTTPException
from models import BaseStats, GrowthRates

import json
from typing import Optional
from pathlib import Path

app = FastAPI()

@app.get("/base_stats/{game}/{unit}")
@app.get("/base_stats/{game}/{book}/{unit}") ## To handle FE3 Book 1 and Book 2
def get_base_stats(game: int, unit: str, book: Optional[str] = None) -> BaseStats:
    base_path = Path(f"data/FE{game}")
    if book:
        base_path = base_path / book
    stat_path = base_path / "PlayerUnits" / f"{unit}.json"
    print(f"Loading data from {stat_path}")

    if not stat_path.exists() :
        raise HTTPException(status_code=404, detail=f"Stats file {stat_path} does not exist")

    try :
        with stat_path.open() as f :
            data = json.load(f)
            print(f"Loaded data from: {data}")
    except json.JSONDecodeError :
        raise HTTPException(status_code=500, detail="Error parsing JSON file")

    if "base_stats" not in data :
        raise HTTPException(status_code=500, detail="Missing 'base_stats' in the data")

    base = data["base_stats"]
    return BaseStats(
        class_=data.get("class"),
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
        wgt=base.get("wgt"),

        authority=data.get("authority"),
        affinity=data.get("affinity")
    )


@app.get("/growth_rates/{game}/{unit}", response_model=GrowthRates) ## Endpoint
def get_growth_rates(game: int, unit: str) -> GrowthRates :
    stat_path = Path(f"data/FE{game}/PlayerUnits/{unit}.json")
    with stat_path.open() as f :
        data = json.load(f)

    return GrowthRates(
        hp=data.get("hp"),
        str=data.get("str"),
        mag=data.get("mag"),
        skl=data.get("skl"),
        spd=data.get("spd"),
        lck=data.get("lck"),
        def_=data.get("def"),
        res=data.get("res")
    )