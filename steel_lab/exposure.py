"""Attach LitPop exposure values to steel plants by geographic proximity."""

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from steel_lab import config as cfg


def build_litpop_index(litpop: pd.DataFrame) -> BallTree:
    """Build a ball tree over LitPop cell centres using great-circle (haversine) distance."""
    return BallTree(np.radians(litpop[["latitude", "longitude"]].to_numpy()), metric="haversine")


def match_plants_to_litpop(plants: pd.DataFrame, litpop: pd.DataFrame) -> pd.DataFrame:
    """Return one row per plant with its nearest LitPop cell and nearby asset value.

    - The nearest cell is kept only if it lies within MAX_MATCH_DISTANCE_KM
      and in the plant's own country, so plants outside the sample countries
      (or with wrong coordinates) get no values.
    - Asset value is also summed over all cells within EXPOSURE_RADIUS_KM,
      which describes the surroundings better than a single cell.
    """
    tree = build_litpop_index(litpop)
    plant_points = np.radians(plants[[cfg.LATITUDE, cfg.LONGITUDE]].to_numpy())

    distances, nearest = tree.query(plant_points, k=1)
    distance_km = distances[:, 0] * cfg.EARTH_RADIUS_KM
    nearest_cells = litpop.iloc[nearest[:, 0]].reset_index(drop=True)
    plant_country_codes = plants[cfg.COUNTRY].map(cfg.LITPOP_COUNTRY_CODES).to_numpy()
    is_match = (distance_km <= cfg.MAX_MATCH_DISTANCE_KM) & (plant_country_codes == nearest_cells["country_iso3"].to_numpy())

    radius = cfg.EXPOSURE_RADIUS_KM / cfg.EARTH_RADIUS_KM
    cells_in_radius = tree.query_radius(plant_points, r=radius)
    cell_values = litpop["value"].to_numpy()
    assets_in_radius_bn = np.array([cell_values[cells].sum() for cells in cells_in_radius]) / 1e9

    matches = pd.DataFrame(
        {
            cfg.LITPOP_DISTANCE: distance_km,
            cfg.LITPOP_NEAREST_VALUE: nearest_cells["value"].to_numpy(),
            cfg.LITPOP_RADIUS_VALUE: assets_in_radius_bn,
            "LitPop country": nearest_cells["country_iso3"].to_numpy(),
        },
        index=plants.index,
    )
    matches.loc[~is_match, [cfg.LITPOP_NEAREST_VALUE, cfg.LITPOP_RADIUS_VALUE, "LitPop country"]] = np.nan
    return matches


def add_litpop_exposure(plants: pd.DataFrame, litpop: pd.DataFrame) -> pd.DataFrame:
    """Return the plants table with the LitPop columns added."""
    return plants.join(match_plants_to_litpop(plants, litpop))
