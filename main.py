from fastapi import FastAPI, HTTPException
from models import BaseStats, GrowthRates

import json
from typing import Optional
from pathlib import Path

app = FastAPI()

@app.get("/base_stats/{game}/{unit}", response_model=BaseStats) ## Endpoint
def get_base_stats(game: int, unit: str) -> BaseStats :
    stat_path = Path(f"data/FE{game}/PlayerUnits/{unit}.json")
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
        class_=data["class"],

        lvl=data["level"],
        hp=base["hp"],
        str=base["str"],
        mag=data.get("mag"),
        skl=base["skl"],
        spd=base["spd"],
        lck=base["lck"],
        def_=base["def"],
        res=base["res"],
        mov=base["mov"],
        bld=data.get("bld"),
        wgt=data.get("wgt"),

        authority=data.get("authority"),
        affinity=data.get("affinity")
    )

@app.get("/growth_rates/{game}/{unit}", response_model=GrowthRates) ## Endpoint
def get_growth_rates(game: int, unit: str) -> GrowthRates :
    stat_path = Path(f"data/FE{game}/PlayerUnits/{unit}.json")
    with stat_path.open() as f :
        data = json.load(f)

    growth = data["growth_rates"]
    return GrowthRates(
        hp=growth["hp"],
        str=growth["str"],
        mag=data.get("mag"),
        spd=growth["spd"],
        skl=growth["skl"],
        lck=growth["lck"],
        def_=growth["def"],
        res=growth["res"]
    )