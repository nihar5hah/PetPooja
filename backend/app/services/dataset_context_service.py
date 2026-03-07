from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from app.core.config import settings


REQUIRED_MENU_COLUMNS = {
    "item_name",
    "category",
    "selling_price",
    "food_cost",
}

FULL_MENU_COLUMNS = {
    "item_id",
    "item_name",
    "category",
    "subcategory",
    "selling_price",
    "food_cost",
    "contribution_margin",
    "margin_pct",
    "prep_time_min",
    "is_veg",
    "status",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_dataset_path(path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (_repo_root() / path).resolve()


def menu_dataset_path() -> Path:
    return _resolve_dataset_path(settings.dataset_menu_csv_path)


def pos_dataset_path() -> Path:
    return _resolve_dataset_path(settings.dataset_pos_csv_path)


@lru_cache(maxsize=1)
def load_menu_dataset() -> pd.DataFrame:
    full_menu = load_full_menu_dataset()
    if full_menu.empty:
        return pd.DataFrame()

    menu = full_menu[["item_name", "category", "selling_price", "food_cost"]].copy()
    menu = menu.dropna(subset=["item_name"]).drop_duplicates(subset=["item_name"], keep="last")
    return menu


@lru_cache(maxsize=1)
def load_full_menu_dataset() -> pd.DataFrame:
    path = menu_dataset_path()
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    missing = FULL_MENU_COLUMNS - set(df.columns)
    if missing:
        return pd.DataFrame()

    menu = df[list(FULL_MENU_COLUMNS)].copy()
    menu["item_name"] = menu["item_name"].astype(str).str.strip()
    menu["category"] = menu["category"].astype(str).str.strip()
    menu["subcategory"] = menu["subcategory"].astype(str).str.strip()
    menu["status"] = menu["status"].astype(str).str.strip()
    menu["item_id"] = menu["item_id"].astype(str).str.strip()
    menu["selling_price"] = pd.to_numeric(menu["selling_price"], errors="coerce")
    menu["food_cost"] = pd.to_numeric(menu["food_cost"], errors="coerce")
    menu["contribution_margin"] = pd.to_numeric(menu["contribution_margin"], errors="coerce")
    menu["margin_pct"] = pd.to_numeric(menu["margin_pct"], errors="coerce")
    menu["prep_time_min"] = pd.to_numeric(menu["prep_time_min"], errors="coerce")
    menu = menu[menu["status"].str.lower() == "active"].copy()
    menu = menu.dropna(subset=["item_name"]).drop_duplicates(subset=["item_name"], keep="last")
    return menu


@lru_cache(maxsize=1)
def menu_item_lookup() -> dict[str, dict[str, float | str]]:
    df = load_full_menu_dataset()
    if df.empty:
        return {}
    out: dict[str, dict[str, float | str]] = {}
    for rec in df.to_dict(orient="records"):
        out[str(rec["item_name"]).lower()] = {
            "item_id": str(rec["item_id"]),
            "item_name": str(rec["item_name"]),
            "category": str(rec["category"]),
            "subcategory": str(rec["subcategory"]),
            "selling_price": float(rec["selling_price"]) if pd.notna(rec["selling_price"]) else 0.0,
            "food_cost": float(rec["food_cost"]) if pd.notna(rec["food_cost"]) else 0.0,
            "contribution_margin": float(rec["contribution_margin"]) if pd.notna(rec["contribution_margin"]) else 0.0,
            "margin_pct": float(rec["margin_pct"]) if pd.notna(rec["margin_pct"]) else 0.0,
            "prep_time_min": float(rec["prep_time_min"]) if pd.notna(rec["prep_time_min"]) else 0.0,
            "is_veg": str(rec["is_veg"]),
            "status": str(rec["status"]),
        }
    return out


def get_menu_item_fallback(item_name: str) -> dict[str, float | str] | None:
    return menu_item_lookup().get(item_name.strip().lower())


def load_pos_dataset() -> pd.DataFrame:
    path = pos_dataset_path()
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)
