"""Save processed tables for the dashboard and load them back."""

import pandas as pd

from steel_lab import config as cfg

# Plant columns worth keeping for the dashboard (the raw sheet has 44, many in other languages).
PLANT_EXPORT_COLUMNS = [
    cfg.PLANT_ID,
    cfg.PLANT_NAME,
    cfg.OWNER,
    "Parent (English)",
    cfg.COUNTRY,
    cfg.REGION,
    "Subnational unit",
    cfg.LATITUDE,
    cfg.LONGITUDE,
    "Coordinate accuracy",
    cfg.PLANT_STATUS,
    "Number of units",
    cfg.PLANT_AGE,
    cfg.STEEL_CAPACITY,
    cfg.IRON_CAPACITY,
    *cfg.ANCILLARY_CAPACITIES,
    "Main production equipment",
    "Workforce size",
    "GEM wiki page",
]
LITPOP_EXPORT_COLUMNS = [
    cfg.LITPOP_NEAREST_VALUE,
    cfg.LITPOP_RADIUS_VALUE,
    cfg.LITPOP_DISTANCE,
    "LitPop country",
]


def save_processed_data(
    plants: pd.DataFrame, plants_with_exposure: pd.DataFrame, company_table: pd.DataFrame
) -> list[str]:
    """Write the three dashboard tables as CSV and return the file paths written."""
    cfg.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    plants[PLANT_EXPORT_COLUMNS].to_csv(cfg.PLANTS_EXPORT, index=False)
    plants_with_exposure[PLANT_EXPORT_COLUMNS + LITPOP_EXPORT_COLUMNS].to_csv(cfg.PLANTS_EXPOSURE_EXPORT, index=False)
    company_table.to_csv(cfg.COMPANIES_EXPORT, index=False)
    return [str(path.relative_to(cfg.PROJECT_ROOT)) for path in
            (cfg.PLANTS_EXPORT, cfg.PLANTS_EXPOSURE_EXPORT, cfg.COMPANIES_EXPORT)]


def load_plants_with_exposure() -> pd.DataFrame:
    """Read the merged plant + LitPop table."""
    return pd.read_csv(cfg.PLANTS_EXPOSURE_EXPORT)


def load_companies() -> pd.DataFrame:
    """Read the company-level table."""
    return pd.read_csv(cfg.COMPANIES_EXPORT)
