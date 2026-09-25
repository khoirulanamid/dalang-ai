"""
Dalang-AI — Hermes-Native Sub-Agent Runner (SSE Stream Compatible)
The local gateway (192.168.1.100:20127) streams all completions via SSE data chunks.
This runner parses the SSE stream, accumulates the full message content and tool calls,
and runs the autonomous coding loop.
"""

import asyncio
import json
import os
import re
from pathlib import Path
from typing import AsyncGenerator, Callable, Coroutine, Optional

import httpx

from agent_tools import AgentToolbox

HERMES_BASE_URL = "http://192.168.1.100:20127/v1"

def _load_standards(agent_id: str) -> str:
    """Load corresponding international standard document for the agent."""
    standards_dir = Path("/root/storage/projects/dalang-ai/standards")
    mapping = {
        "pingot": "pingot_data_standards.md",
        "zaki": "zaki_backend_standards.md",
        "lulu": "lulu_frontend_standards.md",
        "mika": "mika_docs_standards.md",
        "nova": "nova_devops_standards.md",
        "kai": "kai_security_standards.md",
        "ren": "ren_qa_standards.md",
    }
    std_file = standards_dir / mapping.get(agent_id, "")
    if std_file.exists():
        return f"\n\n## MANDATORY INTERNATIONAL ENGINEERING STANDARDS ({std_file.name}):\n" + std_file.read_text(encoding="utf-8")
    return ""

ROLE_PROMPTS = {
    "pingot": """You are Pingot, the Senior Data Architect agent in the Dalang-AI team.
Task: Write production-grade data models, schemas, and parsers following Domain-Driven Design (DDD).
Rules:
- Apply ubiquitous language, strict invariants, explicit projection models (UserInDB vs UserPublic).
- Never expose raw credentials. Enforce ISO 8601 UTC timestamps.
- Use `write_file` to write clean code, and verify with `run_command`.""",

    "zaki": """You are Zaki, the Senior Backend & Distributed Systems Engineer agent.
Task: Build production-grade REST APIs, business services, and auth mechanisms following SOLID principles and Clean Architecture.
Rules:
- Strictly adhere to SOLID principles and 12-Factor App config (Factor III: zero hardcoded secrets/hosts).
- Implement semantic HTTP status codes, structured error payloads ({detail, code, request_id}).
- Verify your code with `run_command` (pytest) before declaring completion.""",

    "lulu": """You are Lulu, the Lead Frontend Engineer & UX Specialist agent.
Task: Build high-quality UI/UX components meeting WCAG 2.1 AA accessibility and Core Web Vitals standards.
Rules:
- Ensure color contrast >= 4.5:1, full keyboard navigation, explicit form labels, and focus rings.
- Implement explicit UI states: Loading, Error, Empty, and Success states.
- Zero secrets in client-side code, and sanitize all user-rendered content (XSS prevention).""",

    "risko": """You are Risko, Technical Lead & Master Orchestrator.
Task: Define specifications and schemas, enforce quality gates, and coordinate sub-agents.""",

    "mika": """You are Mika, the Lead Technical Writer & Information Architect agent.
Task: Produce documentation adhering to the Diátaxis Framework and Google Developer Documentation Style Guide.
Rules:
- Classify content into Tutorial, How-To, Reference, or Explanation.
- Use active voice, present tense, and verified runnable code snippets.
- Document all parameters, error schemas, and constraints exhaustively.""",

    "nova": """You are Nova, the Senior Site Reliability Engineer (SRE) & DevOps Specialist agent.
Task: Containerization, CI/CD, and deployment infrastructure adhering to CIS Docker Benchmarks and Google SRE standards.
Rules:
- Non-root execution is MANDATORY (USER appuser:1001). Use multi-stage builds.
- Include robust HEALTHCHECK directives. Follow 12-factor configuration principles.
- Verify configs using `run_command` (docker compose config / linters).""",

    "kai": """You are Kai, the Principal Application Security Architect & Penetration Tester.
Task: Security auditing and threat modeling adhering to OWASP ASVS v4.0 Level 2 and NIST SP 800-63B.
Rules:
- Evaluate code against OWASP Top 10 (2021). Quantify findings using CVSS v3.1 scoring.
- Mandate anti-automation (rate limiting), constant-time comparisons, and strict token-type verification.
- Write regression security tests that prove vulnerabilities and verify mitigations.""",

    "ren": """You are Ren, the Lead QA Automation & Test Architect agent.
Task: End-to-end integration and system testing following the Test Pyramid and AAA Pattern.
Rules:
- Structure all tests using Arrange-Act-Assert. Apply Boundary Value Analysis (BVA).
- Test race conditions, token expiry boundaries, and full lifecycle journeys.
- Ensure 100% test pass rate via `run_command` before declaring task completed.""",
}


