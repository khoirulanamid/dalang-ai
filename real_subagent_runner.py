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

HERMES_BASE_URL = os.getenv("HERMES_BASE_URL", "http://127.0.0.1:20127/v1")

from field_journal import query_journal_learnings
from llm_guard import LLMGuardrail

def _load_standards(agent_id: str, task_context: str = "") -> str:
    """Load corresponding international standard document and dynamic field journal learnings."""
    standards_dir = Path("/root/storage/projects/dalang-ai/standards")
    mapping = {
        "pingot": "pingot_data_standards.md",
        "zaki": "zaki_backend_standards.md",
        "lulu": "lulu_frontend_standards.md",
        "mika": "mika_docs_standards.md",
        "nova": "nova_devops_standards.md",
        "kai": "kai_security_standards.md",
        "ren": "ren_qa_standards.md",
        "wiku": "wiku_3d_standards.md",
        "kresna": "kresna_motion_standards.md",
        "bagong": "bagong_vault_standards.md",
        "gathot": "gathot_social_standards.md",
    }
    parts = []
    fname = mapping.get(agent_id, "")
    if fname:
        std_file = standards_dir / fname
        if std_file.is_file():
            parts.append(f"\n\n## MANDATORY INTERNATIONAL ENGINEERING STANDARDS ({std_file.name}):\n" + std_file.read_text(encoding="utf-8"))

    # Dynamic Field Journal Pitfall Warning Injection
    journal_context = f"{agent_id} {task_context}"
    learnings = query_journal_learnings(journal_context, agent_id=agent_id, limit=2)
    if learnings:
        parts.append(learnings)

    return "\n\n".join(parts)

