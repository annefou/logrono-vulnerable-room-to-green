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
# # 01 — Data download
#
# This chain tests one finding about the residents at pluvial flood risk in Logroño
# (Spain): whether the most socially vulnerable of them have less land that could be
# greened near their homes than the least vulnerable. Three inputs:
#
# | Component | Source | Licence |
# |---|---|---|
# | Residents at risk, vulnerability | **Logroño flood-adaptation scenarios**, release v0.2.0, Zenodo [10.5281/zenodo.23302113](https://doi.org/10.5281/zenodo.23302113): committed result tables (`building_risk.parquet`, `vulnerability_by_building.csv`, `where_vulnerable.csv`) | MIT (code); data under their own licences |
# | Building footprints | Spanish Cadastre, INSPIRE Buildings, municipality 26900 (Logroño), ATOM bulk download | Catastro INSPIRE licence of access and use (DG del Catastro, v1.0, 2016): use of transformed data; original files not redistributed |
# | Land use | Copernicus Urban Atlas 2018, FUA ES018L2 Logroño, [10.2909/9911fe21-57f6-46fb-ae26-d76e7bb6378f](https://doi.org/10.2909/9911fe21-57f6-46fb-ae26-d76e7bb6378f), EEA public map service | Copernicus (free, full and open) |
#
# The Cadastre and Urban Atlas files are downloaded here and never committed or
# released: only values derived from them (land that could be greened per building) are.
# The Cadastre feed is updated twice a year, so the download date, the server's
# Last-Modified and the checksum are logged; 02 reports how many buildings of the
# analysis match.

# %%
import datetime
import hashlib
import json
import shutil
import time
import zipfile
from pathlib import Path

import requests

# %%
RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS = {
    "name": "logrono-flood-adaptation-scenarios",
    "version": "v0.2.0",
    "doi": "10.5281/zenodo.23302113",
    "record": "23302113",
    "file": "annefou/logrono-flood-adaptation-scenarios-v0.2.0.zip",
    "license": "MIT (code); data under their own licences",
}
ANALYSIS_DIR = RAW_DIR / "analysis"
CADASTRE = {
    "name": "cadastre_buildings",
    "url": "https://www.catastro.hacienda.gob.es/INSPIRE/Buildings/26/26900-LOGRO%C3%91O/A.ES.SDGC.BU.26900.zip",
    "extract": ["A.ES.SDGC.BU.26900.building.gml"],
    "license": "Catastro INSPIRE licence of access and use (v1.0, 2016)",
}
# Municipality extent (Cadastre zoning, EPSG:25830), as in the Logroño replication.
EXTENT_25830 = (537600, 4697500, 554120, 4707640)
URBAN_ATLAS = {
    "name": "urban_atlas_2018_logrono",
    "doi": "10.2909/9911fe21-57f6-46fb-ae26-d76e7bb6378f",
    "layer": "https://image.discomap.eea.europa.eu/arcgis/rest/services/UrbanAtlas/UA_UrbanAtlas_2018/MapServer/2",
    "where": "fua_code='ES018L2'",
    "license": "Copernicus (free, full and open)",
}
HEADERS = {"User-Agent": "logrono-vulnerable-room-to-green (+https://github.com/annefou/logrono-vulnerable-room-to-green)"}


def get(url: str, attempts: int = 6, **kw) -> requests.Response:
    """GET with retries and growing back-off: Zenodo and map services throttle."""
    for i in range(attempts):
        try:
            r = requests.get(url, timeout=600, headers=HEADERS, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if i == attempts - 1:
                raise
            print(f"retry {i + 1} after: {str(e)[:120]}")
            time.sleep(30 * (i + 1))


def digest(path: Path, algo: str = "md5") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# %% [markdown]
# ## The analysis release

# %%
record = get(f"https://zenodo.org/api/records/{ANALYSIS['record']}").json()
entry = next(f for f in record["files"] if f["key"] == ANALYSIS["file"])
expected_md5 = entry["checksum"].removeprefix("md5:")
archive = RAW_DIR / Path(ANALYSIS["file"]).name
if not archive.exists() or digest(archive) != expected_md5:
    with get(entry["links"]["self"], stream=True) as r, open(archive, "wb") as f:
        shutil.copyfileobj(r.raw, f)
assert digest(archive) == expected_md5, "analysis archive does not match Zenodo's MD5"

if not (ANALYSIS_DIR / "Snakefile").exists():
    with zipfile.ZipFile(archive) as z:
        top = {n.split("/")[0] for n in z.namelist()}
        assert len(top) == 1, top
        z.extractall(RAW_DIR)
    (RAW_DIR / top.pop()).rename(ANALYSIS_DIR)
print(f"{archive.name}: MD5 {expected_md5} verified; extracted to {ANALYSIS_DIR}")

# %% [markdown]
# ## Building footprints (Cadastre ATOM)

# %%
zpath = RAW_DIR / Path(CADASTRE["url"]).name
with get(CADASTRE["url"], stream=True) as r, open(zpath, "wb") as f:
    shutil.copyfileobj(r.raw, f)
    last_modified = r.headers.get("Last-Modified")
with zipfile.ZipFile(zpath) as z:
    for n in CADASTRE["extract"]:
        z.extract(n, RAW_DIR / CADASTRE["name"])
cadastre_log = {**CADASTRE, "file": zpath.name, "bytes": zpath.stat().st_size,
                "sha256": digest(zpath, "sha256"), "last_modified": last_modified}
print(f"Cadastre buildings: {cadastre_log['bytes']:,} bytes, Last-Modified {last_modified}")

# %% [markdown]
# ## Land use (Urban Atlas 2018, EEA map service)

# %%
def query_layer(layer: str, where: str, out: Path, page: int = 1000) -> int:
    """Page through an ArcGIS map-service layer over EXTENT_25830; write GeoJSON."""
    params = {"where": where, "geometry": ",".join(map(str, EXTENT_25830)),
              "geometryType": "esriGeometryEnvelope", "inSR": 25830, "outSR": 25830,
              "outFields": "*", "orderByFields": "OBJECTID", "f": "geojson",
              "resultRecordCount": page}
    features, offset = [], 0
    while True:
        batch = get(f"{layer}/query", params={**params, "resultOffset": offset}).json()
        features += batch["features"]
        if len(batch["features"]) < page:
            break
        offset += page
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features,
                               "crs": {"type": "name", "properties": {"name": "EPSG:25830"}}}))
    return len(features)


ua_path = RAW_DIR / f"{URBAN_ATLAS['name']}.geojson"
n = query_layer(URBAN_ATLAS["layer"], URBAN_ATLAS["where"], ua_path)
ua_log = {**URBAN_ATLAS, "extent_epsg25830": EXTENT_25830, "features": n,
          "file": ua_path.name, "sha256": digest(ua_path, "sha256")}
print(f"Urban Atlas: {n} features")

# %% [markdown]
# ## Source log

# %%
log = {"accessed_on": datetime.date.today().isoformat(),
       "analysis": {**ANALYSIS, "md5": expected_md5, "path": str(ANALYSIS_DIR)},
       "cadastre": cadastre_log, "urban_atlas": ua_log}
(RAW_DIR / "sources.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
print(f"logged to {RAW_DIR / 'sources.json'}")
