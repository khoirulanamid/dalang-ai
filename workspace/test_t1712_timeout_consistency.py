"""
T-1712 regression test: verify that AsyncClient and client.stream use the same
300-second timeout, eliminating the 120s vs 180s race condition.
"""
import ast
import pathlib


SOURCE = pathlib.Path("/root/storage/projects/dalang-ai/real_subagent_runner.py")


def _extract_timeout_literals(source_text: str) -> dict[str, list[float]]:
    """Parse the source AST and collect timeout keyword values per call site."""
    tree = ast.parse(source_text)
    results: dict[str, list[float]] = {
        "AsyncClient": [],
        "client.stream": [],
    }

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        # httpx.AsyncClient(timeout=...)
        func = node.func
        is_async_client = (
            isinstance(func, ast.Attribute)
            and func.attr == "AsyncClient"
        ) or (
            isinstance(func, ast.Name)
            and func.id == "AsyncClient"
        )

        # client.stream(...)
        is_stream = (
            isinstance(func, ast.Attribute)
            and func.attr == "stream"
        )

        target = None
        if is_async_client:
            target = "AsyncClient"
        elif is_stream:
            target = "client.stream"

        if target is None:
            continue

        for kw in node.keywords:
            if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                results[target].append(float(kw.value.value))

    return results


def test_source_file_exists() -> None:
    assert SOURCE.exists(), f"Source file not found: {SOURCE}"


def test_async_client_timeout_is_300() -> None:
    """AsyncClient must be constructed with timeout=300.0."""
    source = SOURCE.read_text(encoding="utf-8")
    timeouts = _extract_timeout_literals(source)
    assert timeouts["AsyncClient"], "No AsyncClient(timeout=...) call found"
    for val in timeouts["AsyncClient"]:
        assert val == 300.0, (
            f"AsyncClient timeout must be 300.0, got {val}. "
            "Race condition: inner stream timeout would fire first."
        )


def test_stream_timeout_is_300() -> None:
    """client.stream must use timeout=300.0 to match the outer AsyncClient."""
    source = SOURCE.read_text(encoding="utf-8")
    timeouts = _extract_timeout_literals(source)
    assert timeouts["client.stream"], "No client.stream(timeout=...) call found"
    for val in timeouts["client.stream"]:
        assert val == 300.0, (
            f"client.stream timeout must be 300.0, got {val}. "
            "Race condition: inner stream timeout would fire first."
        )


def test_timeouts_are_consistent() -> None:
    """Both call sites must share the same timeout value."""
    source = SOURCE.read_text(encoding="utf-8")
    timeouts = _extract_timeout_literals(source)
    all_values = timeouts["AsyncClient"] + timeouts["client.stream"]
    assert len(set(all_values)) == 1, (
        f"Inconsistent timeouts detected across call sites: {timeouts}. "
        "All httpx timeout values must be identical to prevent race conditions."
    )


def test_no_legacy_120_timeout() -> None:
    """Ensure the old 120.0 timeout value is fully removed."""
    source = SOURCE.read_text(encoding="utf-8")
    timeouts = _extract_timeout_literals(source)
    all_values = timeouts["AsyncClient"] + timeouts["client.stream"]
    assert 120.0 not in all_values, (
        "Legacy timeout=120.0 still present — race condition not resolved."
    )


def test_no_legacy_180_timeout() -> None:
    """Ensure the old 180.0 timeout value is fully removed."""
    source = SOURCE.read_text(encoding="utf-8")
    timeouts = _extract_timeout_literals(source)
    all_values = timeouts["AsyncClient"] + timeouts["client.stream"]
    assert 180.0 not in all_values, (
        "Legacy timeout=180.0 still present — race condition not resolved."
    )
