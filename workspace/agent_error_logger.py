"""
agent_error_logger.py
=====================
Utility for formatting enriched `agent_error` log detail strings.

Provides a single public function `format_agent_error` that produces a
structured, human-readable string containing:
  - Exception type (fully-qualified class name)
  - Condensed traceback (last N frames, default 3)
  - Model identifier that was active when the error occurred

Kept as a pure function with no side-effects so it can be unit-tested
without mocking the async log infrastructure.
"""

from __future__ import annotations

import traceback
from types import TracebackType
from typing import Optional


def format_agent_error(
    exc: BaseException,
    model: str,
    max_frames: int = 3,
) -> str:
    """Return a structured error detail string for `agent_error` log events.

    Args:
        exc: The caught exception instance.
        model: LLM model identifier active at the time of failure.
        max_frames: Maximum number of innermost traceback frames to include.
            Keeping this small prevents log bloat while preserving the
            call-site context most useful for diagnosis.

    Returns:
        A multi-line string ready to be passed as the `detail` argument to
        the `log("agent_error", ...)` call.
    """
    exc_type = type(exc).__qualname__
    exc_module = type(exc).__module__
    # Prefer module-qualified name unless it is a builtin.
    if exc_module and exc_module != "builtins":
        full_type = f"{exc_module}.{exc_type}"
    else:
        full_type = exc_type

    tb: Optional[TracebackType] = exc.__traceback__
    if tb is not None:
        # Extract all frames then keep only the last `max_frames`.
        all_lines = traceback.format_tb(tb)
        condensed_frames = all_lines[-max_frames:]
        # Strip trailing newlines from each frame line for compact output.
        frame_block = "".join(condensed_frames).rstrip()
    else:
        frame_block = "(no traceback available)"

    return (
        f"LLM stream error | type={full_type} | model={model}\n"
        f"message: {exc}\n"
        f"traceback (last {max_frames} frames):\n{frame_block}"
    )
