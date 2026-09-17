# 🏭 Global Steel Plants Dashboard

An interactive dashboard for exploring the world's iron and steel plants — their locations, owners, production capacities, and surrounding economic exposure (LitPop).

🔗 **[Live App](https://aidams-lab1-gusching-rang-henz-guetari-citthygx7ko6rixwsgvrob.streamlit.app/)**

---

## 📌 Project Overview

This project was developed as part of **AIDAMS Lab 1** by:
- **Gusching**
- **Rang**
- **Henz**
- **Guetari**

It combines plant-level steel industry data with geospatial LitPop asset exposure data to provide insights into the global steel industry landscape.

---

## 🚀 Features

- 🗺️ **Interactive Maps** — Plant locations by region, sized by capacity, density heatmaps, and LitPop asset exposure (China, India, Japan)
- 📊 **Exploration Charts** — Capacity by region & country, top owners, plant age distribution, plant status breakdown
- 🏢 **Company Analysis** — Company-level aggregated stats with geographic overview
- 📥 **Data Table** — Filterable plant table with CSV export

### Sidebar Filters
- Region, Country, Company (owner), Plant status
- Crude steel capacity range slider

---

## 🛠️ Tech Stack

| Tool | Usage |
|------|-------|
| Python | Core language |
| Streamlit | Web app framework |
| Plotly | Interactive charts & maps |
| Pandas | Data processing |

---

## 📂 Project Structure

```
├── app.py                  # Streamlit dashboard
├── lab_1.ipynb             # Data processing notebook
├── steel_lab/              # Helper modules (config, maps, storage)
├── data/processed/         # Processed CSVs (output of notebook)
├── litpop/                 # LitPop exposure data
├── requirements.txt
└── Plant-level_data_Global_Iron_and_Steel_Tracker_June_2026_V1.xlsx
```

---

## 📦 Installation & Run locally

```bash
git clone https://github.com/mariusrang/steel-industry-geospatial-analysis.git
cd steel-industry-geospatial-analysis
pip install -r requirements.txt
streamlit run app.py
```

> ⚠️ Run `lab_1.ipynb` first to generate the processed data in `data/processed/`.

---

## 📚 Data Sources

- **[Global Energy Monitor](https://globalenergymonitor.org/)** — Global Iron and Steel Tracker, June 2026
- **[CLIMADA LitPop](https://climada-python.readthedocs.io/en/stable/tutorial/climada_entity_LitPop.html)** (ETH Zurich) — Produced-capital asset exposure at 300 arc-second resolution for China, India and Japan
