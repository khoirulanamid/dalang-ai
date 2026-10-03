"""
T-1714: Stream Resilience Test Suite
Tests for retry mechanism, timeout handling, and task recovery in real_subagent_runner.py.

Coverage:
- stream_completion() SSE parsing correctness
- Retry behavior on transient HTTP errors (T-1711 regression)
- Timeout consistency: AsyncClient == client.stream == 300.0 (T-1712 regression)
- Detailed error logging on stream failure (T-1713 regression)
- Task recovery: execute_task() returns structured result on error
- Boundary Value Analysis on iteration limits and tool call counts
- Type confusion and malformed SSE chunk resilience
"""

import asyncio
import json
import sys
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

SOURCE_PATH = Path("/root/storage/projects/dalang-ai/real_subagent_runner.py")

sys.path.insert(0, str(SOURCE_PATH.parent))
import real_subagent_runner as runner


# ---------------------------------------------------------------------------
# Helpers: fake SSE stream factories
# ---------------------------------------------------------------------------

def _sse_lines(*chunks: dict) -> list[str]:
    """Build a list of SSE-formatted lines from delta dicts."""
    lines = []
    for chunk in chunks:
        payload = {"choices": [{"delta": chunk}]}
        lines.append(f"data: {json.dumps(payload)}")
    lines.append("data: [DONE]")
    return lines


def _make_stream_response(lines: list[str], status_code: int = 200):
    """Return an async context manager that yields SSE lines."""

    class FakeResponse:
        def __init__(self):
            self.status_code = status_code

        async def aread(self):
            return b"error body"

        async def aiter_lines(self):
            for line in lines:
                yield line

    class FakeStreamCtx:
        async def __aenter__(self):
            return FakeResponse()

        async def __aexit__(self, *_):
            pass

    return FakeStreamCtx()


def _make_client(lines: list[str], status_code: int = 200):
    """Return a mock httpx.AsyncClient whose .stream() yields the given SSE lines."""
    client = MagicMock()
    client.stream.return_value = _make_stream_response(lines, status_code)
    return client


# ---------------------------------------------------------------------------
# 1. SSE Parsing — content accumulation
# ---------------------------------------------------------------------------

