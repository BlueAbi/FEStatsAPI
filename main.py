from fastapi import FastAPI, HTTPException, status
from pathlib import Path
import json
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

# Import your Pydantic models (assuming models.py is in the same directory)
from models import Unit, BaseStats, GrowthRates

# Define the base directory where your game data is stored
BASE_DATA_DIR = Path(__file__).resolve().parent / "data"

# --- Mapping for game names to folder names ---
# This dictionary maps user-friendly game names to their corresponding folder names.
# Add all the Fire Emblem games you plan to include here.
GAME_FOLDER_MAP = {
    "shadow_dragon_and_the_blade_of_light": "FE1",
    "gaiden": "FE2",
    "mystery_of_the_emblem": "FE3",
    "genealogy_of_the_holy_war": "FE4",
    "thracia_776": "FE5",
    "the_binding_blade": "FE6",
    "the_blazing_sword": "FE7",
    "the_sacred_stones": "FE8",
    "path_of_radiance": "FE9", # Your current test game for Ike
    "radiant_dawn": "FE10",
    "shadow_dragon": "FE11",
    "new_mystery_of_the_emblem": "FE12",
    "awakening": "FE13",
    "fates": "FE14",
    "echoes_shadows_of_valentia": "FE15",
    "three_houses": "FE16",
    "engage": "FE17",
    # Add more mappings as needed for all your FE games
}

# --- Reverse map for folder names to friendly names ---
# This will be populated automatically during application startup.
# It allows the API to accept both "FE9" and "path_of_radiance" in URLs.
_FOLDER_TO_FRIENDLY_MAP: Dict[str, str] = {}

# --- In-memory cache for unit data ---
# Unit data will be loaded into this cache when the application starts.
# Keys are user-friendly game names (e.g., "path_of_radiance"), values are dictionaries
# mapping lowercased unit names to Unit Pydantic models.
_GAME_UNIT_CACHE: Dict[str, Dict[str, Unit]] = {}

# --- Helper Function: Resolve Game Name for Lookups ---
def _get_game_names_for_lookup(input_game_name: str) -> Optional[str]:
    """
    Resolves an input game name (which could be friendly or a folder code)
    to the consistent friendly game name used as a key in the cache.
    Returns the friendly name if found, otherwise None.
    """
    input_game_name_lower = input_game_name.lower()

    # 1. Check if the input is already a friendly name (a key in our cache)
    if input_game_name_lower in _GAME_UNIT_CACHE:
        return input_game_name_lower

    # 2. Check if the input is a folder code (e.g., "fe9") using our reverse map
    if input_game_name_lower in _FOLDER_TO_FRIENDLY_MAP:
        return _FOLDER_TO_FRIENDLY_MAP[input_game_name_lower]

    # If neither matches, the game name isn't recognized
    return None

# --- Helper Function: Load Individual Unit Data ---
def _load_unit_data(game_name_friendly: str, unit_name: str) -> Unit:
    """
    Loads and validates a single unit's JSON data from a specific game's folder.
    This function expects the *friendly game name* as input, ensuring consistency.
    """
    # Basic sanitization to prevent directory traversal attempts in unit_name
    if not unit_name.replace('-', '').replace('_', '').isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid unit name. Only alphanumeric characters, hyphens, and underscores are allowed."
        )

    # Get the actual folder name (e.g., "FE9") from the friendly game name (e.g., "path_of_radiance")
    game_folder_name = GAME_FOLDER_MAP.get(game_name_friendly)
    if not game_folder_name:
        # This error should ideally not be triggered if the startup process runs correctly
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: Friendly game name '{game_name_friendly}' not mapped to a folder."
        )

    # Construct the full path to the unit's JSON file
    json_file_path = BASE_DATA_DIR / game_folder_name / f"{unit_name.lower()}.json"

    # Check if the file exists before attempting to open it
    if not json_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unit '{unit_name}' not found in game '{game_name_friendly}' (looked in: {json_file_path}). "
                    f"Please ensure the JSON filename is all lowercase: '{unit_name.lower()}.json'."
        )

    try:
        # Read the JSON data from the file
        with open(json_file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Validate the loaded data against the Pydantic Unit model
        unit = Unit(**raw_data)
        return unit
    except json.JSONDecodeError:
        # Catch errors if the JSON file is malformed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error decoding JSON for unit '{unit_name}' in game '{game_name_friendly}'. Invalid JSON format."
        )
    except Exception as e:
        # Catch any other unexpected errors during data processing/validation
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while processing unit '{unit_name}' in game '{game_name_friendly}': {e}"
        )

