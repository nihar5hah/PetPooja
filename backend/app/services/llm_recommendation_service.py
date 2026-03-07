from __future__ import annotations

import json
from functools import lru_cache

from app.core.config import settings


FALLBACK_ACTIONS: dict[str, list[str]] = {
    "STAR": [
        "Keep this item pinned in high-visibility menu slots and hero banners.",
        "Use it as the anchor item in premium bundles with complementary add-ons.",
        "Protect consistency on recipe, plating, and service speed to preserve repeat demand.",
    ],
    "PUZZLE": [
        "Feature it in staff upsell prompts and app banners to increase trial volume.",
        "Pair it with a proven Star item to lift discovery without discounting deeply.",
        "Move it higher in the menu flow where customers decide on premium mains or sides.",
    ],
    "CASH_COW": [
        "Test a small price increase and track conversion before making a permanent change.",
        "Tighten portioning or input costs to recover margin without hurting demand.",
        "Bundle it with high-margin sides or drinks so the overall basket gets richer.",
    ],
    "DOG": [
        "Review recipe, positioning, or naming because both demand and profit are under pressure.",
        "Limit visibility and promo spend until the item has a clearer role in the menu.",
        "Consider replacing it if nearby alternatives outperform on both sales and contribution.",
    ],
}


def _fallback(menu_class: str) -> list[str]:
    return FALLBACK_ACTIONS.get(menu_class, FALLBACK_ACTIONS["DOG"])


@lru_cache(maxsize=256)
def generate_item_recommendations(
    item_name: str,
    menu_class: str,
    category: str,
    margin_pct: float,
    units_sold: int,
    revenue: float,
    profit: float,
    avg_category_margin: float,
) -> tuple[str, str, str]:
    if not settings.gemini_api_key:
        return tuple(_fallback(menu_class)[:3])

    try:
        import google.generativeai as genai
    except Exception:  # noqa: BLE001
        return tuple(_fallback(menu_class)[:3])

    prompt = (
        "You are a restaurant revenue strategist. "
        "Return exactly 3 short action recommendations as a JSON array of strings. "
        "Each action must be specific, operational, and at most 16 words. "
        "Do not include numbering or markdown.\n\n"
        f"Item: {item_name}\n"
        f"Menu class: {menu_class}\n"
        f"Category: {category}\n"
        f"Margin %: {margin_pct:.1f}\n"
        f"Units sold: {units_sold}\n"
        f"Revenue: {revenue:.2f}\n"
        f"Profit: {profit:.2f}\n"
        f"Category average margin %: {avg_category_margin:.1f}"
    )

    try:
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.llm_model)
        response = model.generate_content(prompt)
        text = (response.text or "").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:].strip()
        payload = json.loads(text)
        if isinstance(payload, list):
            actions = [str(item).strip() for item in payload if str(item).strip()]
            if len(actions) >= 3:
                return tuple(actions[:3])
    except Exception:  # noqa: BLE001
        pass

    return tuple(_fallback(menu_class)[:3])