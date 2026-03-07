from app.services.dashboard_service import get_dashboard_summary


def test_dashboard_summary_empty_db():
    class _DummyResult:
        def __init__(self, scalar=None, rows=None):
            self._scalar = scalar
            self._rows = rows or []

        def scalar_one(self):
            return self._scalar

        def all(self):
            return self._rows

    class _DummyDB:
        def __init__(self):
            self.calls = 0

        def execute(self, _query):
            self.calls += 1
            if self.calls == 1:
                return _DummyResult(scalar=0)
            if self.calls == 2:
                return _DummyResult(scalar=0.0)
            return _DummyResult(rows=[])

    out = get_dashboard_summary(_DummyDB(), "default_restaurant")
    assert out["order_count"] == 0
    assert out["total_revenue"] == 0.0
    assert out["avg_order_value"] == 0.0
    assert out["top_selling_items"] == []
