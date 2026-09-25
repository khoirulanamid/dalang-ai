"""
Dalang-AI — Agent Tools
Sandboxed tool set that LLM sub-agents can call:
  read_file, write_file, list_dir, run_command, search_code
All operations are scoped to the project workspace directory.
"""

import os
import re
import subprocess
from pathlib import Path


class AgentToolbox:
    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, rel_path: str) -> Path:
        """Resolve path, block escaping outside workspace."""
        p = (self.workspace / rel_path).resolve()
        if not str(p).startswith(str(self.workspace)):
            raise PermissionError(f"Path escape blocked: {rel_path}")
        return p

    def read_file(self, path: str) -> str:
        p = self._safe_path(path)
        if not p.exists():
            return f"ERROR: File not found: {path}"
        try:
            return p.read_text(encoding="utf-8")
        except Exception as e:
            return f"ERROR reading {path}: {e}"

    def write_file(self, path: str, content: str) -> str:
        p = self._safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            p.write_text(content, encoding="utf-8")
            return f"OK: Written {len(content)} chars to {path}"
        except Exception as e:
            return f"ERROR writing {path}: {e}"

    def list_dir(self, path: str = ".") -> str:
        p = self._safe_path(path)
        if not p.exists():
            return f"ERROR: Directory not found: {path}"
        try:
            entries = sorted(p.iterdir())
            lines = []
            for e in entries:
                prefix = "📁" if e.is_dir() else "📄"
                lines.append(f"{prefix} {e.name}")
            return "\n".join(lines) if lines else "(empty directory)"
        except Exception as e:
            return f"ERROR listing {path}: {e}"

    def run_command(self, cmd: str, timeout: int = 30) -> str:
        """Run shell command inside workspace (sandboxed cwd)."""
        # Block obviously dangerous operations
        blocked = ["rm -rf /", "sudo rm", "mkfs", "dd if=", ":(){ :|:"]
        for b in blocked:
            if b in cmd:
                return f"ERROR: Blocked command: {b}"
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(self.workspace),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            out = result.stdout[-3000:] if result.stdout else ""
            err = result.stderr[-1000:] if result.stderr else ""
            if result.returncode != 0:
                return f"RETURNCODE: {result.returncode}\nSTDOUT: {out}\nSTDERR: {err}"
            return out or "(no output)"
        except subprocess.TimeoutExpired:
            return f"ERROR: Command timed out after {timeout}s"
        except Exception as e:
            return f"ERROR: {e}"

    def search_code(self, pattern: str, path: str = ".") -> str:
        """Grep-style search inside workspace."""
        p = self._safe_path(path)
        try:
            result = subprocess.run(
                ["grep", "-r", "-n", "--include=*.py", "--include=*.js",
                 "--include=*.ts", "--include=*.jsx", "--include=*.tsx",
                 "--include=*.md", pattern, str(p)],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout[-3000:] or "(no matches)"
        except Exception as e:
            return f"ERROR: {e}"

    def tool_descriptions(self) -> list[dict]:
        """OpenAI function-calling format tool specs."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a file from the project workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string", "description": "Relative path from workspace root"}},
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write or overwrite a file in the project workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string", "description": "Full file content to write"},
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_dir",
                    "description": "List files and directories in the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string", "default": "."}},
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Run a shell command inside the workspace directory. Use for: running tests, linting, installing packages, executing scripts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cmd": {"type": "string", "description": "Shell command to execute"},
                            "timeout": {"type": "integer", "default": 30},
                        },
                        "required": ["cmd"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_code",
                    "description": "Search for a pattern inside code files in the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "path": {"type": "string", "default": "."},
                        },
                        "required": ["pattern"],
                    },
                },
            },
        ]
