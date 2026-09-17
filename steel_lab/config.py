"""Shared settings: file locations, column names and analysis constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Raw inputs
PLANT_WORKBOOK = PROJECT_ROOT / "Plant-level_data_Global_Iron_and_Steel_Tracker_June_2026_V1.xlsx"
PLANT_SHEET = "Plant data"
CAPACITY_SHEET = "Plant capacities and status"
LITPOP_DIR = PROJECT_ROOT / "litpop"
LITPOP_FILE_PATTERN = "LitPop_pc_300_arcsec_*_v1.hdf5"

# Processed outputs read by the dashboard
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PLANTS_EXPORT = PROCESSED_DIR / "plants_clean.csv"
PLANTS_EXPOSURE_EXPORT = PROCESSED_DIR / "plants_with_litpop.csv"
COMPANIES_EXPORT = PROCESSED_DIR / "companies.csv"

# Column names from the GEM workbook
PLANT_ID = "GEM plant ID"
PLANT_NAME = "Plant name (English)"
OWNER = "Owner"
COUNTRY = "Country/area"
REGION = "Region"
COORDINATES = "Coordinates"
PLANT_AGE = "Plant age (years)"
STATUS = "Status"
STEEL_CAPACITY = "Nominal crude steel capacity (ttpa)"
IRON_CAPACITY = "Nominal iron capacity (ttpa)"
ANCILLARY_CAPACITIES = [
    "Ferronickel capacity (ttpa)",
    "Sinter plant capacity (ttpa)",
    "Coking plant capacity (ttpa)",
    "Pelletizing plant capacity (ttpa)",
]

# Columns added during cleaning
LATITUDE = "Latitude"
LONGITUDE = "Longitude"
PLANT_STATUS = "Plant status"

# A production unit counts towards a plant's capacity only while it runs.
OPERATING_STATUSES = {"operating", "operating pre-retirement"}

# When a plant has several units, its overall status is the first match in this list.
STATUS_PRIORITY = [
    "operating",
    "operating pre-retirement",
    "construction",
    "mothballed",
    "mothballed pre-retirement",
    "announced",
    "retired",
    "cancelled",
]

# LitPop matching
EARTH_RADIUS_KM = 6371.0
# A 300 arc-second cell is about 9.3 km wide, so an inland plant is within ~7 km
# of a cell centre. Coastal plants on reclaimed land can be further from the
# nearest land cell, hence the looser limit. Anything further is "no match".
MAX_MATCH_DISTANCE_KM = 20.0
# LitPop sample files are named by ISO3 code; plants must sit in the same country.
LITPOP_COUNTRY_CODES = {"China": "CHN", "India": "IND", "Japan": "JPN"}
# Radius used to add up the asset value around each plant.
EXPOSURE_RADIUS_KM = 20.0

# LitPop columns added to the plants
LITPOP_NEAREST_VALUE = "LitPop nearest cell value (USD)"
LITPOP_RADIUS_VALUE = f"LitPop assets within {EXPOSURE_RADIUS_KM:g} km (USD bn)"
LITPOP_DISTANCE = "Distance to LitPop cell (km)"
