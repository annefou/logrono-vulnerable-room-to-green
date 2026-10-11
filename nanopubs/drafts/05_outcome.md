# 05 — FORRT Replication Outcome

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> **Verify the actual numerical results first** by reading `results/` and `notebooks/03_analysis.py`. Don't quote numbers from memory. See `docs/verify-before-drafting.md`.

## Field-by-field draft

<!-- field: outcome -->
### Short URI suffix for outcome ID (text input, required)

Slug. Use kebab-case.

```
logrono-vulnerable-room-to-green-outcome
```

<!-- field: label -->
### Plain-text label for the outcome (text input, required)

Descriptive title.

```
The most socially vulnerable residents at pluvial flood risk in Logroño have less room to green near their homes
```

<!-- field: study -->
### Choose study (search/select, required)

URI of the Replication Study published in step 04. Pull from `nanopubs/PUBLISHED.md`.

```

```

<!-- field: repo -->
### Repository URL (text input, required)

Use the Zenodo **version DOI** URL for the release the results came from — not a
bare branch URL, and not the concept DOI.

> **Why not the bare repo URL.** `https://github.com/ORG/REPO` names a *moving
> branch*. This Outcome asserts "this code produced this number", in a signed,
> immutable record. A branch URL means that assertion points at whatever `main`
> happens to be years from now — code that may never have produced the number
> above. A concept DOI has the same flaw: it resolves to the latest version.
> The version DOI pins the exact release. `docs/chain-decision-tree.md` § Anchor
> ranks the options: SWHID > Zenodo DOI > repo URL > Wayback.
>
> Both DOIs and the SWHID are in `CITATION.cff` under `identifiers:`, recorded
> automatically at release by `.github/workflows/release-identifiers.yml`. Take
> the one described as *"Version DOI"*.

```
https://doi.org/{{ZENODO_VERSION_DOI}}
```

<!-- field: date -->
### Choose completion date (text input, required)

```
2026-10-11
```

<!-- field: validationStatus -->
### Choose validation status (dropdown, required)


This dropdown maps to the CiTO intention in step 06: Validated → `confirms`, PartiallySupported → `qualifies`, Contradicted → `disputes`.

- [ ] contradicted
- [ ] inconclusive
- [ ] not tested
- [ ] partially supported
- [x] validated

<!-- field: confidenceLevel -->
### Choose confidence level (dropdown, required)

_Vocabulary not yet captured._

```

```

- [x] high - Strong evidence, mostly agrees with original
- [ ] low - Limited evidence, significant disagreement
- [ ] moderate - Adequate evidence, partial agreement
- [ ] very high - Extensive evidence, high agreement with original
- [ ] very low - Minimal evidence, major disagreement

<!-- field: conclusion -->
### Describe the overall conclusion about the original claim (textarea, required)

Substantive interpretation. Headline comparison: replication's number vs the paper's number, sign + significance.

```
Validated. In Logroño (Spain), the residents at pluvial flood risk in the most socially vulnerable fifth have about a quarter of the land that could be greened near their homes that those in the least vulnerable fifth have: on average 4 to 6 % of the land within 100 m of their buildings against 17 to 20 %. This holds in all 42 comparisons with the current green cover (3 climates, 7 return periods, 2 risk indices), each significant, and in all 492 comparisons across 50, 100 and 200 m and every REACHOUT land cover. The finding is descriptive: within each vulnerability group, residents with more land that could be greened were not consistently the ones that city-wide greening takes out of risk, so it does not explain why greening helps the most vulnerable least. It matters for adaptation planning: near the homes of the most vulnerable residents at risk there is little room for greening, so protecting them will likely depend on other measures.
```

<!-- field: evidence -->
### Describe the evidence that supports your conclusion (textarea, required)

Numerical results, test statistics, model coefficients. Read directly from `results/`.

```
Current green cover, 100 m, resident-weighted mean share of land that could be greened: least vulnerable fifth 17.2 to 19.6 %, most vulnerable fifth 3.8 to 5.7 % over all 42 comparisons; e.g. 100-year storm with present rainfall, risk to well-being 19.2 % (9,050 residents in 107 buildings) against 4.7 % (3,733 residents in 93 buildings), risk to mobility 17.4 % (12,946 residents, 177 buildings) against 3.9 % (5,887 residents, 170 buildings). Less in 42 of 42 comparisons, all with one-sided permutation p <= 0.0002 (10,000 permutations); significantly more in none. Radius: 50 m 11.4 to 14.3 % against 2.7 to 3.7 %; 200 m 23.8 to 26.1 % against 5.1 to 6.7 %. All 492 comparisons across radii and land covers in the same direction (largest p = 0.046). All 4,540 assessed buildings matched in the Cadastre; the measure equals the analysis release's own to rounding error. Context (not part of the finding): among residents at risk with the current cover, those that city-wide greening takes out of risk had more land that could be greened than those who remain in 0 of 20 cases for the least vulnerable fifth and 9 of 20 for the most vulnerable (results/room_vs_taken_out.csv). Figure: figures/main_result.png; checks: results/claim_test.json, results/room_robustness.csv.
```

<!-- field: limitations -->
### Describe what limits the conclusions of the study (textarea, optional)

Honest caveats. If the result is partial or contradicted, say so plainly. Don't overclaim.

```
Land that could be greened is a proxy from Urban Atlas 2018 land-use classes, not the cells REACHOUT's all-green scenario changes, which are not published; small courtyards, verges and roofs are not counted, and some counted land may not be available. The finding is descriptive and says nothing about whether greening that land would reduce flood risk. Social vulnerability comes from census-section rates, so all buildings of a section share one value, and it was not validated against impact data. Residents at risk come from REACHOUT's fill-and-spill flood model without sewers and are fixed at 2021; 157 buildings near the edge of the modelled area (1,851 residents) are left out. Many comparisons are made and they overlap, so individual p-values are not adjusted; the finding rests on the direction holding in every comparison.
```

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 05.
