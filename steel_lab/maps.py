"""Plotly map builders shared by the notebook and the Streamlit dashboard.

Plotly 6+ replaced the Mapbox functions (scatter_mapbox, density_mapbox) with
MapLibre versions (scatter_map, density_map) that need no access token.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from steel_lab import config as cfg

MAP_STYLE = "carto-positron"
WORLD_VIEW = {"center": {"lat": 25, "lon": 30}, "zoom": 1}
# The LitPop sample covers China, India and Japan
LITPOP_VIEW = {"center": {"lat": 30, "lon": 105}, "zoom": 2.3}
EXPOSURE_COLOR_SCALE = "Viridis"


def _capped_color_range(values: pd.Series, upper_quantile: float = 0.95) -> tuple[float, float]:
    """Colour range that stops at a high quantile.

    Asset values are extremely skewed (a few Japanese metro plants are 100x the
    median), so a full range would make almost every marker the same colour.
    """
    return 0.0, float(values.quantile(upper_quantile))


def _finish_layout(figure: go.Figure, title: str) -> go.Figure:
    """Apply the common title, size and margins."""
    figure.update_layout(title=title, height=600, margin={"l": 0, "r": 0, "t": 50, "b": 0})
    return figure


def plant_location_map(plants: pd.DataFrame, color_by: str = cfg.REGION) -> go.Figure:
    """All plants as dots, coloured by a category such as region or country."""
    figure = px.scatter_map(
        plants,
        lat=cfg.LATITUDE,
        lon=cfg.LONGITUDE,
        color=color_by,
        hover_name=cfg.PLANT_NAME,
        hover_data={cfg.OWNER: True, cfg.COUNTRY: True, cfg.STEEL_CAPACITY: ":,.0f",
                    cfg.LATITUDE: False, cfg.LONGITUDE: False},
        map_style=MAP_STYLE,
        **WORLD_VIEW,
    )
    return _finish_layout(figure, f"Steel plant locations by {color_by}")


def label_top_owners(plants: pd.DataFrame, top_n: int) -> pd.Series:
    """Keep the names of the top_n owners by capacity and call everyone else 'Other'."""
    top_owners = plants.groupby(cfg.OWNER)[cfg.STEEL_CAPACITY].sum().nlargest(top_n).index
    return plants[cfg.OWNER].where(plants[cfg.OWNER].isin(top_owners), "Other")


def plant_capacity_map(plants: pd.DataFrame, top_owners: int = 15) -> go.Figure:
    """Operating plants sized by crude steel capacity and coloured by owner.

    There are hundreds of owners, so only the biggest get their own colour;
    the hover label still shows every plant's real owner.
    """
    operating = plants[plants[cfg.STEEL_CAPACITY] > 0]
    owner_group = label_top_owners(operating, top_owners).rename("Owner (top by capacity)")
    figure = px.scatter_map(
        operating.assign(**{owner_group.name: owner_group}),
        lat=cfg.LATITUDE,
        lon=cfg.LONGITUDE,
        size=cfg.STEEL_CAPACITY,
        size_max=30,
        color=owner_group.name,
        color_discrete_map={"Other": "lightgray"},
        hover_name=cfg.PLANT_NAME,
        hover_data={cfg.OWNER: True, cfg.COUNTRY: True, cfg.PLANT_STATUS: True, cfg.PLANT_AGE: True,
                    cfg.STEEL_CAPACITY: ":,.0f", cfg.LATITUDE: False, cfg.LONGITUDE: False},
        map_style=MAP_STYLE,
        **WORLD_VIEW,
    )
    return _finish_layout(figure, "Operating steel plants sized by crude steel capacity")


def plant_density_map(plants: pd.DataFrame, weight_by_capacity: bool = False) -> go.Figure:
    """Heatmap of where plants cluster, optionally weighted by capacity."""
    figure = px.density_map(
        plants,
        lat=cfg.LATITUDE,
        lon=cfg.LONGITUDE,
        z=cfg.STEEL_CAPACITY if weight_by_capacity else None,
        radius=12,
        hover_name=cfg.PLANT_NAME,
        map_style=MAP_STYLE,
        **WORLD_VIEW,
    )
    weighting = " (weighted by capacity)" if weight_by_capacity else ""
    return _finish_layout(figure, f"Steel plant density{weighting}")


def plant_exposure_map(plants: pd.DataFrame) -> go.Figure:
    """Plants matched to LitPop, coloured by nearby asset value and sized by capacity."""
    matched = plants.dropna(subset=[cfg.LITPOP_RADIUS_VALUE])
    figure = px.scatter_map(
        matched,
        lat=cfg.LATITUDE,
        lon=cfg.LONGITUDE,
        color=cfg.LITPOP_RADIUS_VALUE,
        size=matched[cfg.STEEL_CAPACITY].clip(lower=100),  # keep non-operating plants visible
        size_max=25,
        color_continuous_scale=EXPOSURE_COLOR_SCALE,
        range_color=_capped_color_range(matched[cfg.LITPOP_RADIUS_VALUE]),
        hover_name=cfg.PLANT_NAME,
        hover_data={cfg.OWNER: True, cfg.COUNTRY: True, cfg.STEEL_CAPACITY: ":,.0f",
                    cfg.LITPOP_RADIUS_VALUE: ":,.1f", cfg.LITPOP_NEAREST_VALUE: ":,.3s",
                    cfg.LITPOP_DISTANCE: ":.1f", cfg.LATITUDE: False, cfg.LONGITUDE: False},
        map_style=MAP_STYLE,
        **LITPOP_VIEW,
    )
    return _finish_layout(figure, "Steel plants and surrounding asset value (LitPop; colour capped at the 95th percentile)")


def company_map(companies: pd.DataFrame) -> go.Figure:
    """One marker per company at its plant centroid, sized by capacity, coloured by exposure.

    Only companies with at least one plant matched to LitPop can be coloured,
    so the others are left out.
    """
    exposure_column = f"Average {cfg.LITPOP_RADIUS_VALUE}"
    with_capacity = companies[(companies["Total crude steel capacity (ttpa)"] > 0) & companies[exposure_column].notna()]
    figure = px.scatter_map(
        with_capacity,
        lat=cfg.LATITUDE,
        lon=cfg.LONGITUDE,
        size="Total crude steel capacity (ttpa)",
        size_max=35,
        color=exposure_column,
        color_continuous_scale=EXPOSURE_COLOR_SCALE,
        range_color=_capped_color_range(with_capacity[exposure_column]),
        hover_name=cfg.OWNER,
        hover_data={"Number of plants": True, "Total crude steel capacity (ttpa)": ":,.0f",
                    exposure_column: ":,.1f", "Number of countries": True, "Countries": True,
                    "Average plant age (years)": ":.0f", cfg.LATITUDE: False, cfg.LONGITUDE: False},
        map_style=MAP_STYLE,
        **LITPOP_VIEW,
    )
    return _finish_layout(figure, "Companies at the centroid of their plants (companies with LitPop data)")