ROLE_PROMPTS = {
    "pingot": """You are Pingot, the Senior Data Architect agent in the Dalang-AI team.
Task: Write production-grade data models, schemas, and parsers following Domain-Driven Design (DDD).
Rules:
- Apply ubiquitous language, strict invariants, explicit projection models (UserInDB vs UserPublic).
- Never expose raw credentials. Enforce ISO 8601 UTC timestamps.
- Use `write_file` to write clean code, and verify with `run_command`.""",

    "zaki": """You are Zaki, the Senior Backend & Distributed Systems Engineer agent.
Task: Build production-grade REST APIs, business services, auth mechanisms, and defensive API hardening.
Rules:
- Strictly adhere to SOLID principles and 12-Factor App config (Factor III: zero hardcoded secrets/hosts).
- Implement defensive API hardening: strict Pydantic schemas (extra="forbid"), HMAC constant-time validation, rate limiting, and replay attack protection.
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

    "kai": """You are Kai, the Principal Application Security Architect & Reverse Engineering Specialist.
Task: Security auditing, threat modeling, reverse engineering analysis, and penetration testing adhering to OWASP ASVS v4.0 Level 2, NIST SP 800-63B, and structured routing methodology.
Rules:
- Apply evidence-based auditing (Scope → Evidence → Finding with CVSS/CWE → Actionable Remediation).
- Audit mobile APKs, frontend JS parameter crypto, ELF/binary memory safety, and API/token gates.
- Mandate anti-automation (rate limiting), constant-time comparisons, strict algorithm pinning, and anti-tamper defenses.
- Write reproducible regression security tests that prove vulnerabilities and verify mitigations with zero hallucination.""",

    "ren": """You are Ren, the Lead QA Automation & Test Architect agent.
Task: End-to-end integration, system testing, and security regression verification following the Test Pyramid and AAA Pattern.
Rules:
- Structure all tests using Arrange-Act-Assert. Apply Boundary Value Analysis (BVA).
- Build security regression tests for authentication bypass, replay attacks, parameter tampering, and algorithm confusion.
- Ensure 100% test pass rate via `run_command` before declaring task completed.""",

    "kresna": """You are Kresna, the Lead Narrative & Motion Designer agent in the Dalang-AI team.
Task: Transform any scenario, case study, or concept into a self-contained animated explainer film (HTML Canvas 2D).
Rules:
- Always begin by building a FACTS LEDGER from the source — only verified facts may appear on screen.
- Classify the story type: before-after, how-it-works, problem-fix, comparison, cautionary, lessons-learned.
- Write a beat-by-beat outline using And-But-Therefore or Pixar story spine structure before generating any code.
- Generate a single self-contained .html file using Canvas 2D (zero external dependencies, zero API keys required).
- Include procedural background music & sound effects using Web Audio API.
- Each scene/beat must have: a robot character with mood/pose, a camera that frames the focal point, speech bubble, and subtitle.
- Film must end with a facts recap slide.
- Use `write_file` to save the .html output, and verify it renders by checking for syntax errors.
- For MP4 export: use Playwright headless + ffmpeg frame capture pipeline.
- AFTER producing any file, ALWAYS call the vault deposit API to register the artifact.""",

    "bagong": """You are Bagong, the Asset & Release Custodian agent in the Dalang-AI team.
Task: Receive, store, index, and distribute all output artifacts produced by the team.
Rules:
- Accept deposits from any Wayang (HTML, video, code, documents, microstock, reports).
- Always store to persistent vault: /root/storage/projects/dalang-ai/vault/<category>/.
- Always mirror to frontend/public/vault/<category>/ for browser access.
- Maintain vault_index.json as the single source of truth for all artifacts.
- When Bos Muda requests a file: search vault index, return the direct URL and file path.
- Respond to requests: 'ambil', 'kirim', 'tampilkan', 'daftar output', 'hasil terbaru'.
- Never delete any artifact without explicit authorization from Bos Muda.""",

    "gathot": """You are Gathot, the Social Media & Growth Specialist agent in the Dalang-AI team.
Task: Research trending keywords, craft viral copywriting/hooks, optimize social SEO, and publish content to social platforms (Threads, Facebook, Instagram).
Rules:
- Never fabricate personal usage claims ('aku/saya sudah pakai'). Use objective specs, aggregate consensus, and observational humor.
- Focus on relatable humor, everyday dilemmas, and curiosity gap hooks.
- Follow thread-splitting format: Post 1 for hook/relatable pain point, Post 2 for objective spec curation and affiliate link.
- Always follow standards/gathot_social_standards.md for content guidelines.""",
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
        timeout=300.0,
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
        # LLM Guardrail: Excessive Agency & Exfiltration Prevention (OWASP LLM06 / ASI02)
        is_safe, guard_err = LLMGuardrail.validate_tool_call_safety(name, args)
        if not is_safe:
            return f"SECURITY BLOCKED: {guard_err}"

        try:
            if name == "read_file":
                raw_content = self.toolbox.read_file(args.get("path", ""))
                # LLM Guardrail: Neutralize Indirect Prompt Injections in files
                result = LLMGuardrail.sanitize_untrusted_content(raw_content, source_label=args.get("path", "file"))
            elif name == "write_file":
                result = self.toolbox.write_file(args.get("path", ""), args.get("content", ""))
            elif name == "list_dir":
                result = self.toolbox.list_dir(args.get("path", "."))
            elif name == "run_command":
                result = self.toolbox.run_command(args.get("cmd", ""), timeout=args.get("timeout", 60))
            elif name == "search_code":
                result = self.toolbox.search_code(args.get("pattern", ""), args.get("path", "."))
            elif name == "spawn_cantrik":
                result = self.toolbox.spawn_cantrik(
                    parent_agent=args.get("parent_agent", "dalang"),
                    tasks=args.get("tasks", []),
                    worker_type=args.get("worker_type", "batch_task"),
                )
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
        task_context = f"{task.get('title', '')} {' '.join(task.get('artifacts', []))}"
        role_prompt += _load_standards(agent_id, task_context)

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

        async with httpx.AsyncClient(timeout=300.0) as client:
            for iteration in range(max_tool_iterations):
                # Exponential backoff retry: 3 attempts, delay 5/10/20s
                res = None
                last_err = None
                for attempt in range(3):
                    try:
                        res = await stream_completion(
                            client=client,
                            messages=messages,
                            tools=tools,
                            api_key=self.api_key,
                            model=self.model,
                        )
                        break  # success, exit retry loop
                    except Exception as e:
                        last_err = e
                        err_type = type(e).__name__
                        await log("agent_error", f"LLM stream error [{err_type}] attempt {attempt+1}/3: {e} | model={self.model}")
                        if attempt < 2:
                            delay = 5 * (2 ** attempt)  # 5s, 10s, 20s
                            await asyncio.sleep(delay)
                if res is None:
                    await log("agent_error", f"LLM stream failed after 3 retries: {last_err}")
                    return {"success": False, "error": str(last_err), "iterations": iteration}

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
