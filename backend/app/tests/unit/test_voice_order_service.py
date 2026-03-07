from app.services.voice_order_service import resolve_item_name


def test_resolve_item_name_with_alias():
    candidates = ["Pizza", "Garlic Bread", "Paneer Pizza"]
    aliases = {"paneer pizaa": ("Paneer Pizza", 0.95)}

    matched, confidence = resolve_item_name("paneer pizaa", candidates, aliases)

    assert matched == "Paneer Pizza"
    assert confidence >= 0.9


def test_resolve_item_name_with_fuzzy_match():
    candidates = ["Pizza", "Garlic Bread", "Paneer Pizza"]
    aliases = {}

    matched, confidence = resolve_item_name("garlic bred", candidates, aliases)

    assert matched == "Garlic Bread"
    assert confidence > 0.7
