from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections import defaultdict
from difflib import get_close_matches
from datetime import UTC, datetime

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import FailedOrderQueue, MenuAlias, MenuMetric, PosTransaction, VoiceCallLog
from app.services.dataset_context_service import load_menu_dataset
from app.services.order_service import enqueue_failed_order, persist_order
from app.services.upsell_service import get_upsell_suggestions


NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def verify_retell_signature(raw_body: bytes, signature: str | None) -> bool:
    if not settings.retell_webhook_secret:
        return True
    if not signature:
        return False
    expected = hmac.new(settings.retell_webhook_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _menu_candidates(db: Session, restaurant_id: str) -> tuple[list[str], dict[str, tuple[str, float]]]:
    metric_items = db.execute(
        select(MenuMetric.item_name).where(MenuMetric.restaurant_id == restaurant_id)
    ).scalars().all()

    txn_items = db.execute(
        select(distinct(PosTransaction.item_name)).where(PosTransaction.restaurant_id == restaurant_id)
    ).scalars().all()

    menu_df = load_menu_dataset()
    menu_items = menu_df["item_name"].dropna().astype(str).tolist() if not menu_df.empty else []

    candidates = sorted(set(metric_items) | set(txn_items) | set(menu_items))

    alias_rows = db.execute(
        select(MenuAlias.alias_text, MenuAlias.canonical_item_name, MenuAlias.confidence_hint)
        .where(MenuAlias.restaurant_id == restaurant_id)
    ).all()
    alias_map = {_normalize(a): (c, float(h)) for a, c, h in alias_rows}

    return candidates, alias_map


def resolve_item_name(raw_item: str, candidates: list[str], alias_map: dict[str, tuple[str, float]]) -> tuple[str | None, float]:
    norm = _normalize(raw_item)
    if not norm:
        return None, 0.0

    if norm in alias_map:
        canonical, confidence_hint = alias_map[norm]
        return canonical, confidence_hint

    norm_to_item = {_normalize(item): item for item in candidates}
    if norm in norm_to_item:
        return norm_to_item[norm], 1.0

    close = get_close_matches(norm, list(norm_to_item.keys()), n=1, cutoff=0.72)
    if close:
        return norm_to_item[close[0]], 0.82

    return None, 0.0


def _extract_items_from_transcript(transcript: str, candidates: list[str]) -> list[dict]:
    text = _normalize(transcript)
    if not text:
        return []

    found: dict[str, int] = defaultdict(int)

    for match in re.finditer(r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+([a-z][a-z\s]{1,40})", text):
        qty_token, phrase = match.groups()
        qty = int(qty_token) if qty_token.isdigit() else NUMBER_WORDS.get(qty_token, 1)
        phrase = phrase.strip()

        best = get_close_matches(phrase, [_normalize(c) for c in candidates], n=1, cutoff=0.72)
        if best:
            for candidate in candidates:
                if _normalize(candidate) == best[0]:
                    found[candidate] += qty
                    break

    for candidate in candidates:
        norm_candidate = _normalize(candidate)
        if re.search(rf"\b{re.escape(norm_candidate)}\b", text):
            if found[candidate] == 0:
                found[candidate] = 1

    return [{"item_name": name, "quantity": qty} for name, qty in found.items()]


def _log_call(db: Session, restaurant_id: str, call_id: str, transcript: str, payload: dict, outcome: str) -> None:
    db.add(
        VoiceCallLog(
            restaurant_id=restaurant_id,
            call_id=call_id,
            transcript=transcript,
            parsed_payload=json.dumps(payload),
            outcome=outcome,
            created_at=datetime.now(UTC),
        )
    )
    db.commit()


def process_voice_order(db: Session, payload: dict) -> dict:
    restaurant_id = payload.get("restaurant_id", "default_restaurant")
    call_id = payload["call_id"]
    customer_phone = payload.get("customer_phone", "")
    transcript = payload.get("transcript", "")
    confirm_order = bool(payload.get("confirm_order", False))

    candidates, alias_map = _menu_candidates(db, restaurant_id)

    raw_items = payload.get("ordered_items")
    if raw_items:
        extracted = [{"item_name": i["item_name"], "quantity": int(i.get("quantity", 1))} for i in raw_items]
    else:
        extracted = _extract_items_from_transcript(transcript, candidates)

    resolved_items = []
    unresolved_items = []
    needs_confirmation = False

    for item in extracted:
        matched, confidence = resolve_item_name(item["item_name"], candidates, alias_map)
        if not matched:
            unresolved_items.append(item["item_name"])
            continue
        if confidence < 0.9:
            needs_confirmation = True
        resolved_items.append(
            {
                "item_name": matched,
                "quantity": int(item["quantity"]),
                "confidence": float(confidence),
            }
        )

    upsell = []
    seen = set()
    for item in resolved_items:
        for suggestion in get_upsell_suggestions(db, restaurant_id, item["item_name"], limit=2):
            key = (item["item_name"], suggestion["suggested_item"])
            if key in seen:
                continue
            seen.add(key)
            upsell.append(suggestion)

    if not resolved_items:
        _log_call(db, restaurant_id, call_id, transcript, payload, "no_items_detected")
        return {
            "status": "needs_input",
            "call_id": call_id,
            "needs_confirmation": True,
            "resolved_items": [],
            "unresolved_items": unresolved_items,
            "upsell_suggestions": [],
            "order_id": None,
            "message": "I could not identify menu items. Please repeat your order.",
        }

    if unresolved_items or not confirm_order or needs_confirmation:
        _log_call(db, restaurant_id, call_id, transcript, payload, "pending_confirmation")
        return {
            "status": "pending_confirmation",
            "call_id": call_id,
            "needs_confirmation": True,
            "resolved_items": resolved_items,
            "unresolved_items": unresolved_items,
            "upsell_suggestions": upsell,
            "order_id": None,
            "message": "Please confirm the detected items before finalizing your order.",
        }

    order_id, total, error = persist_order(
        db=db,
        restaurant_id=restaurant_id,
        call_id=call_id,
        customer_phone=customer_phone,
        resolved_items=resolved_items,
        source="voice",
        max_retries=3,
    )

    if error or order_id is None:
        queue_id = enqueue_failed_order(
            db=db,
            restaurant_id=restaurant_id,
            call_id=call_id,
            payload={
                "restaurant_id": restaurant_id,
                "call_id": call_id,
                "customer_phone": customer_phone,
                "resolved_items": resolved_items,
                "source": "voice",
            },
            failure_reason=error or "unknown error",
            retry_count=3,
        )
        _log_call(db, restaurant_id, call_id, transcript, payload, "queued_for_retry")
        return {
            "status": "queued",
            "call_id": call_id,
            "needs_confirmation": False,
            "resolved_items": resolved_items,
            "unresolved_items": [],
            "upsell_suggestions": upsell,
            "order_id": None,
            "message": f"Order persistence failed and was queued for retry (queue_id={queue_id}).",
        }

    _log_call(db, restaurant_id, call_id, transcript, payload, "order_confirmed")
    return {
        "status": "confirmed",
        "call_id": call_id,
        "needs_confirmation": False,
        "resolved_items": resolved_items,
        "unresolved_items": [],
        "upsell_suggestions": upsell,
        "order_id": order_id,
        "message": f"Order confirmed with total amount {total:.2f}.",
    }


def retry_failed_order(db: Session, queue_id: int) -> tuple[str, int | None, str]:
    queued = db.execute(select(FailedOrderQueue).where(FailedOrderQueue.id == queue_id)).scalar_one_or_none()
    if not queued:
        return "not_found", None, "Queue entry not found"

    if queued.status == "resolved":
        return "resolved", None, "Queue entry already resolved"

    payload = json.loads(queued.payload)

    order_id, _, error = persist_order(
        db=db,
        restaurant_id=payload["restaurant_id"],
        call_id=payload["call_id"],
        customer_phone=payload.get("customer_phone", ""),
        resolved_items=payload["resolved_items"],
        source=payload.get("source", "voice"),
        max_retries=2,
    )

    if error or order_id is None:
        queued.retry_count += 1
        queued.failure_reason = error or queued.failure_reason
        db.commit()
        return "pending", None, "Retry attempted but failed"

    queued.status = "resolved"
    queued.resolved_at = datetime.now(UTC)
    db.commit()
    return "resolved", order_id, "Failed order has been recovered"
