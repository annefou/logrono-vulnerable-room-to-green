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
# # 03 — Do the most vulnerable residents at risk have less room to green?
#
# The finding under test (AIDA): *in Logroño, the most socially vulnerable residents at
# pluvial flood risk have less land that could be greened near their homes than the least
# vulnerable.*
#
# For every map with the **current green cover** (3 climates × 7 return periods) and both
# risks (well-being, mobility), among the residents at risk:
#
# 1. resident-weighted mean share of land that could be greened within 100 m, most
#    vulnerable fifth (Q5) against least vulnerable fifth (Q1);
# 2. a one-sided permutation test (buildings shuffled between Q1 and Q5, 10,000 times)
#    of "Q5 has less";
# 3. the same at 50 m and 200 m, and with the other land covers, as robustness;
# 4. a cross-check against the analysis release, which computed the same measure for the
#    planned scenario with ponds from its own snapshot of the Cadastre.
#
# **Decision rule, fixed before running:** the finding holds if Q5 has less land that could
# be greened than Q1 in every current-cover comparison at 100 m, and no comparison shows
# significantly more (p < 0.05 in the other direction). Many comparisons are made and they
# are not independent, so an isolated small p-value is not read as evidence.

# %%
import json
from pathlib import Path

import numpy as np
import pandas as pd

CLEAN = Path("../data/clean")
RESULTS = Path("../results")
RESULTS.mkdir(parents=True, exist_ok=True)
sources = json.loads(Path("../data/raw/sources.json").read_text())
RESULTS_A = Path(sources["analysis"]["path"]) / "results"
RADII = [50, 100, 200]
RISKS = ["PFRWB", "PFRMA"]
RNG = np.random.default_rng(20261011)
N_PERM = 10_000

room = pd.read_csv(CLEAN / "room_to_green.csv").set_index("ID")
buildings = pd.read_csv(CLEAN / "buildings.csv")
buildings = buildings[buildings["ID"].isin(room.index)]

# %%
def compare(ids1: pd.Index, ids5: pd.Index, weights: pd.Series, share: pd.Series) -> dict:
    """Resident-weighted mean share, Q5 minus Q1, and one-sided permutation p-values."""
    pooled = ids1.append(ids5)
    w = weights.reindex(pooled).to_numpy()
    ws = w * share.reindex(pooled).to_numpy()
    in5 = np.argsort(RNG.random((N_PERM, len(pooled))), axis=1) < len(ids5)
    w5, ws5 = in5 @ w, in5 @ ws
    null = ws5 / w5 - (ws.sum() - ws5) / (w.sum() - w5)
    m1 = float(np.average(share.reindex(ids1), weights=weights.reindex(ids1)))
    m5 = float(np.average(share.reindex(ids5), weights=weights.reindex(ids5)))
    d = m5 - m1
    return {"buildings_q1": len(ids1), "buildings_q5": len(ids5),
            "residents_q1": float(weights.reindex(ids1).sum()), "residents_q5": float(weights.reindex(ids5).sum()),
            "mean_share_q1": m1, "mean_share_q5": m5, "difference": d,
            "p_q5_less": float((1 + (null <= d).sum()) / (1 + N_PERM)),
            "p_q5_more": float((1 + (null >= d).sum()) / (1 + N_PERM))}


rows = []
for (lc, cl, rp), g in buildings.groupby(["land_cover", "climate", "rp"]):
    g = g.set_index("ID")
    for r in RISKS:
        at = g[g[f"at_risk_{r}"]]
        ids1 = at.index[at["vulnerability_group"] == 1]
        ids5 = at.index[at["vulnerability_group"] == 5]
        if len(ids1) == 0 or len(ids5) == 0:
            continue
        for rad in RADII:
            rows.append({"land_cover": lc, "climate": cl, "rp": rp, "risk": r, "radius_m": rad,
                         **compare(ids1, ids5, at["R"], room[f"greenable_share_{rad}m"])})
comp = pd.DataFrame(rows)
comp.to_csv(RESULTS / "room_comparisons.csv", index=False)

main = comp[(comp["land_cover"] == "Baseline") & (comp["radius_m"] == 100)]
print(main[["climate", "rp", "risk", "residents_q1", "residents_q5", "mean_share_q1", "mean_share_q5",
            "p_q5_less", "p_q5_more"]].round(3).to_string(index=False))

# %% [markdown]
# ## Robustness: radius and land cover

# %%
robust = (comp.assign(q5_less=comp["difference"] < 0, sig_less=comp["p_q5_less"] < 0.05,
                      sig_more=comp["p_q5_more"] < 0.05)
          .groupby(["land_cover", "radius_m"])
          .agg(comparisons=("q5_less", "size"), q5_less=("q5_less", "sum"),
               significant_less=("sig_less", "sum"), significant_more=("sig_more", "sum"),
               mean_share_q1=("mean_share_q1", "mean"), mean_share_q5=("mean_share_q5", "mean"))
          .reset_index())
robust.to_csv(RESULTS / "room_robustness.csv", index=False)
print(robust.round(3).to_string(index=False))

# %% [markdown]
# ## Cross-check against the analysis release (planned scenario with ponds, 100 m)
#
# The release's notebook 06 measured the same share from its own copy of the Cadastre,
# with at-risk sets from the `counts` variant; the at-risk sets are the same, so the means
# differ only through Cadastre updates between the two downloads.

# %%
ref = pd.read_csv(RESULTS_A / "where_vulnerable.csv")
ref = ref.pivot_table(index=["climate", "rp", "risk"], columns="group", values="greenable_share")
ref.columns = [f"release_q{c}" for c in ref.columns]
ours = comp[(comp["land_cover"] == "NBSplanned_plus") & (comp["radius_m"] == 100)].set_index(["climate", "rp", "risk"])
check = ours[["mean_share_q1", "mean_share_q5"]].join(ref, how="inner")
check["abs_diff_q1"] = (check["mean_share_q1"] - check["release_q1"]).abs()
check["abs_diff_q5"] = (check["mean_share_q5"] - check["release_q5"]).abs()
check.reset_index().to_csv(RESULTS / "crosscheck_release.csv", index=False)
print(f"{len(check)} comparisons; largest absolute difference "
      f"{check[['abs_diff_q1', 'abs_diff_q5']].max().max():.4f}")

# %% [markdown]
# ## Does the finding hold?

# %%
n_main = len(main)
claim = {
    "aida": "In Logroño, the most socially vulnerable residents at pluvial flood risk have less land that "
            "could be greened near their homes than the least vulnerable.",
    "comparisons_current_cover_100m": n_main,
    "q5_less_in": int((main["difference"] < 0).sum()),
    "significant_q5_less_p_lt_0.05": int((main["p_q5_less"] < 0.05).sum()),
    "significant_q5_more_p_lt_0.05": int((main["p_q5_more"] < 0.05).sum()),
    "mean_share_q1_range": [float(main["mean_share_q1"].min()), float(main["mean_share_q1"].max())],
    "mean_share_q5_range": [float(main["mean_share_q5"].min()), float(main["mean_share_q5"].max())],
    "all_comparisons_all_radii_all_covers": int(len(comp)),
    "q5_less_in_all": int((comp["difference"] < 0).sum()),
    "buildings_matched_in_cadastre": int(len(room)),
    "crosscheck_max_abs_diff": float(check[["abs_diff_q1", "abs_diff_q5"]].max().max()),
}
claim["holds"] = (claim["q5_less_in"] == n_main and claim["significant_q5_more_p_lt_0.05"] == 0)
(RESULTS / "claim_test.json").write_text(json.dumps(claim, indent=2, ensure_ascii=False))
claim
