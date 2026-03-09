"""Test framework for Shunyalabs TTS SDK end-to-end testing.

Provides structured test case definitions, result tracking, and reporting.
Every test case captures: status, timing, audio size, error details, and notes.
"""

import time
import json
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class TestResult:
    """Result of a single test case execution."""
    test_id: str
    test_name: str
    category: str
    subcategory: str
    description: str
    input_text: str = ""
    input_config: str = ""
    status: TestStatus = TestStatus.SKIP
    duration_ms: float = 0.0
    audio_bytes: int = 0
    audio_duration_sec: float = 0.0
    output_file: str = ""
    output_format: str = ""
    error_message: str = ""
    notes: str = ""
    timestamp: str = ""

    def to_row(self) -> list:
        """Convert to a flat list for spreadsheet row."""
        return [
            self.test_id,
            self.category,
            self.subcategory,
            self.test_name,
            self.description,
            self.input_text,
            self.input_config,
            self.status.value,
            f"{self.duration_ms:.0f}",
            str(self.audio_bytes),
            f"{self.audio_duration_sec:.2f}" if self.audio_duration_sec else "",
            self.output_format,
            self.output_file,
            self.error_message,
            self.notes,
            self.timestamp,
        ]


# Spreadsheet column headers
REPORT_HEADERS = [
    "Test ID",
    "Category",
    "Sub-Category",
    "Test Name",
    "Description",
    "Input Text",
    "Input Config",
    "Status",
    "Latency (ms)",
    "Audio Size (bytes)",
    "Audio Duration (s)",
    "Output Format",
    "Output File",
    "Error",
    "Notes",
    "Timestamp",
]


@dataclass
class TestSuite:
    """Collects results from all test cases."""
    results: list[TestResult] = field(default_factory=list)
    suite_start: float = 0.0
    suite_end: float = 0.0

    def add(self, result: TestResult):
        self.results.append(result)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.PASS)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAIL)

    @property
    def errors(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.ERROR)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.SKIP)

    def summary_row(self) -> list:
        """Summary row for the spreadsheet."""
        elapsed = self.suite_end - self.suite_start
        return [
            "", "", "", "TOTAL",
            f"{self.total} tests",
            "", "",
            f"P:{self.passed} F:{self.failed} E:{self.errors} S:{self.skipped}",
            f"{elapsed * 1000:.0f}",
            "", "", "", "", "", "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ]

    def to_rows(self) -> list[list]:
        """All result rows for the spreadsheet."""
        return [r.to_row() for r in self.results]

    def save_json(self, path: str):
        """Save results as JSON for local reference."""
        data = {
            "suite_start": datetime.fromtimestamp(self.suite_start).isoformat(),
            "suite_end": datetime.fromtimestamp(self.suite_end).isoformat(),
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "results": [asdict(r) for r in self.results],
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def print_summary(self):
        """Print a formatted summary to console."""
        print("\n" + "=" * 80)
        print("  TEST SUITE REPORT")
        print("=" * 80)

        for r in self.results:
            icon = {"PASS": "+", "FAIL": "X", "ERROR": "!", "SKIP": "-"}[r.status.value]
            line = f"  [{icon}] {r.test_id:<8} {r.test_name:<45} {r.status.value:<5} {r.duration_ms:>6.0f}ms"
            if r.audio_bytes:
                line += f"  {r.audio_bytes:>8}B"
            print(line)
            if r.error_message:
                print(f"           ERROR: {r.error_message[:80]}")

        elapsed = (self.suite_end - self.suite_start) * 1000
        print("-" * 80)
        print(f"  Total: {self.total} | Pass: {self.passed} | Fail: {self.failed} | "
              f"Error: {self.errors} | Skip: {self.skipped} | Time: {elapsed:.0f}ms")
        print("=" * 80)


def run_test_case(
    test_id: str,
    test_name: str,
    category: str,
    subcategory: str,
    description: str,
    test_fn,
    **kwargs,
) -> TestResult:
    """Execute a single test function and capture the result.

    The test_fn should return a dict with optional keys:
        audio_bytes, audio_duration_sec, output_file, notes
    Or raise an exception on failure.
    """
    result = TestResult(
        test_id=test_id,
        test_name=test_name,
        category=category,
        subcategory=subcategory,
        description=description,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    start = time.time()
    try:
        out = test_fn(**kwargs)
        elapsed = time.time() - start
        result.status = TestStatus.PASS
        result.duration_ms = elapsed * 1000

        if isinstance(out, dict):
            result.input_text = out.get("input_text", "")
            result.input_config = out.get("input_config", "")
            result.audio_bytes = out.get("audio_bytes", 0)
            result.audio_duration_sec = out.get("audio_duration_sec", 0.0)
            result.output_file = out.get("output_file", "")
            result.output_format = out.get("output_format", "")
            result.notes = out.get("notes", "")

    except AssertionError as e:
        elapsed = time.time() - start
        result.status = TestStatus.FAIL
        result.duration_ms = elapsed * 1000
        result.error_message = str(e)

    except Exception as e:
        elapsed = time.time() - start
        result.status = TestStatus.ERROR
        result.duration_ms = elapsed * 1000
        result.error_message = f"{type(e).__name__}: {e}"

    # Print inline
    icon = {"PASS": "+", "FAIL": "X", "ERROR": "!", "SKIP": "-"}[result.status.value]
    print(f"  [{icon}] {test_id} | {test_name} | {result.status.value} | "
          f"{result.duration_ms:.0f}ms | {result.audio_bytes}B")
    if result.error_message:
        print(f"       -> {result.error_message[:120]}")

    return result
