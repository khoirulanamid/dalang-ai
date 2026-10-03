"""
test_agent_error_logger.py
==========================
Regression tests for format_agent_error (T-1713).

Covers:
  - Presence of exception type (both builtin and custom)
  - Presence of model name
  - Inclusion of condensed traceback (last N frames)
  - Handling when __traceback__ is None
  - Formatting with real exception raised via try/except
"""

import sys
from agent_error_logger import format_agent_error


def _raise_nested():
    def _inner():
        raise ConnectionResetError("Remote server closed the stream abruptly")
    _inner()


def test_agent_error_includes_exception_type():
    try:
        _raise_nested()
    except Exception as exc:
        result = format_agent_error(exc, model="qwen2.5-coder:32b")
        assert "ConnectionResetError" in result
        assert "type=" in result


def test_agent_error_includes_model_name():
    try:
        raise ValueError("Invalid temperature argument")
    except Exception as exc:
        result = format_agent_error(exc, model="deepseek-r1:14b")
        assert "model=deepseek-r1:14b" in result


def test_agent_error_condenses_traceback_to_max_frames():
    try:
        _raise_nested()
    except Exception as exc:
        # Default is 3 frames; let's request 1 frame
        result_1 = format_agent_error(exc, model="auto", max_frames=1)
        result_3 = format_agent_error(exc, model="auto", max_frames=3)

        assert "traceback (last 1 frames):" in result_1
        assert "traceback (last 3 frames):" in result_3
        # 1-frame result must be shorter than 3-frame result
        assert len(result_1) < len(result_3)


def test_agent_error_without_traceback():
    exc = RuntimeError("synthetic exception with no tb")
    # exc.__traceback__ is None here because it was never raised
    result = format_agent_error(exc, model="hermes-local")
    assert "RuntimeError" in result
    assert "hermes-local" in result
    assert "(no traceback available)" in result


def test_agent_error_custom_exception_module_qualification():
    class CustomLLMTimeout(Exception):
        pass

    try:
        raise CustomLLMTimeout("SSE read timed out after 300s")
    except Exception as exc:
        result = format_agent_error(exc, model="claude-3-5-sonnet")
        assert "CustomLLMTimeout" in result
        assert "model=claude-3-5-sonnet" in result
        assert "SSE read timed out after 300s" in result
