import pandas as pd

from app.services.analytics_service import build_menu_metrics_df, classify_menu_item, get_underperformers


def test_classify_menu_item():
    assert classify_menu_item(10, 0.8, 8, 0.5) == "STAR"
    assert classify_menu_item(10, 0.2, 8, 0.5) == "PUZZLE"
    assert classify_menu_item(4, 0.8, 8, 0.5) == "CASH_COW"
    assert classify_menu_item(4, 0.2, 8, 0.5) == "DOG"


def test_build_menu_metrics_df_and_underperformers():
    df = pd.DataFrame(
        [
            {"item_name": "Pizza", "quantity": 10, "line_revenue": 1000, "line_contribution_margin": 40, "transaction_date": pd.Timestamp("2026-03-01")},
            {"item_name": "Pizza", "quantity": 5, "line_revenue": 500, "line_contribution_margin": 38, "transaction_date": pd.Timestamp("2026-03-02")},
            {"item_name": "Garlic Bread", "quantity": 2, "line_revenue": 120, "line_contribution_margin": 55, "transaction_date": pd.Timestamp("2026-03-01")},
        ]
    )

    out = build_menu_metrics_df(df)
    assert set(out["item_name"].tolist()) == {"Pizza", "Garlic Bread"}

    underperformers = get_underperformers(out)
    assert "Garlic Bread" in underperformers["item_name"].values
