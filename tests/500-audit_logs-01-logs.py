from datetime import datetime, timedelta, timezone

from .cache import britive


def test_fields():
    fields = britive.audit_logs.logs.fields()
    assert isinstance(fields, dict)
    assert len(fields) == 18


def test_operators():
    operators = britive.audit_logs.logs.operators()
    assert isinstance(operators, dict)
    assert len(operators) == 4


def test_query_json():
    events = britive.audit_logs.logs.query(
        from_time=(datetime.now(timezone.utc) - timedelta(1)), to_time=datetime.now(timezone.utc)
    )
    assert isinstance(events, list)
    assert isinstance(events[0], dict)
    assert len(events) % 100 != 0  # v2.8.1 - adding check due to pagination bug not including the last page


def test_query_csv():
    csv = britive.audit_logs.logs.query(
        from_time=datetime.now(timezone.utc) - timedelta(1), to_time=datetime.now(timezone.utc), csv=True
    )
    assert '"timestamp","actor.display_name"' in csv
