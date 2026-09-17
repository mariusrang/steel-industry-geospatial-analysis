"""AIDAMS Lab 1 – Steel plants dashboard.

Run with:  streamlit run app.py
Reads the processed CSVs written by lab_1.ipynb (Part 6) from data/processed/.
"""

from dataclasses import dataclass

import pandas as pd
import plotly.express as px
import streamlit as st

from steel_lab import config as cfg
from steel_lab import maps, storage

EXPOSURE_COLUMN = cfg.LITPOP_RADIUS_VALUE
COMPANY_CAPACITY = "Total crude steel capacity (ttpa)"


@dataclass
class Filters:
    """Choices made in the sidebar."""

    regions: list[str]
    countries: list[str]
    owners: list[str]
    statuses: list[str]
    capacity_range: tuple[int, int]


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the plant and company tables once per session."""
    return storage.load_plants_with_exposure(), storage.load_companies()


def apply_filters(plants: pd.DataFrame, filters: Filters) -> pd.DataFrame:
    """Keep only the plants matching every sidebar choice (an empty choice means 'all')."""
    low, high = filters.capacity_range
    mask = plants[cfg.STEEL_CAPACITY].between(low, high)
    for column, selected in [
        (cfg.REGION, filters.regions),
        (cfg.COUNTRY, filters.countries),
        (cfg.OWNER, filters.owners),
        (cfg.PLANT_STATUS, filters.statuses),
    ]:
        if selected:
            mask &= plants[column].isin(selected)
    return plants[mask]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def sorted_options(values: pd.Series) -> list[str]:
    """Unique values of a column, sorted, for use in a selector."""
    return sorted(values.dropna().unique())


def render_sidebar(plants: pd.DataFrame) -> Filters:
    """Draw the filters. Country and company lists narrow down as broader filters are set."""
    st.sidebar.header("Filters")

    regions = st.sidebar.multiselect("Region", sorted_options(plants[cfg.REGION]))
    in_regions = plants[plants[cfg.REGION].isin(regions)] if regions else plants

    countries = st.sidebar.multiselect("Country / area", sorted_options(in_regions[cfg.COUNTRY]))
    in_countries = in_regions[in_regions[cfg.COUNTRY].isin(countries)] if countries else in_regions

    owners = st.sidebar.multiselect("Company (owner)", sorted_options(in_countries[cfg.OWNER]))

    statuses = st.sidebar.multiselect(
        "Plant status",
        [status for status in cfg.STATUS_PRIORITY if status in set(plants[cfg.PLANT_STATUS])],
        default=["operating", "operating pre-retirement"],
    )

    max_capacity = int(plants[cfg.STEEL_CAPACITY].max())
    capacity_range = st.sidebar.slider(
        "Crude steel capacity (ttpa)", min_value=0, max_value=max_capacity, value=(0, max_capacity), step=100
    )
    st.sidebar.caption("Leave a filter empty to include everything.")
    return Filters(regions, countries, owners, statuses, capacity_range)


# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
def render_kpis(plants: pd.DataFrame) -> None:
    """Headline numbers for the current selection."""
    columns = st.columns(6)
    columns[0].metric("Plants", f"{len(plants):,}")
    columns[1].metric("Operating capacity", f"{plants[cfg.STEEL_CAPACITY].sum() / 1000:,.0f} Mt/yr")
    columns[2].metric("Companies", f"{plants[cfg.OWNER].nunique():,}")
    columns[3].metric("Countries", f"{plants[cfg.COUNTRY].nunique():,}")
    average_age = plants[cfg.PLANT_AGE].mean()
    columns[4].metric("Average plant age", "–" if pd.isna(average_age) else f"{average_age:.0f} yrs")
    columns[5].metric("Plants with LitPop data", f"{plants[EXPOSURE_COLUMN].notna().sum():,}")


def render_maps_tab(plants: pd.DataFrame) -> None:
    """Let the user pick one of the maps from Parts 3 and 4."""
    map_builders = {
        "Plant locations (by region)": lambda: maps.plant_location_map(plants, color_by=cfg.REGION),
        "Plants sized by capacity (top owners)": lambda: maps.plant_capacity_map(plants),
        "Plant density": lambda: maps.plant_density_map(plants),
        "Plant density weighted by capacity": lambda: maps.plant_density_map(plants, weight_by_capacity=True),
        "LitPop asset exposure (China, India, Japan)": lambda: maps.plant_exposure_map(plants),
    }
    choice = st.radio("Map", list(map_builders), horizontal=True)

    if choice.startswith("LitPop") and plants[EXPOSURE_COLUMN].isna().all():
        st.info("No plants in the current selection have LitPop data. It only covers China, India and Japan.")
        return
    st.plotly_chart(map_builders[choice](), width="stretch")


def render_exploration_tab(plants: pd.DataFrame) -> None:
    """Charts from the exploratory analysis in Part 2."""
    left, right = st.columns(2)

    by_region = plants.groupby(cfg.REGION)[cfg.STEEL_CAPACITY].agg(["count", "sum"]).reset_index()
    left.plotly_chart(
        px.bar(by_region.sort_values("sum"), x="sum", y=cfg.REGION, orientation="h", text="count",
               title="Capacity by region (label = number of plants)",
               labels={"sum": "Capacity (ttpa)", cfg.REGION: ""}),
        width="stretch",
    )

    top_countries = plants.groupby(cfg.COUNTRY)[cfg.STEEL_CAPACITY].sum().nlargest(15).sort_values()
    right.plotly_chart(
        px.bar(top_countries, orientation="h", title="Top 15 countries by capacity",
               labels={"value": "Capacity (ttpa)", cfg.COUNTRY: ""}).update_layout(showlegend=False),
        width="stretch",
    )

    top_owners = plants.groupby(cfg.OWNER)[cfg.STEEL_CAPACITY].sum().nlargest(15).sort_values()
    left.plotly_chart(
        px.bar(top_owners, orientation="h", title="Top 15 owners by capacity",
               labels={"value": "Capacity (ttpa)", cfg.OWNER: ""}).update_layout(showlegend=False),
        width="stretch",
    )

    right.plotly_chart(
        px.histogram(plants, x=cfg.PLANT_AGE, color=cfg.REGION, nbins=50, title="Plant age distribution"),
        width="stretch",
    )

    status_counts = plants[cfg.PLANT_STATUS].value_counts().rename_axis("Status").reset_index(name="Plants")
    st.plotly_chart(
        px.bar(status_counts, x="Status", y="Plants", title="Plants by status"),
        width="stretch",
    )


def render_companies_tab(plants: pd.DataFrame, company_table: pd.DataFrame) -> None:
    """Company map and table for the companies that own plants in the selection."""
    selected = company_table[company_table[cfg.OWNER].isin(plants[cfg.OWNER])]
    st.caption(
        "Company figures cover **all** plants of each company that has at least one plant in your selection."
    )

    exposure_column = f"Average {EXPOSURE_COLUMN}"
    if selected[exposure_column].notna().any():
        st.plotly_chart(maps.company_map(selected), width="stretch")
    else:
        st.info("None of these companies has plants in the LitPop sample (China, India, Japan), so there is no map.")

    columns = [cfg.OWNER, "Number of plants", COMPANY_CAPACITY, "Total iron capacity (ttpa)",
               "Average plant age (years)", exposure_column, "Number of countries", "Countries"]
    st.dataframe(selected[columns].sort_values(COMPANY_CAPACITY, ascending=False), hide_index=True, width="stretch")


def render_data_tab(plants: pd.DataFrame) -> None:
    """Filtered plant table with a CSV download."""
    columns = [cfg.PLANT_NAME, cfg.OWNER, cfg.COUNTRY, cfg.REGION, cfg.PLANT_STATUS, cfg.STEEL_CAPACITY,
               cfg.IRON_CAPACITY, cfg.PLANT_AGE, EXPOSURE_COLUMN, cfg.LATITUDE, cfg.LONGITUDE, "GEM wiki page"]
    st.dataframe(
        plants[columns].sort_values(cfg.STEEL_CAPACITY, ascending=False),
        hide_index=True,
        width="stretch",
        column_config={"GEM wiki page": st.column_config.LinkColumn("GEM wiki page")},
    )
    st.download_button(
        "Download selection as CSV",
        plants[columns].to_csv(index=False).encode("utf-8"),
        file_name="steel_plants_selection.csv",
        mime="text/csv",
    )


def render_footer() -> None:
    """Data sources and method notes."""
    st.divider()
    st.caption(
        "**Sources:** Global Energy Monitor, *Global Iron and Steel Tracker* (plant-level data, June 2026); "
        "ETH Zurich / CLIMADA *LitPop* produced-capital exposure, 300 arc-second samples for China, India and Japan.  \n"
        "**Notes:** capacity counts only operating and operating pre-retirement units. "
        f"LitPop exposure is the total asset value within {cfg.EXPOSURE_RADIUS_KM:g} km of each plant. "
        "Companies are the direct `Owner` in the GEM data, placed at the centroid of their plants.  \n"
        "AIDAMS Lab 1 – Gusching, Rang, Henz, Guetari."
    )


def main() -> None:
    st.set_page_config(page_title="Steel Plants Dashboard", page_icon="🏭", layout="wide")
    st.title("🏭 Global Steel Plants Dashboard")
    st.markdown(
        "Where the world's iron and steel plants are, who owns them, how much they can produce, "
        "and how much economic value surrounds them (LitPop exposure)."
    )

    plants, company_table = load_data()
    filters = render_sidebar(plants)
    selection = apply_filters(plants, filters)

    render_kpis(selection)
    if selection.empty:
        st.warning("No plants match these filters.")
        render_footer()
        return

    maps_tab, exploration_tab, companies_tab, data_tab = st.tabs(["Maps", "Exploration", "Companies", "Data"])
    with maps_tab:
        render_maps_tab(selection)
    with exploration_tab:
        render_exploration_tab(selection)
    with companies_tab:
        render_companies_tab(selection, company_table)
    with data_tab:
        render_data_tab(selection)
    render_footer()


if __name__ == "__main__":
    main()