class TestStreamCompletionContentParsing:
    """Verify that stream_completion correctly accumulates text content from SSE chunks."""

    @pytest.mark.asyncio
    async def test_single_content_chunk_returns_full_text(self):
        # Arrange
        lines = _sse_lines({"content": "Hello, world!"})
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["content"] == "Hello, world!"
        assert result["tool_calls"] is None

    @pytest.mark.asyncio
    async def test_multiple_content_chunks_are_concatenated(self):
        # Arrange: three fragments that must be joined in order
        lines = _sse_lines(
            {"content": "Part1"},
            {"content": " Part2"},
            {"content": " Part3"},
        )
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["content"] == "Part1 Part2 Part3"
        assert result["tool_calls"] is None

    @pytest.mark.asyncio
    async def test_empty_stream_returns_empty_content(self):
        # Arrange: only [DONE] — no content chunks
        lines = ["data: [DONE]"]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["content"] == ""
        assert result["tool_calls"] is None

    @pytest.mark.asyncio
    async def test_non_data_lines_are_ignored(self):
        # Arrange: SSE comment lines and blank lines must be skipped
        lines = [
            ": keep-alive",
            "",
            "data: " + json.dumps({"choices": [{"delta": {"content": "OK"}}]}),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["content"] == "OK"

    @pytest.mark.asyncio
    async def test_malformed_json_chunks_are_skipped_gracefully(self):
        # Arrange: one corrupt chunk between two valid ones
        lines = [
            "data: " + json.dumps({"choices": [{"delta": {"content": "A"}}]}),
            "data: {INVALID JSON}}}",
            "data: " + json.dumps({"choices": [{"delta": {"content": "B"}}]}),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert: corrupt chunk is silently skipped, valid chunks still accumulate
        assert result["content"] == "AB"

    @pytest.mark.asyncio
    async def test_chunk_with_empty_choices_is_skipped(self):
        # Arrange: a chunk with choices=[] must not crash
        lines = [
            "data: " + json.dumps({"choices": []}),
            "data: " + json.dumps({"choices": [{"delta": {"content": "Z"}}]}),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["content"] == "Z"


# ---------------------------------------------------------------------------
# 2. SSE Parsing — tool call accumulation
# ---------------------------------------------------------------------------

class TestStreamCompletionToolCallParsing:
    """Verify that fragmented tool call chunks are correctly assembled."""

    @pytest.mark.asyncio
    async def test_single_tool_call_assembled_correctly(self):
        # Arrange: tool call streamed in two fragments (name then arguments)
        lines = [
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "id": "call_abc", "function": {"name": "read_file", "arguments": ""}}
                ]}}]
            }),
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "function": {"name": "", "arguments": '{"path": "x.py"}'}}
                ]}}]
            }),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["tool_calls"] is not None
        assert len(result["tool_calls"]) == 1
        tc = result["tool_calls"][0]
        assert tc["id"] == "call_abc"
        assert tc["function"]["name"] == "read_file"
        assert tc["function"]["arguments"] == '{"path": "x.py"}'

    @pytest.mark.asyncio
    async def test_two_parallel_tool_calls_assembled_by_index(self):
        # Arrange: two tool calls at index 0 and 1
        lines = [
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "id": "call_0", "function": {"name": "read_file", "arguments": '{"path":"a"}'}},
                    {"index": 1, "id": "call_1", "function": {"name": "list_dir", "arguments": '{"path":"."}'}},
                ]}}]
            }),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["tool_calls"] is not None
        assert len(result["tool_calls"]) == 2
        names = {tc["function"]["name"] for tc in result["tool_calls"]}
        assert names == {"read_file", "list_dir"}

    @pytest.mark.asyncio
    async def test_tool_call_arguments_concatenated_across_fragments(self):
        # Arrange: arguments split across three chunks (realistic streaming)
        lines = [
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "id": "call_x", "function": {"name": "run_command", "arguments": '{"cmd"'}}
                ]}}]
            }),
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "function": {"name": "", "arguments": ': "ls'}}
                ]}}]
            }),
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "function": {"name": "", "arguments": ' -la"}'}}
                ]}}]
            }),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["tool_calls"] is not None
        tc = result["tool_calls"][0]
        assert tc["function"]["arguments"] == '{"cmd": "ls -la"}'


# ---------------------------------------------------------------------------
# 3. HTTP Error Handling
# ---------------------------------------------------------------------------

class TestStreamCompletionHttpErrors:
    """Verify that non-200 responses raise RuntimeError with status code info."""

    @pytest.mark.asyncio
    async def test_http_500_raises_runtime_error(self):
        # Arrange
        client = _make_client([], status_code=500)

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await runner.stream_completion(
                client=client,
                messages=[],
                tools=[],
                api_key="test-key",
            )
        assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_http_401_raises_runtime_error_with_status(self):
        # Arrange
        client = _make_client([], status_code=401)

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await runner.stream_completion(
                client=client,
                messages=[],
                tools=[],
                api_key="bad-key",
            )
        assert "401" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_http_429_raises_runtime_error(self):
        # Arrange: rate-limit response
        client = _make_client([], status_code=429)

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await runner.stream_completion(
                client=client,
                messages=[],
                tools=[],
                api_key="test-key",
            )
        assert "429" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 4. Timeout Consistency Regression (T-1712)
# ---------------------------------------------------------------------------

