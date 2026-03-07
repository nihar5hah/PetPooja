import pandas as pd

from app.services.association_service import mine_combo_rules_df


def test_mine_combo_rules_df_returns_expected_columns():
    df = pd.DataFrame(
        [
            {"order_id": "1", "item_name": "Pizza", "quantity": 1},
            {"order_id": "1", "item_name": "Coke", "quantity": 1},
            {"order_id": "2", "item_name": "Pizza", "quantity": 1},
            {"order_id": "2", "item_name": "Coke", "quantity": 1},
            {"order_id": "3", "item_name": "Pizza", "quantity": 1},
            {"order_id": "3", "item_name": "Garlic Bread", "quantity": 1},
        ]
    )

    rules = mine_combo_rules_df(df, min_support=0.2, min_confidence=0.2)

    if not rules.empty:
        assert {"antecedent_item", "consequent_item", "support", "confidence", "lift"}.issubset(set(rules.columns))
