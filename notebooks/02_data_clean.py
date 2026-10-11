# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 02 — The inputs of this finding
#
# | Table | From | Content |
# |---|---|---|
# | `room_to_green.csv` | Cadastre footprints (01), Urban Atlas 2018 (01) | per assessed building: share of the land within 50, 100 and 200 m of its footprint that lies in an Urban Atlas class that could be greened |
# | `buildings.csv` | analysis `building_risk.parquet`, `vulnerability_by_building.csv` | per building, map (land cover × climate × return period) and risk: residents, at risk or not; its residents' vulnerability fifth |
#
# **Land that could be greened** (Urban Atlas 2018 codes): discontinuous low and very low
# density urban fabric (11230, 11240), construction sites (13300), land without current
# use (13400), green urban areas (14100), sports and leisure facilities (14200),
# agricultural land (21000, 22000, 23000), forests and semi-natural areas (31000, 32000)
# and wetlands (40000). Dense urban fabric, industrial and commercial units, roads,
# railways, extraction sites and water are not. REACHOUT does not publish the cells its
# all-green scenario changes, so this is a proxy for where greening can act.
#
# Vulnerability is the analysis's **rates** version (census-section shares of children,
# elderly people living alone, unemployed, residents without higher education), ranked
# over all residential buildings; residents are split into five groups of equal
# population (Q1 least, Q5 most vulnerable). Whether a building is at risk does not depend
# on the indicator version.

# %%
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

RAW = Path("../data/raw")
sources = json.loads((RAW / "sources.json").read_text())
RESULTS_A = Path(sources["analysis"]["path"]) / "results"
CLEAN = Path("../data/clean")
CLEAN.mkdir(parents=True, exist_ok=True)
CRS = "EPSG:25830"
GREENABLE = ["11230", "11240", "13300", "13400", "14100", "14200",
             "21000", "22000", "23000", "31000", "32000", "40000"]
RADII = [50, 100, 200]

# %% [markdown]
# ## 1. Assessed buildings and their footprints

# %%
group = pd.read_csv(RESULTS_A / "vulnerability_by_building.csv").set_index("ID")["vulnerability_group"]
footprints = gpd.read_file(RAW / "cadastre_buildings/A.ES.SDGC.BU.26900.building.gml")
footprints = footprints.to_crs(CRS).rename(columns={"localId": "ID"}).drop_duplicates("ID").set_index("ID")
matched = group.index.intersection(footprints.index)
print(f"{len(group):,} assessed buildings in the analysis; {len(matched):,} found in today's Cadastre "
      f"({len(group) - len(matched)} missing)")
fp = footprints.loc[matched, ["geometry"]]

# %% [markdown]
# ## 2. Land that could be greened around each building

# %%
ua = gpd.read_file(RAW / "urban_atlas_2018_logrono.geojson").to_crs(CRS)
ua["code"] = ua["code_2018"].astype(str)
print(ua.groupby(["code", "class_2018"]).size().to_string())
greenable = ua.loc[ua["code"].isin(GREENABLE)].geometry.union_all()

room = pd.DataFrame(index=fp.index)
for r in RADII:
    zone = fp.geometry.buffer(r)
    room[f"greenable_share_{r}m"] = zone.intersection(greenable).area / zone.area
room = room.join(group)
room.reset_index().to_csv(CLEAN / "room_to_green.csv", index=False)
print(room.groupby("vulnerability_group").median().round(3).to_string())

# %% [markdown]
# ## 3. Residents at risk for every map

# %%
risk = pd.read_parquet(RESULTS_A / "building_risk.parquet", filters=[("variant", "==", "rates")])
keep = ["land_cover", "climate", "rp", "ID", "R", "PFRWB", "PFRMA"]
buildings = risk[keep].copy()
buildings["at_risk_PFRWB"] = buildings["PFRWB"] > 0
buildings["at_risk_PFRMA"] = buildings["PFRMA"] > 0
buildings = buildings.drop(columns=["PFRWB", "PFRMA"]).join(group, on="ID")
buildings.to_csv(CLEAN / "buildings.csv", index=False)
print(f"{buildings.groupby(['land_cover', 'climate', 'rp']).ngroups} maps; "
      f"{buildings['ID'].nunique():,} buildings")