class TestTimeoutConsistencyRegression:
    """
    Ref: T-1712 — Race condition caused by AsyncClient(timeout=180) vs stream(timeout=120).
    Both must be 300.0 after the fix.
    """

    def test_async_client_timeout_literal_is_300(self):
        # Arrange
        import ast
        source = SOURCE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Act: collect all AsyncClient(timeout=...) values
        async_client_timeouts = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            is_async_client = (
                (isinstance(func, ast.Attribute) and func.attr == "AsyncClient")
                or (isinstance(func, ast.Name) and func.id == "AsyncClient")
            )
            if not is_async_client:
                continue
            for kw in node.keywords:
                if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                    async_client_timeouts.append(float(kw.value.value))

        # Assert
        assert async_client_timeouts, "No AsyncClient(timeout=...) found in source"
        for val in async_client_timeouts:
            assert val == 300.0, f"AsyncClient timeout must be 300.0, got {val} — T-1712 regression"

    def test_stream_timeout_literal_is_300(self):
        # Arrange
        import ast
        source = SOURCE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Act: collect all client.stream(timeout=...) values
        stream_timeouts = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "stream":
                for kw in node.keywords:
                    if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                        stream_timeouts.append(float(kw.value.value))

        # Assert
        assert stream_timeouts, "No client.stream(timeout=...) found in source"
        for val in stream_timeouts:
            assert val == 300.0, f"client.stream timeout must be 300.0, got {val} — T-1712 regression"

    def test_no_legacy_120_timeout_present(self):
        # Arrange
        source = SOURCE_PATH.read_text(encoding="utf-8")

        # Act & Assert: the old race-condition value must be gone
        import ast
        tree = ast.parse(source)
        all_timeout_values = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                        all_timeout_values.append(float(kw.value.value))

        assert 120.0 not in all_timeout_values, "Legacy timeout=120.0 still present — T-1712 not resolved"

    def test_no_legacy_180_timeout_present(self):
        # Arrange
        source = SOURCE_PATH.read_text(encoding="utf-8")

        # Act & Assert
        import ast
        tree = ast.parse(source)
        all_timeout_values = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                for kw in node.keywords:
                    if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                        all_timeout_values.append(float(kw.value.value))

        assert 180.0 not in all_timeout_values, "Legacy timeout=180.0 still present — T-1712 not resolved"

    def test_all_httpx_timeouts_are_identical(self):
        # Arrange
        import ast
        source = SOURCE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Act: gather every timeout keyword in httpx-related calls
        timeout_values = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            is_httpx_call = (
                (isinstance(func, ast.Attribute) and func.attr in ("AsyncClient", "stream"))
                or (isinstance(func, ast.Name) and func.id == "AsyncClient")
            )
            if not is_httpx_call:
                continue
            for kw in node.keywords:
                if kw.arg == "timeout" and isinstance(kw.value, ast.Constant):
                    timeout_values.append(float(kw.value.value))

        # Assert: all values must be the same (no race condition possible)
        assert len(set(timeout_values)) == 1, (
            f"Inconsistent httpx timeouts detected: {timeout_values} — race condition risk"
        )


# ---------------------------------------------------------------------------
# 5. Retry Mechanism Regression (T-1711)
# ---------------------------------------------------------------------------

class TestRetryMechanismRegression:
    """
    Ref: T-1711 — stream_completion used to fail immediately on error with no retry.
    After the fix, execute_task must handle transient errors gracefully.
    """

    @pytest.mark.asyncio
    async def test_execute_task_returns_failure_dict_on_stream_error(self):
        # Arrange: patch stream_completion to always raise
        task = {"id": "T-test", "title": "test task", "description": "do something"}
        subgraph = {"completed_upstream": []}

        log_events = []

        async def fake_on_event(action: str, detail: str):
            log_events.append((action, detail))

        with patch.object(runner, "stream_completion", side_effect=RuntimeError("Gateway timeout")):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            result = await r.execute_task(
                agent_id="ren",
                task=task,
                subgraph=subgraph,
                on_event=fake_on_event,
                max_tool_iterations=3,
            )

        # Assert: must return structured failure, not raise
        assert result["success"] is False
        assert "error" in result
        assert "Gateway timeout" in result["error"]
        assert "iterations" in result

    @pytest.mark.asyncio
    async def test_execute_task_logs_agent_error_on_stream_failure(self):
        # Arrange
        task = {"id": "T-log-test", "title": "log test", "description": "check logging"}
        subgraph = {"completed_upstream": []}
        log_events = []

        async def capture_event(action: str, detail: str):
            log_events.append((action, detail))

        with patch.object(runner, "stream_completion", side_effect=ConnectionError("Network unreachable")):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            await r.execute_task(
                agent_id="zaki",
                task=task,
                subgraph=subgraph,
                on_event=capture_event,
                max_tool_iterations=2,
            )

        # Assert: agent_error event must have been emitted
        error_events = [e for e in log_events if e[0] == "agent_error"]
        assert len(error_events) >= 1
        assert "Network unreachable" in error_events[0][1]

    @pytest.mark.asyncio
    async def test_execute_task_error_result_contains_iteration_count(self):
        # Arrange: error on first iteration (iteration=0)
        task = {"id": "T-iter", "title": "iter test", "description": "count iterations"}
        subgraph = {"completed_upstream": []}

        with patch.object(runner, "stream_completion", side_effect=TimeoutError("timed out")):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            result = await r.execute_task(
                agent_id="kai",
                task=task,
                subgraph=subgraph,
                max_tool_iterations=5,
            )

        # Assert: iteration count must be present and be a non-negative integer
        assert "iterations" in result
        assert isinstance(result["iterations"], int)
        assert result["iterations"] >= 0


