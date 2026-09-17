"""Company-level (Owner) aggregation of plant data."""

import numpy as np
import pandas as pd

from steel_lab import config as cfg


def spherical_centroid(latitudes: pd.Series, longitudes: pd.Series) -> tuple[float, float]:
    """Average points on the globe correctly, even across the 180° meridian.

    Each point becomes a 3D unit vector; the mean vector is turned back into
    latitude and longitude.
    """
    lat, lon = np.radians(latitudes.to_numpy()), np.radians(longitudes.to_numpy())
    x = np.mean(np.cos(lat) * np.cos(lon))
    y = np.mean(np.cos(lat) * np.sin(lon))
    z = np.mean(np.sin(lat))
    return float(np.degrees(np.arctan2(z, np.hypot(x, y)))), float(np.degrees(np.arctan2(y, x)))


def aggregate_companies(plants: pd.DataFrame) -> pd.DataFrame:
    """Summarise capacity, plant count, exposure and geographic spread per owner."""
    grouped = plants.groupby(cfg.OWNER)
    return grouped.agg(
        **{
            "Number of plants": (cfg.PLANT_ID, "count"),
            "Total crude steel capacity (ttpa)": (cfg.STEEL_CAPACITY, "sum"),
            "Total iron capacity (ttpa)": (cfg.IRON_CAPACITY, "sum"),
            "Average plant age (years)": (cfg.PLANT_AGE, "mean"),
            f"Average {cfg.LITPOP_RADIUS_VALUE}": (cfg.LITPOP_RADIUS_VALUE, "mean"),
            f"Average {cfg.LITPOP_NEAREST_VALUE}": (cfg.LITPOP_NEAREST_VALUE, "mean"),
            "Plants matched to LitPop": (cfg.LITPOP_RADIUS_VALUE, "count"),
            "Number of countries": (cfg.COUNTRY, "nunique"),
            "Number of regions": (cfg.REGION, "nunique"),
            "Countries": (cfg.COUNTRY, lambda countries: ", ".join(sorted(countries.unique()))),
        }
    ).sort_values("Total crude steel capacity (ttpa)", ascending=False)


def company_locations(plants: pd.DataFrame) -> pd.DataFrame:
    """Place each company at the centroid of its plants (option 1 in the lab)."""
    centroids = {
        owner: spherical_centroid(group[cfg.LATITUDE], group[cfg.LONGITUDE])
        for owner, group in plants.groupby(cfg.OWNER)
    }
    return pd.DataFrame.from_dict(centroids, orient="index", columns=[cfg.LATITUDE, cfg.LONGITUDE])


def build_company_table(plants: pd.DataFrame) -> pd.DataFrame:
    """Company metrics plus a representative location, ready to map or export."""
    table = aggregate_companies(plants).join(company_locations(plants))
    return table.rename_axis(cfg.OWNER).reset_index()
