from __future__ import annotations

import argparse

from sqlalchemy import delete

from app.db.models import ComboRule, MenuAlias, MenuMetric, PosTransaction
from app.db.session import SessionLocal
from app.services.analytics_service import recompute_menu_metrics
from app.services.association_service import recompute_combo_rules
from app.services.dataset_context_service import load_menu_dataset, menu_dataset_path, pos_dataset_path
from app.services.ingestion_service import ingest_pos_dataframe, parse_csv


def _seed_menu_context(db, restaurant_id: str) -> int:
    menu_df = load_menu_dataset()
    if menu_df.empty:
        return 0

    alias_count = 0
    existing_aliases = {
        (row.alias_text.lower(), row.canonical_item_name)
        for row in db.query(MenuAlias).filter(MenuAlias.restaurant_id == restaurant_id).all()
    }

    for rec in menu_df.to_dict(orient="records"):
        canonical = str(rec["item_name"]).strip()
        aliases = {canonical, canonical.lower()}
        for alias in aliases:
            key = (alias.lower(), canonical)
            if key in existing_aliases:
                continue
            db.add(
                MenuAlias(
                    restaurant_id=restaurant_id,
                    alias_text=alias,
                    canonical_item_name=canonical,
                    confidence_hint=1.0,
                )
            )
            existing_aliases.add(key)
            alias_count += 1

    db.commit()
    return alias_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed DB from Set2 menu and POS datasets")
    parser.add_argument("--restaurant-id", default="default_restaurant")
    parser.add_argument("--replace", action="store_true", help="Delete existing rows for the restaurant before seeding")
    args = parser.parse_args()

    pos_path = pos_dataset_path()
    menu_path = menu_dataset_path()
    if not pos_path.exists():
        raise FileNotFoundError(f"POS dataset not found: {pos_path}")
    if not menu_path.exists():
        raise FileNotFoundError(f"Menu dataset not found: {menu_path}")

    with SessionLocal() as db:
        if args.replace:
            db.execute(delete(ComboRule).where(ComboRule.restaurant_id == args.restaurant_id))
            db.execute(delete(MenuMetric).where(MenuMetric.restaurant_id == args.restaurant_id))
            db.execute(delete(MenuAlias).where(MenuAlias.restaurant_id == args.restaurant_id))
            db.execute(delete(PosTransaction).where(PosTransaction.restaurant_id == args.restaurant_id))
            db.commit()

        with pos_path.open("rb") as f:
            df = parse_csv(f.read())
        inserted = ingest_pos_dataframe(db, args.restaurant_id, df)
        alias_count = _seed_menu_context(db, args.restaurant_id)

        metric_count, _ = recompute_menu_metrics(db, args.restaurant_id)
        combo_count, _ = recompute_combo_rules(
            db,
            args.restaurant_id,
            min_support=0.0005,
            min_confidence=0.05,
            min_lift=0.5,
            max_rules=200,
        )

        print(
            {
                "restaurant_id": args.restaurant_id,
                "pos_rows_received": len(df),
                "pos_rows_inserted": inserted,
                "menu_aliases_upserted": alias_count,
                "menu_metrics_count": metric_count,
                "combo_rules_count": combo_count,
                "menu_dataset_path": str(menu_path),
                "pos_dataset_path": str(pos_path),
            }
        )


if __name__ == "__main__":
    main()