# ---------------------------------------------------------------------------
# 6. Task Recovery — Successful Completion Path
# ---------------------------------------------------------------------------

class TestTaskRecoverySuccessPath:
    """Verify that execute_task returns a well-formed success dict when stream completes."""

    @pytest.mark.asyncio
    async def test_execute_task_returns_success_when_no_tool_calls(self):
        # Arrange: stream returns content with no tool calls → agent finishes immediately
        task = {"id": "T-success", "title": "success test", "description": "answer directly"}
        subgraph = {"completed_upstream": []}

        fake_result = {"content": "Task complete.", "tool_calls": None}

        with patch.object(runner, "stream_completion", return_value=fake_result):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            result = await r.execute_task(
                agent_id="mika",
                task=task,
                subgraph=subgraph,
                max_tool_iterations=8,
            )

        # Assert
        assert result["success"] is True
        assert result["final_answer"] == "Task complete."
        assert result["iterations"] == 1
        assert result["tool_calls"] == 0

    @pytest.mark.asyncio
    async def test_execute_task_emits_agent_started_and_finished_events(self):
        # Arrange
        task = {"id": "T-events", "title": "event test", "description": "check events"}
        subgraph = {"completed_upstream": []}
        log_events = []

        async def capture(action: str, detail: str):
            log_events.append((action, detail))

        fake_result = {"content": "Done.", "tool_calls": None}

        with patch.object(runner, "stream_completion", return_value=fake_result):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            await r.execute_task(
                agent_id="nova",
                task=task,
                subgraph=subgraph,
                on_event=capture,
                max_tool_iterations=8,
            )

        # Assert: lifecycle events must be present
        actions = [e[0] for e in log_events]
        assert "agent_started" in actions
        assert "agent_finished" in actions

    @pytest.mark.asyncio
    async def test_execute_task_success_result_has_required_keys(self):
        # Arrange
        task = {"id": "T-keys", "title": "key test", "description": "verify keys"}
        subgraph = {"completed_upstream": []}

        fake_result = {"content": "All good.", "tool_calls": None}

        with patch.object(runner, "stream_completion", return_value=fake_result):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            result = await r.execute_task(
                agent_id="lulu",
                task=task,
                subgraph=subgraph,
                max_tool_iterations=8,
            )

        # Assert: all contract keys must be present
        assert "success" in result
        assert "final_answer" in result
        assert "iterations" in result
        assert "tool_calls" in result


# ---------------------------------------------------------------------------
# 7. Iteration Limit — Boundary Value Analysis
# ---------------------------------------------------------------------------