def _load_api_key() -> str:
    env_file = Path("/root/.hermes/.env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.getenv("OPENAI_API_KEY", "hermes-local")


async def stream_completion(
    client: httpx.AsyncClient,
    messages: list,
    tools: list,
    api_key: str,
    model: str = "auto",
) -> dict:
    """
    Call the local gateway and parse SSE stream response.
    Returns: {"content": str, "tool_calls": list}
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "temperature": 0.2,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    async with client.stream(
        "POST",
        f"{HERMES_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=120.0,
    ) as response:
        if response.status_code != 200:
            body = await response.aread()
            raise RuntimeError(f"Gateway HTTP {response.status_code}: {body.decode()[:200]}")

        accumulated_content = ""
        tool_calls_map = {}  # index -> {"id", "name", "arguments"}

        async for line in response.aiter_lines():
            line = line.strip()
            if not line or not line.startswith("data:"):
                continue

            raw_data = line[5:].strip()
            if raw_data == "[DONE]":
                break

            try:
                chunk = json.loads(raw_data)
                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})

                # Accumulate text content
                if "content" in delta and delta["content"]:
                    accumulated_content += delta["content"]

                # Accumulate tool calls (streamed in fragments)
                if "tool_calls" in delta and delta["tool_calls"]:
                    for tc in delta["tool_calls"]:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls_map:
                            tool_calls_map[idx] = {
                                "id": tc.get("id", f"call_{idx}"),
                                "type": "function",
                                "function": {"name": "", "arguments": ""},
                            }
                        if "id" in tc and tc["id"]:
                            tool_calls_map[idx]["id"] = tc["id"]
                        fn = tc.get("function", {})
                        if "name" in fn and fn["name"]:
                            tool_calls_map[idx]["function"]["name"] += fn["name"]
                        if "arguments" in fn and fn["arguments"]:
                            tool_calls_map[idx]["function"]["arguments"] += fn["arguments"]

            except Exception:
                continue

        parsed_tool_calls = list(tool_calls_map.values()) if tool_calls_map else None

        return {
            "content": accumulated_content,
            "tool_calls": parsed_tool_calls,
        }


class RealSubAgentRunner:
    def __init__(self, workspace: str, model: str = "auto"):
        self.workspace = workspace
        self.model = model
        self.toolbox = AgentToolbox(workspace)
        self.api_key = _load_api_key()

    def _dispatch_tool(self, name: str, args: dict) -> str:
        MAX_OUTPUT = 4000  # truncate long outputs to avoid context overflow
        try:
            if name == "read_file":
                result = self.toolbox.read_file(args.get("path", ""))
            elif name == "write_file":
                result = self.toolbox.write_file(args.get("path", ""), args.get("content", ""))
            elif name == "list_dir":
                result = self.toolbox.list_dir(args.get("path", "."))
            elif name == "run_command":
                result = self.toolbox.run_command(args.get("cmd", ""), timeout=args.get("timeout", 60))
            elif name == "search_code":
                result = self.toolbox.search_code(args.get("pattern", ""), args.get("path", "."))
            else:
                return f"ERROR: Unknown tool {name}"

            result = str(result)
            if len(result) > MAX_OUTPUT:
                half = MAX_OUTPUT // 2
                result = result[:half] + f"\n...[truncated {len(result) - MAX_OUTPUT} chars]...\n" + result[-half:]
            return result
        except Exception as e:
            return f"ERROR executing {name}: {e}"

    async def execute_task(
        self,
        agent_id: str,
        task: dict,
        subgraph: dict,
        on_event: Optional[Callable[[str, str], Coroutine]] = None,
        max_tool_iterations: int = 8,
    ) -> dict:
        async def log(action: str, detail: str):
            if on_event:
                await on_event(action, detail)

        role_prompt = ROLE_PROMPTS.get(agent_id, ROLE_PROMPTS["zaki"])
        role_prompt += _load_standards(agent_id)

        context = f"""## YOUR ASSIGNED TASK
- Task ID: {task.get('id')}
- Task Title: {task.get('title')}
- Expected Artifacts: {task.get('artifacts', [])}

## UPSTREAM DEPENDENCIES COMPLETED
{json.dumps(subgraph.get('completed_upstream', []), indent=2)}

## WORKSPACE & ENVIRONMENT
- Working directory: `{self.workspace}`
- Python: `/root/storage/projects/dalang-ai/.venv/bin/python3`
- Pytest: `/root/storage/projects/dalang-ai/.venv/bin/pytest`
- Pre-installed packages: fastapi, uvicorn, pytest, PyJWT, cryptography, bcrypt, passlib, pyyaml, httpx
- Always use the venv paths above for `run_command`
- Write code files with `write_file`, then test them with `run_command`
- Once tests pass, declare yourself done.
"""

        messages = [
            {"role": "system", "content": role_prompt},
            {"role": "user", "content": context},
        ]
        tools = self.toolbox.tool_descriptions()
        tool_call_count = 0

        await log("agent_started", f"{agent_id.upper()} starting task [{task.get('id')}]")

        async with httpx.AsyncClient(timeout=180.0) as client:
            for iteration in range(max_tool_iterations):
                try:
                    res = await stream_completion(
                        client=client,
                        messages=messages,
                        tools=tools,
                        api_key=self.api_key,
                        model=self.model,
                    )
                except Exception as e:
                    await log("agent_error", f"LLM stream error: {e}")
                    return {"success": False, "error": str(e), "iterations": iteration}

                content = res.get("content") or ""
                tool_calls = res.get("tool_calls")

                # Append assistant message to history
                assistant_msg = {"role": "assistant", "content": content}
                if tool_calls:
                    assistant_msg["tool_calls"] = tool_calls
                messages.append(assistant_msg)

                # If no tool calls, agent is finished
                if not tool_calls:
                    await log("agent_finished", f"{agent_id.upper()} completed task [{task.get('id')}] with {tool_call_count} tool calls")
                    return {
                        "success": True,
                        "final_answer": content,
                        "iterations": iteration + 1,
                        "tool_calls": tool_call_count,
                    }

                # Process each requested tool call
                for tc in tool_calls:
                    fn_name = tc["function"]["name"]
                    args_raw = tc["function"].get("arguments", "{}")
                    tool_call_count += 1

                    try:
                        args = json.loads(args_raw)
                    except Exception:
                        args = {}

                    preview = ", ".join(f"{k}={repr(v)[:40]}" for k, v in args.items())
                    await log("tool_called", f"{agent_id.upper()} ▶ {fn_name}({preview})")

                    result = self._dispatch_tool(fn_name, args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "name": fn_name,
                        "content": str(result),
                    })

            await log("agent_timeout", f"{agent_id.upper()} reached max iterations ({max_tool_iterations})")
            return {
                "success": True,
                "final_answer": "Reached iteration limit. Code artifacts written to workspace.",
                "iterations": max_tool_iterations,
                "tool_calls": tool_call_count,
            }
