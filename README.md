# AIDAMS Lab 1 – Steel Plants, LitPop Exposure and Dashboard

Group: Edgar Gusching, Marius Rang, Victor Henz, Ylias Guetari

We look at the world's iron and steel plants (Global Energy Monitor), attach LitPop asset-value exposure to each plant, summarise everything per company, and show it in a Streamlit dashboard.

## What's in the repo

| Path | What it is |
|------|------------|
| `lab_1.ipynb` | The completed lab, with all outputs and written answers |
| `app.py` | Streamlit dashboard (Part 6) |
| `steel_lab/` | Code shared by the notebook and the dashboard |
| `steel_lab/config.py` | File paths, column names and settings |
| `steel_lab/loading.py` | Loads and cleans the GEM workbook and LitPop files |
| `steel_lab/exposure.py` | Matches plants to the nearest LitPop cells (ball tree, haversine) |
| `steel_lab/companies.py` | Company totals and company locations (centroid of plants) |
| `steel_lab/maps.py` | Plotly maps |
| `steel_lab/storage.py` | Saves and loads the processed CSVs |
| `data/processed/` | Processed data the dashboard reads |
| `Plant-level_data_Global_Iron_and_Steel_Tracker_June_2026_V1.xlsx` | Raw GEM plant data |
| `litpop/` | LitPop samples for China, India and Japan (from Moodle) |

## How to run

```bash
# 1. Install the dependencies (Python 3.12+)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt jupyter

# 2. (Optional) Re-run the notebook to rebuild data/processed/
jupyter nbconvert --to notebook --execute --inplace lab_1.ipynb

# 3. Start the dashboard
streamlit run app.py
```

The dashboard only needs `data/processed/`, which is already in the repo, so step 2 is optional.

## Main choices

- **Capacity** is the sum of a plant's units that are *operating* or *operating pre-retirement*. Announced, construction, mothballed, retired and cancelled units are not counted.
- **LitPop exposure** is the total produced-capital value (USD) within 20 km of a plant. A plant is only matched if the nearest cell is in the same country and within 20 km. This covers 613 plants in China, India and Japan.
- **Companies** are the direct `Owner` in the GEM data, placed at the centroid of their plants.
- **Data issue found:** *Hyundai Steel Louisiana* has a positive longitude in the source file (it should be negative). We flag it in the notebook and don't match it to LitPop.

## Sources

- Global Energy Monitor, [Global Iron and Steel Tracker](https://globalenergymonitor.org/projects/global-iron-steel-tracker), plant-level data, June 2026.
- ETH Zurich, [LitPop](https://www.research-collection.ethz.ch/entities/researchdata/12dcfc4f-9d03-463a-8d6b-76c0dc73cdc8): global gridded asset exposure, 300 arc-second country samples.
