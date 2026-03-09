"""Google Sheets reporter via Apps Script web app.

No OAuth, no service account — just a simple HTTP POST/GET.

Setup:
  1. Open your Google Sheet
  2. Extensions > Apps Script
  3. Paste contents of apps_script.js
  4. Deploy > New deployment > Web app > Anyone > Deploy
  5. Copy the URL into .env as APPS_SCRIPT_URL=<url>

Editing inputs:
  - Edit test inputs directly in the "Inputs" tab of the Google Sheet
  - On next run, inputs are fetched from the sheet automatically
"""

import os
import json
import requests
from datetime import datetime

from dotenv import load_dotenv
from test_framework import TestSuite

load_dotenv()

APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL", "")
INPUTS_FILE = os.path.join(os.path.dirname(__file__), "test_inputs.json")


def fetch_inputs_from_sheet() -> dict | None:
    """GET test inputs from the Inputs sheet via Apps Script.
    Returns the inputs dict, or None if unavailable."""
    if not APPS_SCRIPT_URL:
        return None

    try:
        print("[Sheets] Fetching test inputs from Google Sheet...")
        resp = requests.get(APPS_SCRIPT_URL, timeout=15)
        if resp.status_code == 200:
            body = resp.json()
            if body.get("success") and body.get("inputs"):
                print("[Sheets] Got inputs from sheet. Using those for this run.")
                return body["inputs"]
            else:
                print(f"[Sheets] No inputs in sheet yet: {body.get('error', 'empty')}")
        else:
            print(f"[Sheets] GET HTTP {resp.status_code}")
    except Exception as e:
        print(f"[Sheets] Could not fetch inputs: {e}")

    return None


def build_payload(suite: TestSuite, inputs: dict = None) -> dict:
    """Build the JSON payload for the Apps Script."""
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    results = []
    for r in suite.results:
        results.append({
            "test_id": r.test_id,
            "category": r.category,
            "subcategory": r.subcategory,
            "test_name": r.test_name,
            "description": r.description,
            "input_text": r.input_text,
            "input_config": r.input_config,
            "status": r.status.value,
            "duration_ms": round(r.duration_ms),
            "audio_bytes": r.audio_bytes,
            "audio_duration_sec": round(r.audio_duration_sec, 2) if r.audio_duration_sec else "",
            "output_format": r.output_format,
            "output_file": r.output_file,
            "error_message": r.error_message,
            "notes": r.notes,
            "timestamp": r.timestamp,
        })

    # Aggregate by category
    cat_map = {}
    for r in suite.results:
        cat = r.category
        if cat not in cat_map:
            cat_map[cat] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "latencies": []}
        cat_map[cat]["total"] += 1
        if r.status.value == "PASS":
            cat_map[cat]["pass"] += 1
        elif r.status.value == "FAIL":
            cat_map[cat]["fail"] += 1
        elif r.status.value == "ERROR":
            cat_map[cat]["error"] += 1
        cat_map[cat]["latencies"].append(r.duration_ms)

    categories = []
    for name, data in cat_map.items():
        rate = f"{data['pass'] / data['total'] * 100:.0f}%" if data["total"] > 0 else "N/A"
        avg = f"{sum(data['latencies']) / len(data['latencies']):.0f}" if data["latencies"] else ""
        categories.append({
            "name": name,
            "total": data["total"],
            "pass": data["pass"],
            "fail": data["fail"],
            "error": data["error"],
            "pass_rate": rate,
            "avg_latency": avg,
        })

    total_ms = f"{(suite.suite_end - suite.suite_start) * 1000:.0f}"

    payload = {
        "run_time": run_time,
        "results": results,
        "categories": categories,
        "summary": {
            "total": suite.total,
            "passed": suite.passed,
            "failed": suite.failed,
            "errors": suite.errors,
            "skipped": suite.skipped,
            "total_ms": total_ms,
        },
    }

    # Include inputs so the Inputs sheet gets populated/updated
    if inputs:
        payload["inputs"] = inputs

    return payload


def push_results(suite: TestSuite, inputs: dict = None):
    """POST test results to the Apps Script web app."""
    if not APPS_SCRIPT_URL:
        raise ValueError(
            "APPS_SCRIPT_URL not set in .env\n"
            "  1. Open your Google Sheet > Extensions > Apps Script\n"
            "  2. Paste apps_script.js > Deploy as Web App\n"
            "  3. Add to .env: APPS_SCRIPT_URL=<your-url>"
        )

    payload = build_payload(suite, inputs)

    print(f"\n[Sheets] Pushing {len(suite.results)} test results to Google Sheets...")

    resp = requests.post(
        APPS_SCRIPT_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )

    if resp.status_code == 200:
        body = resp.json()
        if body.get("success"):
            print(f"[Sheets] Done! {body.get('rows', 0)} rows pushed.")
            print(f"[Sheets] View: https://docs.google.com/spreadsheets/d/1rbp45K3opTCTzb0-d0PTInJP7rUPdwAKDDnRS-ZkH0U")
        else:
            print(f"[Sheets] Apps Script error: {body.get('error', 'unknown')}")
    else:
        print(f"[Sheets] HTTP {resp.status_code}: {resp.text[:200]}")


def push_results_safe(suite: TestSuite, inputs: dict = None):
    """Push results, gracefully handle failures."""
    try:
        push_results(suite, inputs)
    except ValueError as e:
        print(f"\n[Sheets] {e}")
        print("  Results saved locally to output/test_report.json")
    except Exception as e:
        print(f"\n[Sheets] Could not push to Google Sheets: {e}")
        print("  Results saved locally to output/test_report.json")
