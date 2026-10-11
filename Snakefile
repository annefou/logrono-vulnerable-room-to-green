# Snakefile — orchestrates the pipeline end-to-end.
#
# Each rule wraps a notebook executed via jupytext. Inputs are files that are never
# committed (data/), so a fresh checkout always starts from the download.
#
# Usage:
#   snakemake --cores 1                  # run everything
#   snakemake --cores 1 -n               # dry run

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"


rule all:
    input:
        f"{FIGURES}/main_result.png",
        f"{RESULTS}/claim_test.json",


# ---------- 01: the analysis release, Cadastre buildings, Urban Atlas ----------
rule data_download:
    output:
        f"{DATA}/raw/sources.json",
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 01_data_download.py 2>&1 | tee ../{{log}}"


# ---------- 02: the inputs of this finding ----------
rule data_clean:
    input:
        f"{DATA}/raw/sources.json",
    output:
        f"{DATA}/clean/room_to_green.csv",
        f"{DATA}/clean/buildings.csv",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 02_data_clean.py"


# ---------- 03: the finding ----------
rule analysis:
    input:
        f"{DATA}/clean/room_to_green.csv",
        f"{DATA}/clean/buildings.csv",
    output:
        f"{RESULTS}/claim_test.json",
        f"{RESULTS}/room_comparisons.csv",
        f"{RESULTS}/room_robustness.csv",
        f"{RESULTS}/crosscheck_release.csv",
        f"{RESULTS}/room_vs_taken_out.csv",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 03_analysis.py"


# ---------- 04: figures ----------
rule figures:
    input:
        f"{RESULTS}/room_comparisons.csv",
    output:
        f"{FIGURES}/main_result.png",
    shell:
        f"cd {{NOTEBOOKS}} && jupytext --to notebook --execute 04_figures.py"
