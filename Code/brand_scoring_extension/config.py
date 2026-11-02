"""Where everything lives. The data stays outside OneDrive (NDA)."""

import os
from pathlib import Path

DATA_ROOT = Path(os.getenv("EURPAC_DATA", r"C:\CapstoneData"))
DATA_DIR = DATA_ROOT / "data"
RAW_ALL = DATA_DIR / "sales_dataset"                      # NIQ's raw feed, 387 files
KRISTIN_FILE = DATA_DIR / "sales_dataset_spirits_weeks"   # only used to check step 1

PROJECT_ROOT = Path(__file__).resolve().parent
CAPSTONE = PROJECT_ROOT.parents[1]                        # .../Capstone
TRUTH_DIR = CAPSTONE / "Data"                             # hand-labeled truth sets live here
TRUTH_FILE = TRUTH_DIR / "vodka_single_ext_truth_set.csv"  # Kristin's 112 vodka labels
OUTPUTS = PROJECT_ROOT / "outputs"                        # gitignored


def check():
    if not DATA_DIR.exists():
        raise SystemExit(f"Data folder not found: {DATA_DIR}")
    if any(s in str(DATA_ROOT).lower() for s in ("onedrive", "dropbox", "google drive")):
        raise SystemExit(f"Data is in a cloud-synced folder: {DATA_ROOT}. NDA: keep it local.")
