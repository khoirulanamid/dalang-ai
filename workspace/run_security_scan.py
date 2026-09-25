"""
Dalang-AI Security Scan Script
Jalankan ini dulu, hasilnya dipakai Kai untuk nulis SECURITY_AUDIT.md
"""
import subprocess, sys, json, os

venv = "/root/storage/projects/dalang-ai/.venv/bin/python3"
workspace = "/root/storage/projects/dalang-ai/workspace"
os.chdir(workspace)

print("=" * 60)
print("BANDIT SAST SCAN")
print("=" * 60)
r = subprocess.run(
    [venv, "-m", "bandit", "-r", "auth_models.py", "token_service.py", "auth_api.py", "-f", "txt"],
    capture_output=True, text=True, cwd=workspace
)
print(r.stdout[-3000:])
print(r.stderr[-500:] if r.stderr else "")

print("\n" + "=" * 60)
print("PIP-AUDIT CVE SCAN")
print("=" * 60)
r2 = subprocess.run(
    [venv, "-m", "pip_audit", "--format", "columns"],
    capture_output=True, text=True, cwd=workspace
)
print(r2.stdout[:2000])

print("\n" + "=" * 60)
print("SECRET ENTROPY CHECK")
print("=" * 60)
import re
files = ["auth_api.py", "token_service.py", "auth_models.py"]
for f in files:
    with open(f) as fh:
        content = fh.read()
    secrets = re.findall(r'(secret|password|key|token)\s*=\s*["\']([^"\']{8,})["\']', content, re.I)
    if secrets:
        print(f"[WARN] Potential hardcoded secret in {f}: {secrets[:3]}")
    else:
        print(f"[OK] No hardcoded secrets in {f}")

print("\nScan complete.")
