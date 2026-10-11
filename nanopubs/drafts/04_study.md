# 04 — FORRT Replication Study

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Verify code first:** read the actual reproduction script in `notebooks/03_analysis.py` before writing the methodology field. See `docs/verify-before-drafting.md`.

## Field-by-field draft

<!-- field: study -->
### Short URI suffix for study ID (text input, required)

Slug. Use kebab-case.

```
logrono-vulnerable-room-to-green-study
```

<!-- field: label -->
### Label/name of replication study (text input, required)

Human-readable title.

```
Land that could be greened near the homes of more and less socially vulnerable residents at pluvial flood risk in Logroño
```

<!-- field: type -->
### Choose the study type (dropdown, required)

- [x] Replication Study - replication with different methodology or conditions
- [ ] Reproduction/Replication Study - study that is both, reproduction and replication
- [ ] Reproduction Study - direct reproduction: same methodology, same tools

<!-- field: claim -->
### Choose FORRT claim (search/select, required)

URI of the Claim published in step 03. Pull from `nanopubs/PUBLISHED.md`.

```

```

<!-- field: scope -->
### Describe what part of the claim is reproduced/replicated. (textarea, required)

The **scope** of the claim being tested. Which aspect, what's in/out of scope. NOT methodology. NOT results. See `docs/pico-study-outcome-levels.md`.

```
Whether, among the residents of buildings at pluvial flood risk in Logroño (Spain), those in the most socially vulnerable fifth have a smaller share of land that could be greened near their homes than those in the least vulnerable fifth. In scope: every residential building inside the area modelled by all REACHOUT scenarios; residents at risk with the current green cover under the seven design storms (return periods of 2 to 200 years) and present and future (EURO-CORDEX median and 90th percentile) rainfall, for both risk indices; land within 100 m of each building (50 m and 200 m, and the other REACHOUT land covers, as robustness). Out of scope: whether greening that land would reduce flood risk, or why greening helps the most vulnerable residents least (a within-group check found no consistent link between room to green and leaving risk, so no causal claim is made); land that REACHOUT's all-green scenario actually changes, which is not published; other measures such as storage or drainage; the validity of the vulnerability indicators.
```

<!-- field: methodology -->
### Describe how the claim is reproduced/replicated. (textarea, required)

The **method** in plain prose. Read `notebooks/03_analysis.py` and any config files first. NOT exact numerical results.

```
Residents at risk and vulnerability: the shared analysis Logroño flood-adaptation scenarios, release v0.2.0 (10.5281/zenodo.23302113), whose result tables this chain reads: building-level risk from REACHOUT's SaferRAIN flood maps (10.5281/zenodo.14035876) through building-climate-risk v0.2.1 (10.5281/zenodo.23285504) with the framework of Vogelbacher et al. (2026); a building's residents are at risk for a risk index when that index is above zero. Social vulnerability: the census-section-rate version of the framework's index, ranked over all residential buildings, with residents split into five groups of equal population. Building footprints: Spanish Cadastre INSPIRE Buildings for Logroño (ATOM download; all 4,540 assessed buildings matched by Cadastre identifier). Land that could be greened: Copernicus Urban Atlas 2018 (FUA ES018L2, 10.2909/9911fe21-57f6-46fb-ae26-d76e7bb6378f) classes of low and very low density urban fabric, construction sites, land without current use, green urban areas, sports and leisure facilities, agricultural, forest and semi-natural land and wetlands; for each building, the share of the area within 100 m of its footprint lying in those classes. Measure: per climate, return period and risk index, the resident-weighted mean share for the at-risk residents of the most and of the least vulnerable fifth, with one-sided permutation tests in each direction (buildings shuffled between the two groups, 10,000 times, fixed seed). Decision rule, fixed before running: the finding holds if the most vulnerable fifth has less land in every current-cover comparison at 100 m and none shows significantly more. Robustness: 50 m and 200 m and the other land covers; cross-check against the same measure computed in the analysis release.
```

<!-- field: deviation -->
### Describe any deviations from original methodology. (textarea, optional)

What's different from the original method. Verify against the actual code, don't guess.

```
From the framework of Vogelbacher et al. (2026), inherited from the analysis: (1) hazard model REACHOUT SaferRAIN (fill-and-spill with infiltration, no sewer network, 15-minute storms) instead of VISDOM-SWMM; (2) social vulnerability from census-section rates rather than counts per building, so every building in a census section has the same vulnerability; (3) residents fixed at 2021; (4) the 157 buildings near the edge of the modelled area (1,851 residents) are left out. New in this study: (5) land that could be greened is a proxy from Urban Atlas land-use classes, not REACHOUT's greening layer, which is not published; (6) the Cadastre footprints are today's download (Last-Modified 21 August 2026), matched to the analysis's buildings by identifier.
```

<!-- field: keyword -->
### Search keywords (Wikidata) (search/select, optional)

Provide labels (not QIDs) — the Wikidata search picks up labels.

- social vulnerability (Q581445)
- environmental justice (Q1479527)
- urban green space (Q22652)
- nature-based solutions (Q2421934)
- flood risk (Q2288778)
- urban flooding (Q15909735)
- Logroño (Q14325)

<!-- field: discipline -->
### Search discipline (Wikidata) (search/select, optional)

Provide labels.

- urban planning (Q69883)

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 04.
