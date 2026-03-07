"""Extended analytics service — computes all 10 metric categories dynamically from pos_transactions."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ComboRule, MenuMetric, PosTransaction
from app.services.dataset_context_service import get_menu_item_fallback
from app.services.llm_recommendation_service import generate_item_recommendations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_transactions_df(db: Session, restaurant_id: str) -> pd.DataFrame:
    rows = db.execute(
        select(
            PosTransaction.order_id,
            PosTransaction.transaction_date,
            PosTransaction.item_name,
            PosTransaction.category,
            PosTransaction.quantity,
            PosTransaction.unit_price,
            PosTransaction.food_cost_per_unit,
            PosTransaction.line_revenue,
            PosTransaction.line_contribution_margin,
        ).where(PosTransaction.restaurant_id == restaurant_id)
    ).all()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=[
        "order_id", "transaction_date", "item_name", "category",
        "quantity", "unit_price", "food_cost_per_unit",
        "line_revenue", "line_contribution_margin",
    ])

    for idx, row in df.iterrows():
        fallback = get_menu_item_fallback(str(row["item_name"]))
        if not fallback:
            continue
        category_val = str(row.get("category", "")).strip().lower()
        if not category_val or category_val == "nan" or category_val == "uncategorized":
            df.at[idx, "category"] = str(fallback["category"])
        if pd.isna(row.get("unit_price")):
            df.at[idx, "unit_price"] = float(fallback["selling_price"])
        if pd.isna(row.get("food_cost_per_unit")):
            df.at[idx, "food_cost_per_unit"] = float(fallback["food_cost"])

    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)
    df["food_cost_per_unit"] = pd.to_numeric(df["food_cost_per_unit"], errors="coerce").fillna(0.0)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["line_food_cost"] = df["food_cost_per_unit"] * df["quantity"]
    return df


def _build_item_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    items = df.groupby("item_name").agg(
        category=("category", lambda s: s.mode().iloc[0] if not s.mode().empty else str(s.iloc[0])),
        total_qty=("quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_margin=("line_contribution_margin", "sum"),
        avg_unit_price=("unit_price", "mean"),
        avg_food_cost=("food_cost_per_unit", "mean"),
        order_count=("order_id", "nunique"),
        first_date=("transaction_date", "min"),
        last_date=("transaction_date", "max"),
    ).reset_index()

    span = (items["last_date"] - items["first_date"]).dt.days.clip(lower=0) + 1
    items["sales_velocity"] = items["total_qty"] / span
    items["margin_pct"] = (items["total_margin"] / items["total_revenue"].clip(lower=0.01)) * 100
    items.drop(columns=["first_date", "last_date"], inplace=True)
    return items


def _menu_metric_lookup(db: Session, restaurant_id: str) -> dict[str, dict[str, float | str]]:
    metrics = db.execute(
        select(
            MenuMetric.item_name,
            MenuMetric.menu_class,
            MenuMetric.popularity_score,
            MenuMetric.margin_score,
            MenuMetric.total_sales_qty,
            MenuMetric.total_revenue,
            MenuMetric.avg_margin,
        ).where(MenuMetric.restaurant_id == restaurant_id)
    ).all()
    return {
        row.item_name: {
            "menu_class": row.menu_class,
            "popularity_score": float(row.popularity_score),
            "margin_score": float(row.margin_score),
            "total_sales_qty": int(row.total_sales_qty),
            "total_revenue": float(row.total_revenue),
            "avg_margin": float(row.avg_margin),
        }
        for row in metrics
    }


# ---------------------------------------------------------------------------
# 1. Order-level feature engineering
# ---------------------------------------------------------------------------

def get_order_level_metrics(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    orders = df.groupby("order_id").agg(
        total_items=("quantity", "sum"),
        unique_items=("item_name", "nunique"),
        order_revenue=("line_revenue", "sum"),
        order_food_cost=("line_food_cost", "sum"),
        order_margin=("line_contribution_margin", "sum"),
    ).reset_index()

    orders["avg_item_price"] = orders["order_revenue"] / orders["total_items"].clip(lower=1)

    return orders.to_dict(orient="records")


# ---------------------------------------------------------------------------
# 2. Item-level feature engineering
# ---------------------------------------------------------------------------

def get_item_level_metrics(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    total_orders = df["order_id"].nunique()
    total_revenue = df["line_revenue"].sum()

    items = df.groupby("item_name").agg(
        total_qty_sold=("quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_margin=("line_contribution_margin", "sum"),
        total_food_cost=("line_food_cost", "sum"),
        avg_unit_price=("unit_price", "mean"),
        avg_food_cost=("food_cost_per_unit", "mean"),
        order_count=("order_id", "nunique"),
        first_date=("transaction_date", "min"),
        last_date=("transaction_date", "max"),
    ).reset_index()

    items["avg_margin_per_unit"] = items["total_margin"] / items["total_qty_sold"].clip(lower=1)
    items["margin_pct"] = (items["total_margin"] / items["total_revenue"].clip(lower=0.01)) * 100
    items["order_frequency"] = items["order_count"] / max(total_orders, 1)
    items["revenue_share_pct"] = (items["total_revenue"] / max(total_revenue, 0.01)) * 100

    span = (items["last_date"] - items["first_date"]).dt.days.clip(lower=0) + 1
    items["sales_velocity"] = items["total_qty_sold"] / span
    items["revenue_per_day"] = items["total_revenue"] / span

    items.drop(columns=["first_date", "last_date"], inplace=True)
    return items.to_dict(orient="records")


# ---------------------------------------------------------------------------
# 3. Category-level metrics
# ---------------------------------------------------------------------------

def get_category_level_metrics(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    total_rev = df["line_revenue"].sum()
    total_margin = df["line_contribution_margin"].sum()

    cats = df.groupby("category").agg(
        item_count=("item_name", "nunique"),
        total_qty_sold=("quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_margin=("line_contribution_margin", "sum"),
        total_food_cost=("line_food_cost", "sum"),
        avg_unit_price=("unit_price", "mean"),
        order_count=("order_id", "nunique"),
    ).reset_index()

    cats["revenue_share_pct"] = (cats["total_revenue"] / max(total_rev, 0.01)) * 100
    cats["margin_share_pct"] = (cats["total_margin"] / max(total_margin, 0.01)) * 100
    cats["avg_margin_pct"] = (cats["total_margin"] / cats["total_revenue"].clip(lower=0.01)) * 100

    return cats.to_dict(orient="records")


# ---------------------------------------------------------------------------
# 4. Restaurant-level KPIs
# ---------------------------------------------------------------------------

def get_restaurant_kpis(db: Session, restaurant_id: str) -> dict:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return {
            "total_orders": 0, "total_revenue": 0.0, "total_profit": 0.0,
            "avg_order_value": 0.0, "avg_profit_per_order": 0.0,
            "overall_margin_pct": 0.0,
        }

    n_orders = df["order_id"].nunique()
    total_revenue = float(df["line_revenue"].sum())
    total_profit = float(df["line_contribution_margin"].sum())
    aov = total_revenue / max(n_orders, 1)
    avg_profit = total_profit / max(n_orders, 1)
    margin_pct = (total_profit / max(total_revenue, 0.01)) * 100

    return {
        "total_orders": n_orders,
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "avg_order_value": round(aov, 2),
        "avg_profit_per_order": round(avg_profit, 2),
        "overall_margin_pct": round(margin_pct, 2),
    }


# ---------------------------------------------------------------------------
# 5. Menu engineering extensions
# ---------------------------------------------------------------------------

def get_menu_engineering_extended(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    # Load existing menu metrics for menu_class
    metrics = db.execute(
        select(MenuMetric.item_name, MenuMetric.menu_class, MenuMetric.popularity_score, MenuMetric.margin_score)
        .where(MenuMetric.restaurant_id == restaurant_id)
    ).all()
    class_map = {r.item_name: r.menu_class for r in metrics}
    pop_map = {r.item_name: float(r.popularity_score) for r in metrics}
    margin_map = {r.item_name: float(r.margin_score) for r in metrics}

    total_orders = df["order_id"].nunique()
    total_rev = df["line_revenue"].sum()

    items = df.groupby("item_name").agg(
        total_qty=("quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_margin=("line_contribution_margin", "sum"),
        avg_unit_price=("unit_price", "mean"),
        order_count=("order_id", "nunique"),
    ).reset_index()

    result = []
    for _, row in items.iterrows():
        name = row["item_name"]
        rev_share = float(row["total_revenue"]) / max(total_rev, 0.01) * 100
        margin_pct = float(row["total_margin"]) / max(float(row["total_revenue"]), 0.01) * 100
        order_freq = row["order_count"] / max(total_orders, 1)

        # Ranks (will be populated after sorting)
        result.append({
            "item_name": name,
            "menu_class": class_map.get(name, "UNKNOWN"),
            "popularity_score": pop_map.get(name, 0.0),
            "margin_score": margin_map.get(name, 0.0),
            "revenue_share_pct": round(rev_share, 2),
            "margin_pct": round(margin_pct, 2),
            "order_frequency": round(order_freq, 4),
            "total_revenue": float(row["total_revenue"]),
            "total_margin": float(row["total_margin"]),
            "avg_unit_price": float(row["avg_unit_price"]),
        })

    # Add ranks
    result.sort(key=lambda x: x["total_revenue"], reverse=True)
    for i, item in enumerate(result):
        item["revenue_rank"] = i + 1

    result.sort(key=lambda x: x["total_margin"], reverse=True)
    for i, item in enumerate(result):
        item["margin_rank"] = i + 1

    result.sort(key=lambda x: x["popularity_score"], reverse=True)
    for i, item in enumerate(result):
        item["popularity_rank"] = i + 1

    return result


# ---------------------------------------------------------------------------
# 6. Popularity vs Profitability Indices
# ---------------------------------------------------------------------------

def get_popularity_profitability(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    total_orders = df["order_id"].nunique()

    items = df.groupby("item_name").agg(
        total_qty=("quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_margin=("line_contribution_margin", "sum"),
        order_count=("order_id", "nunique"),
    ).reset_index()

    total_qty = items["total_qty"].sum()
    total_margin = items["total_margin"].sum()

    items["demand_index"] = items["total_qty"] / max(total_qty, 1)
    items["profitability_index"] = items["total_margin"] / max(total_margin, 0.01)

    return items[["item_name", "demand_index", "profitability_index", "total_qty", "total_margin", "order_count"]].to_dict(orient="records")


# ---------------------------------------------------------------------------
# 7. Advanced market basket metrics (from combo_rules)
# ---------------------------------------------------------------------------

def get_advanced_basket_metrics(db: Session, restaurant_id: str) -> list[dict]:
    rows = db.execute(
        select(ComboRule)
        .where(ComboRule.restaurant_id == restaurant_id)
        .order_by(ComboRule.confidence.desc())
    ).scalars().all()

    return [
        {
            "antecedent_item": r.antecedent_item,
            "consequent_item": r.consequent_item,
            "support": float(r.support),
            "confidence": float(r.confidence),
            "lift": float(r.lift),
            "conviction": float(r.conviction) if r.conviction is not None else None,
            "leverage": float(r.leverage) if r.leverage is not None else None,
            "co_order_frequency": int(r.co_order_frequency) if r.co_order_frequency is not None else None,
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# 8. Combo performance metrics
# ---------------------------------------------------------------------------

def get_combo_performance(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    combos = db.execute(
        select(ComboRule.antecedent_item, ComboRule.consequent_item, ComboRule.confidence, ComboRule.lift)
        .where(ComboRule.restaurant_id == restaurant_id)
    ).all()

    if not combos:
        return []

    # Pre-compute per-item aggregates
    item_stats = df.groupby("item_name").agg(
        avg_revenue=("line_revenue", "mean"),
        avg_margin=("line_contribution_margin", "mean"),
    ).to_dict("index")

    # per-order revenue/margin
    order_items = df.groupby("order_id")["item_name"].apply(set).to_dict()
    order_revenue = df.groupby("order_id")["line_revenue"].sum().to_dict()
    order_margin = df.groupby("order_id")["line_contribution_margin"].sum().to_dict()

    result = []
    for c in combos:
        a, b = c.antecedent_item, c.consequent_item
        a_stats = item_stats.get(a, {"avg_revenue": 0, "avg_margin": 0})
        b_stats = item_stats.get(b, {"avg_revenue": 0, "avg_margin": 0})

        pair_avg_revenue = float(a_stats["avg_revenue"]) + float(b_stats["avg_revenue"])
        pair_avg_margin = float(a_stats["avg_margin"]) + float(b_stats["avg_margin"])

        # Orders containing both items
        co_orders = [oid for oid, items in order_items.items() if a in items and b in items]
        co_order_avg_revenue = float(np.mean([order_revenue[oid] for oid in co_orders])) if co_orders else 0.0
        co_order_avg_margin = float(np.mean([order_margin[oid] for oid in co_orders])) if co_orders else 0.0

        result.append({
            "antecedent_item": a,
            "consequent_item": b,
            "confidence": float(c.confidence),
            "lift": float(c.lift),
            "pair_avg_revenue": round(pair_avg_revenue, 2),
            "pair_avg_margin": round(pair_avg_margin, 2),
            "co_order_avg_revenue": round(co_order_avg_revenue, 2),
            "co_order_avg_margin": round(co_order_avg_margin, 2),
        })

    return result


# ---------------------------------------------------------------------------
# 9. Upsell signal metrics
# ---------------------------------------------------------------------------

def get_upsell_signals(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    combos = db.execute(
        select(ComboRule.antecedent_item, ComboRule.consequent_item, ComboRule.confidence, ComboRule.lift)
        .where(ComboRule.restaurant_id == restaurant_id)
        .order_by(ComboRule.confidence.desc())
    ).all()

    if not combos:
        return []

    item_margin = df.groupby("item_name")["line_contribution_margin"].mean().to_dict()
    item_price = df.groupby("item_name")["unit_price"].mean().to_dict()

    result = []
    for c in combos:
        a, b = c.antecedent_item, c.consequent_item
        margin_uplift = item_margin.get(b, 0.0)
        price_delta = (item_price.get(b, 0.0) - item_price.get(a, 0.0))
        upsell_score = float(c.confidence) * float(c.lift) * max(margin_uplift, 0.01)

        result.append({
            "base_item": a,
            "suggested_item": b,
            "confidence": float(c.confidence),
            "lift": float(c.lift),
            "expected_margin_uplift": round(float(margin_uplift), 2),
            "price_delta": round(float(price_delta), 2),
            "upsell_score": round(float(upsell_score), 2),
        })

    result.sort(key=lambda x: x["upsell_score"], reverse=True)
    return result


# ---------------------------------------------------------------------------
# 10. Price optimization signals
# ---------------------------------------------------------------------------

def get_price_optimization(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    total_orders = df["order_id"].nunique()

    items = df.groupby("item_name").agg(
        avg_price=("unit_price", "mean"),
        avg_food_cost=("food_cost_per_unit", "mean"),
        total_qty=("quantity", "sum"),
        total_revenue=("line_revenue", "sum"),
        total_margin=("line_contribution_margin", "sum"),
        order_count=("order_id", "nunique"),
        category=("category", "first"),
    ).reset_index()

    items["cost_ratio"] = items["avg_food_cost"] / items["avg_price"].clip(lower=0.01)
    items["margin_per_unit"] = items["total_margin"] / items["total_qty"].clip(lower=1)
    items["price_to_margin_ratio"] = items["avg_price"] / items["margin_per_unit"].clip(lower=0.01)
    items["demand_elasticity_proxy"] = items["order_count"] / max(total_orders, 1)

    # Category-relative pricing
    cat_avg = df.groupby("category")["unit_price"].mean().to_dict()
    items["category_avg_price"] = items["category"].map(cat_avg)
    items["price_vs_category"] = ((items["avg_price"] - items["category_avg_price"]) / items["category_avg_price"].clip(lower=0.01)) * 100

    result = []
    for _, row in items.iterrows():
        result.append({
            "item_name": row["item_name"],
            "category": row["category"],
            "avg_price": round(float(row["avg_price"]), 2),
            "avg_food_cost": round(float(row["avg_food_cost"]), 2),
            "cost_ratio": round(float(row["cost_ratio"]), 4),
            "margin_per_unit": round(float(row["margin_per_unit"]), 2),
            "price_to_margin_ratio": round(float(row["price_to_margin_ratio"]), 2),
            "demand_elasticity_proxy": round(float(row["demand_elasticity_proxy"]), 4),
            "price_vs_category_pct": round(float(row["price_vs_category"]), 2),
            "category_avg_price": round(float(row["category_avg_price"]), 2),
        })

    return result


# ---------------------------------------------------------------------------
# 11. Menu matrix view
# ---------------------------------------------------------------------------

def get_menu_matrix_view(db: Session, restaurant_id: str) -> dict:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return {"units_median": 0.0, "margin_median": 0.0, "quadrants": []}

    item_metrics = _build_item_metrics_df(df)
    metric_lookup = _menu_metric_lookup(db, restaurant_id)

    units_median = float(item_metrics["total_qty"].median()) if not item_metrics.empty else 0.0
    margin_median = float(item_metrics["margin_pct"].median()) if not item_metrics.empty else 0.0

    quadrant_meta = {
        "STAR": ("stars", "Stars", "High margin · High volume — protect and promote"),
        "PUZZLE": ("hidden_gems", "Hidden Gems", "High margin · Low volume — under-promoted profit drivers"),
        "CASH_COW": ("watch_list", "Watch List", "Low margin · High volume — review pricing and basket mix"),
        "DOG": ("laggards", "Laggards", "Low margin · Low volume — consider recipe, price, or removal"),
    }
    quadrants: dict[str, dict] = {}
    for menu_class, (key, title, description) in quadrant_meta.items():
        quadrants[menu_class] = {
            "key": key,
            "title": title,
            "description": description,
            "count": 0,
            "items": [],
        }

    for _, row in item_metrics.iterrows():
        item_name = str(row["item_name"])
        menu_class = str(metric_lookup.get(item_name, {}).get("menu_class", "DOG"))
        quadrants.setdefault(menu_class, {
            "key": menu_class.lower(),
            "title": menu_class.title(),
            "description": "Derived from current menu engineering performance.",
            "count": 0,
            "items": [],
        })
        quadrants[menu_class]["items"].append({
            "item_name": item_name,
            "margin_pct": round(float(row["margin_pct"]), 1),
        })

    ordered = []
    for menu_class in ["STAR", "PUZZLE", "CASH_COW", "DOG"]:
        quadrant = quadrants[menu_class]
        quadrant["items"].sort(key=lambda item: item["margin_pct"], reverse=True)
        quadrant["count"] = len(quadrant["items"])
        ordered.append(quadrant)

    return {
        "units_median": round(units_median, 1),
        "margin_median": round(margin_median, 1),
        "quadrants": ordered,
    }


# ---------------------------------------------------------------------------
# 12. Combo cards
# ---------------------------------------------------------------------------

def get_combo_cards(db: Session, restaurant_id: str, limit: int = 30) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    item_metrics = _build_item_metrics_df(df)
    item_lookup = {
        str(row["item_name"]): {
            "category": str(row["category"]),
            "avg_unit_price": float(row["avg_unit_price"]),
            "margin_pct": float(row["margin_pct"]),
        }
        for _, row in item_metrics.iterrows()
    }

    rules = db.execute(
        select(ComboRule)
        .where(ComboRule.restaurant_id == restaurant_id)
        .order_by(ComboRule.lift.desc(), ComboRule.confidence.desc())
    ).scalars().all()
    if not rules:
        return []

    pair_groups: dict[tuple[str, str], list[ComboRule]] = defaultdict(list)
    for rule in rules:
        pair_groups[tuple(sorted((rule.antecedent_item, rule.consequent_item)))].append(rule)

    results = []
    for pair_key, pair_rules in pair_groups.items():
        primary_rule = max(pair_rules, key=lambda rule: (float(rule.lift), float(rule.confidence)))
        reverse_rule = next(
            (
                rule for rule in pair_rules
                if rule.antecedent_item == primary_rule.consequent_item and rule.consequent_item == primary_rule.antecedent_item
            ),
            None,
        )
        primary_item = primary_rule.antecedent_item
        secondary_item = primary_rule.consequent_item
        primary_meta = item_lookup.get(primary_item, {})
        secondary_meta = item_lookup.get(secondary_item, {})
        lift = float(primary_rule.lift)
        strength = "Strong" if lift >= 1.5 else "Moderate" if lift >= 1.2 else "Weak"
        bundle_price = (float(primary_meta.get("avg_unit_price", 0.0)) + float(secondary_meta.get("avg_unit_price", 0.0))) * 0.95
        avg_cm_pct = (
            float(primary_meta.get("margin_pct", 0.0)) + float(secondary_meta.get("margin_pct", 0.0))
        ) / 2
        results.append({
            "primary_item": primary_item,
            "secondary_item": secondary_item,
            "primary_category": str(primary_meta.get("category", "uncategorized")),
            "secondary_category": str(secondary_meta.get("category", "uncategorized")),
            "same_cuisine": str(primary_meta.get("category", "")) == str(secondary_meta.get("category", "")),
            "strength": strength,
            "lift": round(lift, 2),
            "support": round(float(primary_rule.support), 4),
            "co_orders": int(primary_rule.co_order_frequency or 0),
            "avg_cm_pct": round(avg_cm_pct, 1),
            "bundle_price": round(bundle_price, 0),
            "primary_to_secondary_confidence": round(float(primary_rule.confidence), 4),
            "secondary_to_primary_confidence": round(float(reverse_rule.confidence), 4) if reverse_rule else 0.0,
        })

    results.sort(key=lambda item: (item["lift"], item["primary_to_secondary_confidence"], item["co_orders"]), reverse=True)
    return results[:limit]


# ---------------------------------------------------------------------------
# 13. Upsell cards
# ---------------------------------------------------------------------------

def get_upsell_cards(db: Session, restaurant_id: str, limit: int = 24) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    item_metrics = _build_item_metrics_df(df)
    item_lookup = {
        str(row["item_name"]): {
            "category": str(row["category"]),
            "margin_pct": float(row["margin_pct"]),
        }
        for _, row in item_metrics.iterrows()
    }

    rules = db.execute(
        select(ComboRule)
        .where(ComboRule.restaurant_id == restaurant_id)
        .order_by(ComboRule.confidence.desc(), ComboRule.lift.desc())
    ).scalars().all()
    if not rules:
        return []

    grouped: dict[str, list[dict]] = defaultdict(list)
    for rule in rules:
        consequent_meta = item_lookup.get(rule.consequent_item, {})
        grouped[rule.antecedent_item].append({
            "item_name": rule.consequent_item,
            "category": str(consequent_meta.get("category", "uncategorized")),
            "co_order_count": int(rule.co_order_frequency or 0),
            "margin_pct": round(float(consequent_meta.get("margin_pct", 0.0)), 1),
            "confidence": round(float(rule.confidence), 4),
            "lift": round(float(rule.lift), 2),
            "score": float(rule.confidence) * float(rule.lift),
        })

    cards = []
    for base_item, suggestions in grouped.items():
        ranked = sorted(suggestions, key=lambda row: (row["score"], row["co_order_count"]), reverse=True)[:3]
        if not ranked:
            continue
        for idx, row in enumerate(ranked, start=1):
            row["rank"] = idx
            row.pop("score", None)
        cards.append({
            "base_item": base_item,
            "category": str(item_lookup.get(base_item, {}).get("category", "uncategorized")),
            "suggestions": ranked,
            "_total_score": sum(item["confidence"] * item["lift"] for item in ranked),
        })

    cards.sort(key=lambda card: card["_total_score"], reverse=True)
    for card in cards:
        card.pop("_total_score", None)
    return cards[:limit]


# ---------------------------------------------------------------------------
# 14. Pricing cards
# ---------------------------------------------------------------------------

def get_pricing_cards(db: Session, restaurant_id: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    item_metrics = _build_item_metrics_df(df)
    category_metrics = get_category_level_metrics(db, restaurant_id)
    category_margin_lookup = {row["category"]: float(row["avg_margin_pct"]) for row in category_metrics}

    cards = []
    for _, row in item_metrics.iterrows():
        category = str(row["category"])
        current_price = float(row["avg_unit_price"])
        current_cm_pct = float(row["margin_pct"])
        target_cm_pct = float(category_margin_lookup.get(category, current_cm_pct))
        cm_gap = current_cm_pct - target_cm_pct
        if cm_gap >= 0:
            continue

        avg_food_cost = float(row["avg_food_cost"])
        if target_cm_pct >= 99.0:
            continue
        suggested_price = avg_food_cost / max(1 - (target_cm_pct / 100), 0.01)
        delta_amount = suggested_price - current_price
        delta_pct = (delta_amount / max(current_price, 0.01)) * 100
        volume_total = int(row["total_qty"])
        volume_per_day = float(row["sales_velocity"])
        uplift_potential = max(delta_amount, 0.0) * volume_total

        if abs(cm_gap) > 3.5 and volume_per_day > 2.5:
            priority = "High"
        elif abs(cm_gap) > 2.0 or volume_per_day > 2.0:
            priority = "Medium"
        else:
            priority = "Low"

        cards.append({
            "item_name": str(row["item_name"]),
            "category": category,
            "priority": priority,
            "uplift_potential": round(uplift_potential, 0),
            "current_price": round(current_price, 0),
            "current_cm_pct": round(current_cm_pct, 1),
            "suggested_price": round(suggested_price, 0),
            "target_cm_pct": round(target_cm_pct, 1),
            "delta_amount": round(delta_amount, 0),
            "delta_pct": round(delta_pct, 0),
            "volume_total": volume_total,
            "volume_per_day": round(volume_per_day, 1),
            "cm_gap_pct": round(cm_gap, 1),
            "cm_gap_description": f"CM is {cm_gap:.1f}% below {category} avg ({target_cm_pct:.1f}%)",
        })

    cards.sort(key=lambda row: row["uplift_potential"], reverse=True)
    return cards


# ---------------------------------------------------------------------------
# 15. Strategy cards
# ---------------------------------------------------------------------------

def get_strategy_cards(db: Session, restaurant_id: str, strategy_type: str) -> list[dict]:
    df = _load_transactions_df(db, restaurant_id)
    if df.empty:
        return []

    item_metrics = _build_item_metrics_df(df)
    metric_lookup = _menu_metric_lookup(db, restaurant_id)
    category_metrics = get_category_level_metrics(db, restaurant_id)
    category_margin_lookup = {row["category"]: float(row["avg_margin_pct"]) for row in category_metrics}
    target_class = "PUZZLE" if strategy_type == "hidden_gems" else "CASH_COW"

    cards = []
    for _, row in item_metrics.iterrows():
        item_name = str(row["item_name"])
        menu_class = str(metric_lookup.get(item_name, {}).get("menu_class", "DOG"))
        if menu_class != target_class:
            continue
        category = str(row["category"])
        actions = generate_item_recommendations(
            item_name=item_name,
            menu_class=menu_class,
            category=category,
            margin_pct=float(row["margin_pct"]),
            units_sold=int(row["total_qty"]),
            revenue=float(row["total_revenue"]),
            profit=float(row["total_margin"]),
            avg_category_margin=float(category_margin_lookup.get(category, row["margin_pct"])),
        )
        cards.append({
            "item_name": item_name,
            "category": category,
            "margin_pct": round(float(row["margin_pct"]), 1),
            "units": int(row["total_qty"]),
            "revenue": round(float(row["total_revenue"]), 0),
            "profit": round(float(row["total_margin"]), 0),
            "recommended_actions": list(actions),
        })

    if strategy_type == "hidden_gems":
        cards.sort(key=lambda row: row["margin_pct"], reverse=True)
    else:
        cards.sort(key=lambda row: row["revenue"], reverse=True)
    return cards
