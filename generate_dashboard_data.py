#!/usr/bin/env python3
"""Generate docs/data.json for the GitHub Pages dashboard.

Reads output/test_report.json and appends to a run history,
producing docs/data.json with current + historical run data.
"""

import json
import os
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE, "output", "test_report.json")
DATA_PATH = os.path.join(BASE, "docs", "data.json")


def load_report():
    with open(REPORT_PATH, "r") as f:
        return json.load(f)


def load_existing_data():
    if os.path.isfile(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            return json.load(f)
    return {"runs": []}


def build_run_entry(report):
    """Build a single run entry from a test report."""
    results = report.get("results", [])

    # Category breakdown
    cats = {}
    for r in results:
        cat = r["category"]
        if cat not in cats:
            cats[cat] = {"total": 0, "pass": 0, "fail": 0, "error": 0, "latencies": []}
        cats[cat]["total"] += 1
        if r["status"] == "PASS":
            cats[cat]["pass"] += 1
        elif r["status"] == "FAIL":
            cats[cat]["fail"] += 1
        else:
            cats[cat]["error"] += 1
        cats[cat]["latencies"].append(r["duration_ms"])

    categories = []
    for name, data in cats.items():
        avg_lat = round(sum(data["latencies"]) / len(data["latencies"])) if data["latencies"] else 0
        min_lat = round(min(data["latencies"])) if data["latencies"] else 0
        max_lat = round(max(data["latencies"])) if data["latencies"] else 0
        categories.append({
            "name": name,
            "total": data["total"],
            "pass": data["pass"],
            "fail": data["fail"],
            "error": data["error"],
            "pass_rate": round(data["pass"] / data["total"] * 100, 1) if data["total"] > 0 else 0,
            "avg_latency": avg_lat,
            "min_latency": min_lat,
            "max_latency": max_lat,
        })

    # Test details
    tests = []
    for r in results:
        tests.append({
            "id": r["test_id"],
            "name": r["test_name"],
            "category": r["category"],
            "subcategory": r["subcategory"],
            "status": r["status"],
            "duration_ms": round(r["duration_ms"]),
            "audio_bytes": r["audio_bytes"],
            "audio_duration_sec": round(r.get("audio_duration_sec") or 0, 2),
            "output_format": r.get("output_format", ""),
            "error": r.get("error_message", ""),
            "notes": r.get("notes", ""),
        })

    total = report.get("total", len(results))
    passed = report.get("passed", sum(1 for r in results if r["status"] == "PASS"))
    failed = report.get("failed", sum(1 for r in results if r["status"] == "FAIL"))
    errors = report.get("errors", sum(1 for r in results if r["status"] == "ERROR"))
    all_latencies = [r["duration_ms"] for r in results]
    total_ms = round(sum(all_latencies))

    return {
        "run_id": report.get("suite_start", datetime.now().isoformat()),
        "timestamp": report.get("suite_start", datetime.now().isoformat()),
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        "total_ms": total_ms,
        "avg_latency": round(sum(all_latencies) / len(all_latencies)) if all_latencies else 0,
        "categories": categories,
        "tests": tests,
    }


def main():
    report = load_report()
    data = load_existing_data()

    entry = build_run_entry(report)

    # Deduplicate by run_id (replace if same timestamp)
    data["runs"] = [r for r in data["runs"] if r["run_id"] != entry["run_id"]]
    data["runs"].append(entry)

    # Keep last 50 runs
    data["runs"] = data["runs"][-50:]

    # Set current pointer
    data["current"] = entry

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[Dashboard] Generated docs/data.json — {len(data['runs'])} run(s), {entry['total']} tests")


if __name__ == "__main__":
    main()
