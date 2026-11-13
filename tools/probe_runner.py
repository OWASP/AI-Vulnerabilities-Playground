#!/usr/bin/env python3
"""
Scriptable probe runner for OWASP AI-Vulnerabilities-Playground.
Closes: https://github.com/OWASP/AI-Vulnerabilities-Playground/issues/3

Usage:
    python tools/probe_runner.py --lab PI_01 --payloads tools/payloads/pi_01.json
    python tools/probe_runner.py --lab PI_01 --payloads tools/payloads/pi_01.json --base-url http://localhost:8000
"""

import argparse
import json
import re
import sys
import requests


BASE_URL = "http://localhost:8000"


def send_prompt(lab_id: str, prompt: str, base_url: str) -> str:
    """Send a prompt and collect the full SSE response text."""
    url = f"{base_url}/api/labs/{lab_id}/chat"
    collected = []
    with requests.post(url, json={"prompt": prompt}, stream=True, timeout=60) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            text = line.decode("utf-8") if isinstance(line, bytes) else line
            if text.startswith("data:"):
                payload = text[len("data:"):].strip()
                try:
                    chunk = json.loads(payload)
                    if "content" in chunk:
                        collected.append(chunk["content"])
                except json.JSONDecodeError:
                    pass
    return "".join(collected)


def validate(lab_id: str, answer: str, base_url: str) -> bool:
    """Check whether the extracted answer is the correct secret."""
    url = f"{base_url}/api/secrets/validate"
    r = requests.post(url, json={"labId": lab_id, "answer": answer.strip()}, timeout=10)
    r.raise_for_status()
    return r.json().get("success", False)


def extract_secret(response_text: str) -> str:
    """
    Extract secret from response. Tries in order:
    1. Value after API-KEY= (handles PI_01 system-prompt leaks)
    2. Last non-empty line
    ponytail: extend with per-lab regex patterns if needed
    """
    m = re.search(r"API-KEY=(\S+)", response_text)
    if m:
        return m.group(1).rstrip(".")
    lines = [l.strip() for l in response_text.splitlines() if l.strip()]
    return lines[-1] if lines else response_text.strip()


def run(lab_id: str, payloads: list[dict], base_url: str) -> None:
    passed = 0
    failed = 0

    for probe in payloads:
        prompt = probe["prompt"]
        expect_success = probe.get("expect_success", True)
        extract_mode = probe.get("extract", "last_line")

        response = send_prompt(lab_id, prompt, base_url)
        answer = response.strip() if extract_mode == "full" else extract_secret(response)
        success = validate(lab_id, answer, base_url)
        outcome = success == expect_success

        status = "PASS" if outcome else "FAIL"
        marker = "✓" if outcome else "✗"
        print(f"{marker} {lab_id} | {status} | {prompt[:60]!r}")
        if not outcome:
            print(f"  response: {response[:120]!r}")

        if outcome:
            passed += 1
        else:
            failed += 1

    total = passed + failed
    print(f"\n{passed}/{total} probes passed")
    if failed:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe runner for AI-Vulnerabilities-Playground")
    parser.add_argument("--lab", required=True, help="Lab ID, e.g. PI_01")
    parser.add_argument("--payloads", required=True, help="Path to JSON payload file")
    parser.add_argument("--base-url", default=BASE_URL, help=f"API base URL (default: {BASE_URL})")
    args = parser.parse_args()

    with open(args.payloads) as f:
        payloads = json.load(f)

    if not isinstance(payloads, list) or not payloads:
        print("error: payload file must be a non-empty JSON array", file=sys.stderr)
        sys.exit(1)

    run(args.lab, payloads, args.base_url)


if __name__ == "__main__":
    main()