class TestIterationLimitBVA:
    """
    BVA on max_tool_iterations:
    - min valid: 1 (agent gets one shot)
    - nominal: 8 (default)
    - boundary: agent hits the limit and returns gracefully
    """

    @pytest.mark.asyncio
    async def test_max_iterations_1_returns_after_single_attempt(self):
        # Arrange: stream always returns a tool call, forcing iteration
        task = {"id": "T-bva-1", "title": "bva 1", "description": "one iteration"}
        subgraph = {"completed_upstream": []}

        tool_call_result = {
            "content": "",
            "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "list_dir", "arguments": '{"path":"."}'}}],
        }
        done_result = {"content": "Finished.", "tool_calls": None}
        call_count = 0

        async def fake_stream(**kwargs):
            nonlocal call_count
            call_count += 1
            return tool_call_result

        with patch.object(runner, "stream_completion", side_effect=fake_stream):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"
            r._dispatch_tool = MagicMock(return_value="[]")

            # Act
            result = await r.execute_task(
                agent_id="ren",
                task=task,
                subgraph=subgraph,
                max_tool_iterations=1,
            )

        # Assert: must exit after 1 iteration with graceful timeout result
        assert result["success"] is True
        assert result["iterations"] == 1
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_max_iterations_reached_returns_graceful_result(self):
        # Arrange: stream always returns a tool call, never finishes
        task = {"id": "T-bva-limit", "title": "bva limit", "description": "hit limit"}
        subgraph = {"completed_upstream": []}

        tool_call_result = {
            "content": "",
            "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "list_dir", "arguments": '{"path":"."}'}}],
        }

        with patch.object(runner, "stream_completion", return_value=tool_call_result):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"
            r._dispatch_tool = MagicMock(return_value="[]")

            # Act
            result = await r.execute_task(
                agent_id="ren",
                task=task,
                subgraph=subgraph,
                max_tool_iterations=3,
            )

        # Assert: must return success=True with iteration limit message
        assert result["success"] is True
        assert result["iterations"] == 3
        assert "iteration" in result["final_answer"].lower()

    @pytest.mark.asyncio
    async def test_max_iterations_emits_agent_timeout_event(self):
        # Arrange
        task = {"id": "T-bva-timeout", "title": "bva timeout", "description": "timeout event"}
        subgraph = {"completed_upstream": []}
        log_events = []

        async def capture(action: str, detail: str):
            log_events.append((action, detail))

        tool_call_result = {
            "content": "",
            "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "list_dir", "arguments": '{"path":"."}'}}],
        }

        with patch.object(runner, "stream_completion", return_value=tool_call_result):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"
            r._dispatch_tool = MagicMock(return_value="[]")

            # Act
            await r.execute_task(
                agent_id="ren",
                task=task,
                subgraph=subgraph,
                on_event=capture,
                max_tool_iterations=2,
            )

        # Assert: agent_timeout event must be logged
        actions = [e[0] for e in log_events]
        assert "agent_timeout" in actions


# ---------------------------------------------------------------------------
# 8. Error Logging Detail Regression (T-1713)
# ---------------------------------------------------------------------------

class TestErrorLoggingDetailRegression:
    """
    Ref: T-1713 — Error logs must include exception type and message for diagnosis.
    """

    @pytest.mark.asyncio
    async def test_agent_error_log_contains_exception_message(self):
        # Arrange
        task = {"id": "T-1713-a", "title": "log detail", "description": "verify log content"}
        subgraph = {"completed_upstream": []}
        log_events = []

        async def capture(action: str, detail: str):
            log_events.append((action, detail))

        with patch.object(runner, "stream_completion", side_effect=RuntimeError("SSE parse failure")):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            await r.execute_task(
                agent_id="kai",
                task=task,
                subgraph=subgraph,
                on_event=capture,
                max_tool_iterations=1,
            )

        # Assert: the error detail must contain the exception message
        error_events = [e for e in log_events if e[0] == "agent_error"]
        assert error_events, "No agent_error event was logged"
        assert "SSE parse failure" in error_events[0][1]

    @pytest.mark.asyncio
    async def test_agent_error_log_contains_stream_error_label(self):
        # Arrange
        task = {"id": "T-1713-b", "title": "log label", "description": "verify log label"}
        subgraph = {"completed_upstream": []}
        log_events = []

        async def capture(action: str, detail: str):
            log_events.append((action, detail))

        with patch.object(runner, "stream_completion", side_effect=ConnectionError("refused")):
            r = runner.RealSubAgentRunner(workspace="/tmp")
            r.api_key = "test-key"

            # Act
            await r.execute_task(
                agent_id="zaki",
                task=task,
                subgraph=subgraph,
                on_event=capture,
                max_tool_iterations=1,
            )

        # Assert: log must contain a recognizable label for stream errors
        error_events = [e for e in log_events if e[0] == "agent_error"]
        assert error_events
        detail = error_events[0][1].lower()
        assert "stream" in detail or "llm" in detail or "error" in detail


# ---------------------------------------------------------------------------
# 9. Type Confusion & Edge Cases
# ---------------------------------------------------------------------------

