from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models import ComboRule, PosTransaction


def score_combo_rule(confidence: float, lift: float, support: float) -> float:
    return round((confidence * 0.5) + (lift * 0.35) + (support * 10 * 0.15), 4)


def classify_combo_strength(confidence: float, lift: float) -> str:
    if lift >= 1.6 and confidence >= 0.2:
        return "Strong"
    if lift >= 1.3 and confidence >= 0.12:
        return "Moderate"
    return "Weak"


def mine_combo_rules_df(
    transactions_df: pd.DataFrame,
    min_support: float = 0.001,
    min_confidence: float = 0.15,
    min_lift: float = 1.0,
    max_rules: int = 200,
) -> pd.DataFrame:
    if transactions_df.empty:
        return pd.DataFrame()

    basket = (
        transactions_df.groupby(["order_id", "item_name"])["quantity"]
        .sum()
        .unstack(fill_value=0)
    )
    basket = basket.gt(0)

    if basket.empty:
        return pd.DataFrame()

    itemsets = apriori(basket, min_support=min_support, use_colnames=True)
    if itemsets.empty:
        return pd.DataFrame()

    rules = association_rules(itemsets, metric="confidence", min_threshold=min_confidence)
    if rules.empty:
        return pd.DataFrame()

    rules = rules[(rules["antecedents"].str.len() == 1) & (rules["consequents"].str.len() == 1)].copy()
    if rules.empty:
        return pd.DataFrame()

    rules["antecedent_item"] = rules["antecedents"].apply(lambda s: list(s)[0])
    rules["consequent_item"] = rules["consequents"].apply(lambda s: list(s)[0])

    rules = rules[rules["antecedent_item"] != rules["consequent_item"]]
    rules = rules[rules["lift"] >= min_lift]

    # Compute conviction: (1 - support_B) / (1 - confidence)
    rules["conviction"] = rules.apply(
        lambda r: (1 - r["consequent support"]) / (1 - r["confidence"]) if r["confidence"] < 1.0 else float("inf"),
        axis=1,
    )
    # Compute leverage: support_AB - support_A * support_B
    rules["leverage"] = rules["support"] - rules["antecedent support"] * rules["consequent support"]

    # Compute co_order_frequency: count of baskets containing both items
    n_baskets = len(basket)
    rules["co_order_frequency"] = (rules["support"] * n_baskets).round().astype(int)

    return rules[["antecedent_item", "consequent_item", "support", "confidence", "lift", "conviction", "leverage", "co_order_frequency"]].sort_values(
        ["confidence", "lift"], ascending=False
    ).head(max_rules)


def recompute_combo_rules(
    db: Session,
    restaurant_id: str,
    min_support: float = 0.001,
    min_confidence: float = 0.15,
    min_lift: float = 1.0,
    max_rules: int = 200,
) -> tuple[int, datetime]:
    rows = db.execute(
        select(PosTransaction.order_id, PosTransaction.item_name, PosTransaction.quantity).where(
            PosTransaction.restaurant_id == restaurant_id
        )
    ).all()

    db.execute(delete(ComboRule).where(ComboRule.restaurant_id == restaurant_id))

    if not rows:
        db.commit()
        return 0, datetime.now(UTC)

    df = pd.DataFrame(rows, columns=["order_id", "item_name", "quantity"])
    rules_df = mine_combo_rules_df(df, min_support=min_support, min_confidence=min_confidence, min_lift=min_lift, max_rules=max_rules)
    computed_at = datetime.now(UTC)

    for rec in rules_df.to_dict(orient="records"):
        conviction_val = float(rec["conviction"]) if rec["conviction"] != float("inf") else 999999.0
        combo_score = score_combo_rule(float(rec["confidence"]), float(rec["lift"]), float(rec["support"]))
        strength = classify_combo_strength(float(rec["confidence"]), float(rec["lift"]))
        db.add(
            ComboRule(
                restaurant_id=restaurant_id,
                antecedent_item=rec["antecedent_item"],
                consequent_item=rec["consequent_item"],
                support=float(rec["support"]),
                confidence=float(rec["confidence"]),
                lift=float(rec["lift"]),
                conviction=conviction_val,
                leverage=float(rec["leverage"]),
                co_order_frequency=int(rec["co_order_frequency"]),
                combo_score=combo_score,
                strength=strength,
                computed_at=computed_at,
            )
        )

    db.commit()
    return len(rules_df), computed_at