# --- Lifespan Event Handler (for application startup/shutdown) ---
@asynccontextmanager
async def lifespan(fastapi_app: FastAPI): # Renamed 'app' parameter to 'fastapi_app' to avoid shadowing
    """
    Manages application startup and shutdown events, primarily used to load
    all unit data into an in-memory cache at startup.
    """
    print("Application starting up...")
    print("Loading unit data into cache...")

    # Iterate through the defined game mappings
    for game_name_friendly, game_folder_name in GAME_FOLDER_MAP.items():
        # Populate the reverse lookup map (e.g., {"fe9": "path_of_radiance"})
        _FOLDER_TO_FRIENDLY_MAP[game_folder_name.lower()] = game_name_friendly

        # Construct the path to the game's data folder
        game_dir = BASE_DATA_DIR / game_folder_name

        # Check if the game's data directory actually exists
        if not game_dir.is_dir():
            print(f"Warning: Folder for game '{game_name_friendly}' (expected: {game_folder_name}) not found. Skipping.")
            continue

        # Initialize an empty dictionary for units in this game within the cache
        _GAME_UNIT_CACHE[game_name_friendly] = {}
        print(f"  Loading units for game: {game_name_friendly} (from folder: {game_folder_name})")

        # Iterate through all JSON files in the game's directory
        for json_file in game_dir.glob("*.json"):
            unit_name = json_file.stem # Get the filename without extension (e.g., "ike")
            try:
                # Load and validate the unit data using the helper function
                unit = _load_unit_data(game_name_friendly, unit_name)
                # Store the validated unit data in the cache, using the lowercased unit name as key
                _GAME_UNIT_CACHE[game_name_friendly][unit_name.lower()] = unit
            except HTTPException as e:
                # Print warnings for individual files that fail to load
                print(f"    Warning: Could not load {unit_name}.json in {game_folder_name} ({game_name_friendly}): {e.detail}")
            except Exception as e:
                # Print warnings for unexpected errors during loading
                print(f"    Warning: Unexpected error loading {unit_name}.json in {game_folder_name} ({game_name_friendly}): {e}")
    print(f"Finished loading data for {len(_GAME_UNIT_CACHE)} mapped games.")

    # The 'yield' statement indicates that startup is complete and the application is ready to serve requests.
    yield

    # Any code placed after 'yield' would run during application shutdown.
    print("Application shutting down.")

# --- FastAPI Application Instance ---
# Initialize your FastAPI app, linking it to the defined lifespan event handler.
app = FastAPI(
    title="Fire Emblem Stats API",
    description="An API to retrieve stats and other useful information for Fire Emblem units across the series.",
    version="0.0.1",
    lifespan=lifespan # Connects the lifespan function to the app's lifecycle
)

# --- API Endpoints ---

@app.get("/data", summary="Get all available Fire Emblem games")
async def get_all_games() -> List[str]:
    """
    Returns a sorted list of all user-friendly game names for which unit data is available
    in the API.
    """
    return sorted(list(_GAME_UNIT_CACHE.keys()))

@app.get("/data/{game_name}/PlayerUnits", response_model=List[Dict[str, str]], summary="Get all units for a specific game")
async def get_all_units_for_game(game_name: str) -> List[Dict[str, str]]:
    """
    Returns a list of all available Fire Emblem units (with their names and games)
    for a specified game.

    - **game_name**: The name of the game (e.g., 'path_of_radiance' or its folder code like 'FE9').
      Case-insensitive.
    """
    # Resolve the input game name to its friendly cached name
    resolved_game_name = _get_game_names_for_lookup(game_name)
    if not resolved_game_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game '{game_name}' not found or not mapped. Try a friendly name (e.g., 'path_of_radiance') or a folder code (e.g., 'FE9')."
        )

    # Return a list of dictionaries containing unit names and the resolved game name
    return [{"name": unit.name, "game": resolved_game_name} for unit in _GAME_UNIT_CACHE[resolved_game_name].values()]


@app.get("/data/{game_name}/PlayerUnits/{unit_name}",
         response_model=Unit,
         summary="Get stats for a specific unit from a specific game")
async def get_unit_stats_by_game(game_name: str, unit_name: str) -> Unit:
    """
    Retrieves the base stats, growth rates, and other details for a specific
    Fire Emblem unit from a specified game.

    - **game_name**: The name of the game (e.g., 'path_of_radiance' or 'FE9'). Case-insensitive.
    - **unit_name**: The name of the unit (e.g., 'ike'). Case-insensitive.
    """
    # Resolve the input game name
    resolved_game_name = _get_game_names_for_lookup(game_name)
    if not resolved_game_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Game '{game_name}' not found or not mapped. Try a friendly name (e.g., 'path_of_radiance') or a folder code (e.g., 'FE9')."
        )

    unit_name_lower = unit_name.lower() # Standardize unit name to lowercase for cache lookup

    # Attempt to retrieve the unit data from the cache
    unit_data = _GAME_UNIT_CACHE[resolved_game_name].get(unit_name_lower)
    if not unit_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unit '{unit_name}' not found in game '{resolved_game_name}' (from input '{game_name}')."
        )
    return unit_data

@app.get("/data/{game_name}/PlayerUnits/{unit_name}/bases",
         response_model=BaseStats,
         summary="Get base stats for a unit from a specific game")
async def get_unit_bases_by_game(game_name: str, unit_name: str) -> BaseStats:
    """
    Retrieves only the base stats (including Movement and Weight) for a specific
    Fire Emblem unit from a specified game.

    - **game_name**: The name of the game (e.g., 'path_of_radiance' or 'FE9'). Case-insensitive.
    - **unit_name**: The name of the unit (e.g., 'ike'). Case-insensitive.
    """
    # Reuse the primary lookup logic to get the full unit object
    unit = await get_unit_stats_by_game(game_name, unit_name)
    return unit.base_stats

@app.get("/data/{game_name}/PlayerUnits/{unit_name}/growths",
         response_model=GrowthRates,
         summary="Get growth rates for a unit from a specific game")
async def get_unit_growths_by_game(game_name: str, unit_name: str) -> GrowthRates:
    """
    Retrieves only the growth rates for a specific Fire Emblem unit from a specified game.

    - **game_name**: The name of the game (e.g., 'path_of_radiance' or 'FE9'). Case-insensitive.
    - **unit_name**: The name of the unit (e.g., 'ike'). Case-insensitive.
    """
    # Reuse the primary lookup logic to get the full unit object
    unit = await get_unit_stats_by_game(game_name, unit_name)
    return unit.growth_rates