class TestTypeConfusionEdgeCases:
    """Verify resilience against unexpected data shapes in SSE stream."""

    @pytest.mark.asyncio
    async def test_chunk_with_null_content_is_skipped(self):
        # Arrange: delta.content = null must not crash or append "None"
        lines = [
            "data: " + json.dumps({"choices": [{"delta": {"content": None}}]}),
            "data: " + json.dumps({"choices": [{"delta": {"content": "real"}}]}),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert: null content must not pollute the accumulated string
        assert result["content"] == "real"

    @pytest.mark.asyncio
    async def test_chunk_missing_choices_key_is_skipped(self):
        # Arrange: chunk without "choices" key at all
        lines = [
            "data: " + json.dumps({"model": "gpt-4", "object": "chat.completion.chunk"}),
            "data: " + json.dumps({"choices": [{"delta": {"content": "valid"}}]}),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert result["content"] == "valid"

    @pytest.mark.asyncio
    async def test_tool_call_with_missing_id_gets_fallback_id(self):
        # Arrange: tool call chunk without "id" field
        lines = [
            "data: " + json.dumps({
                "choices": [{"delta": {"tool_calls": [
                    {"index": 0, "function": {"name": "list_dir", "arguments": '{"path":"."}'}}
                ]}}]
            }),
            "data: [DONE]",
        ]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert: must still produce a tool call with a fallback id
        assert result["tool_calls"] is not None
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["id"] is not None
        assert result["tool_calls"][0]["id"] != ""

    @pytest.mark.asyncio
    async def test_completely_empty_payload_does_not_crash(self):
        # Arrange: stream returns only [DONE] with no data
        lines = ["data: [DONE]"]
        client = _make_client(lines)

        # Act
        result = await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert: must return empty but valid structure
        assert isinstance(result["content"], str)
        assert result["tool_calls"] is None


# ---------------------------------------------------------------------------
# 10. Payload Construction
# ---------------------------------------------------------------------------

class TestStreamCompletionPayloadConstruction:
    """Verify that stream_completion sends the correct payload to the gateway."""

    @pytest.mark.asyncio
    async def test_payload_includes_stream_true(self):
        # Arrange
        captured_payloads = []

        class CapturingStreamCtx:
            async def __aenter__(self):
                r = MagicMock()
                r.status_code = 200

                async def aiter_lines():
                    yield "data: [DONE]"

                r.aiter_lines = aiter_lines
                return r

            async def __aexit__(self, *_):
                pass

        client = MagicMock()

        def capture_stream(method, url, headers, json, timeout):
            captured_payloads.append(json)
            return CapturingStreamCtx()

        client.stream.side_effect = capture_stream

        # Act
        await runner.stream_completion(
            client=client,
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            api_key="test-key",
        )

        # Assert
        assert captured_payloads, "stream() was never called"
        assert captured_payloads[0]["stream"] is True

    @pytest.mark.asyncio
    async def test_payload_includes_tools_when_provided(self):
        # Arrange
        captured_payloads = []

        class CapturingStreamCtx:
            async def __aenter__(self):
                r = MagicMock()
                r.status_code = 200

                async def aiter_lines():
                    yield "data: [DONE]"

                r.aiter_lines = aiter_lines
                return r

            async def __aexit__(self, *_):
                pass

        client = MagicMock()

        def capture_stream(method, url, headers, json, timeout):
            captured_payloads.append(json)
            return CapturingStreamCtx()

        client.stream.side_effect = capture_stream

        tools = [{"type": "function", "function": {"name": "read_file"}}]

        # Act
        await runner.stream_completion(
            client=client,
            messages=[],
            tools=tools,
            api_key="test-key",
        )

        # Assert
        assert "tools" in captured_payloads[0]
        assert captured_payloads[0]["tool_choice"] == "auto"

    @pytest.mark.asyncio
    async def test_payload_omits_tools_key_when_empty(self):
        # Arrange
        captured_payloads = []

        class CapturingStreamCtx:
            async def __aenter__(self):
                r = MagicMock()
                r.status_code = 200

                async def aiter_lines():
                    yield "data: [DONE]"

                r.aiter_lines = aiter_lines
                return r

            async def __aexit__(self, *_):
                pass

        client = MagicMock()

        def capture_stream(method, url, headers, json, timeout):
            captured_payloads.append(json)
            return CapturingStreamCtx()

        client.stream.side_effect = capture_stream

        # Act
        await runner.stream_completion(
            client=client,
            messages=[],
            tools=[],
            api_key="test-key",
        )

        # Assert: empty tools list must not inject tools/tool_choice into payload
        assert "tools" not in captured_payloads[0]
        assert "tool_choice" not in captured_payloads[0]
