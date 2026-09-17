"""Load and clean the GEM steel plant workbook and the LitPop exposure grid."""

from pathlib import Path

import numpy as np
import pandas as pd

from steel_lab import config as cfg


def to_number(values: pd.Series) -> pd.Series:
    """Convert a column to floats, turning text such as 'unknown' or '>0' into NaN."""
    return pd.to_numeric(values, errors="coerce")


def split_coordinates(coordinates: pd.Series) -> pd.DataFrame:
    """Split a 'lat, lon' text column into numeric Latitude and Longitude columns."""
    parts = coordinates.str.split(",", n=1, expand=True)
    return pd.DataFrame(
        {cfg.LATITUDE: to_number(parts[0]), cfg.LONGITUDE: to_number(parts[1])},
        index=coordinates.index,
    )


def distance_km(lat1, lon1, lat2, lon2):
    """Great-circle (haversine) distance in km; works on scalars or arrays."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * cfg.EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def find_suspicious_coordinates(plants: pd.DataFrame, max_km: float = 7000.0) -> pd.DataFrame:
    """List plants located unusually far from the median location of their country.

    A cheap sanity check that catches typos such as a missing minus sign.
    """
    country_centre = plants.groupby(cfg.COUNTRY)[[cfg.LATITUDE, cfg.LONGITUDE]].transform("median")
    km_from_centre = distance_km(plants[cfg.LATITUDE], plants[cfg.LONGITUDE],
                                 country_centre[cfg.LATITUDE], country_centre[cfg.LONGITUDE])
    flagged = plants.assign(**{"km from country median": km_from_centre})
    columns = [cfg.PLANT_NAME, cfg.COUNTRY, "Subnational unit", cfg.COORDINATES, "km from country median"]
    return flagged.loc[flagged["km from country median"] > max_km, columns].sort_values("km from country median", ascending=False)


def pick_plant_status(unit_statuses: pd.Series) -> str:
    """Summarise the statuses of a plant's units into a single plant status."""
    present = set(unit_statuses.dropna())
    for status in cfg.STATUS_PRIORITY:
        if status in present:
            return status
    return "unknown"


def summarise_units(units: pd.DataFrame) -> pd.DataFrame:
    """Reduce the unit-level capacity sheet to one row per plant.

    Capacity only counts units that are currently running, so announced,
    retired or cancelled units do not inflate the totals.
    """
    units = units.assign(
        **{
            cfg.STEEL_CAPACITY: to_number(units[cfg.STEEL_CAPACITY]),
            cfg.IRON_CAPACITY: to_number(units[cfg.IRON_CAPACITY]),
        }
    )
    running = units[units[cfg.STATUS].isin(cfg.OPERATING_STATUSES)]

    operating_capacity = running.groupby(cfg.PLANT_ID)[[cfg.STEEL_CAPACITY, cfg.IRON_CAPACITY]].sum()
    plant_status = units.groupby(cfg.PLANT_ID)[cfg.STATUS].agg(pick_plant_status).rename(cfg.PLANT_STATUS)
    unit_count = units.groupby(cfg.PLANT_ID).size().rename("Number of units")

    summary = pd.concat([plant_status, unit_count, operating_capacity], axis=1)
    return summary.fillna({cfg.STEEL_CAPACITY: 0.0, cfg.IRON_CAPACITY: 0.0})


def load_plants(workbook: Path = cfg.PLANT_WORKBOOK) -> pd.DataFrame:
    """Load the plant sheet, parse numbers and coordinates, and attach operating capacity."""
    plants = pd.read_excel(workbook, sheet_name=cfg.PLANT_SHEET)
    units = pd.read_excel(workbook, sheet_name=cfg.CAPACITY_SHEET)

    plants = plants.rename(columns={"Plant age": cfg.PLANT_AGE})
    plants[cfg.PLANT_AGE] = to_number(plants[cfg.PLANT_AGE])
    for column in cfg.ANCILLARY_CAPACITIES:
        plants[column] = to_number(plants[column])

    plants = plants.join(split_coordinates(plants[cfg.COORDINATES]))
    return plants.merge(summarise_units(units), left_on=cfg.PLANT_ID, right_index=True, how="left")


def load_litpop(directory: Path = cfg.LITPOP_DIR) -> pd.DataFrame:
    """Load every LitPop country file in the folder into one table of grid cells."""
    frames = []
    for path in sorted(directory.glob(cfg.LITPOP_FILE_PATTERN)):
        country_code = path.stem.split("_")[-2]
        cells = pd.read_hdf(path, key="exposures")
        frames.append(cells[["latitude", "longitude", "value", "region_id"]].assign(country_iso3=country_code))
    return pd.concat(frames, ignore_index=True)
