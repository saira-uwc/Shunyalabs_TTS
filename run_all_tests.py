"""Master Test Runner: Execute all TTS test scripts sequentially.

Usage:
    python run_all_tests.py              # Run all tests
    python run_all_tests.py 1 4 5        # Run specific tests by number
    python run_all_tests.py --list       # List all available tests
"""

import sys
import os
import time
import importlib
import traceback

sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

# All test modules in order
TESTS = {
    1:  ("test_01_batch_basic",          "test_batch_basic",            "Basic Batch Synthesis"),
    2:  ("test_02_streaming",            "test_streaming",              "Streaming Synthesis (WebSocket)"),
    3:  ("test_03_all_voices",           "test_all_voices",             "All 46 Voices / 23 Languages"),
    4:  ("test_04_formats",              "test_formats",                "All 7 Output Formats"),
    5:  ("test_05_speed",                "test_speed",                  "Speed Control"),
    6:  ("test_06_expressions",          "test_expressions",            "Expression Styles"),
    7:  ("test_07_trim_silence",         "test_trim_silence",           "Silence Trimming"),
    8:  ("test_08_volume_normalization", "test_volume_normalization",   "Volume Normalization"),
    9:  ("test_09_word_timestamps",      "test_word_timestamps",        "Word Timestamps"),
    10: ("test_10_background_audio",     "test_background_audio",       "Background Audio"),
}


def list_tests():
    print("Available TTS Tests:")
    print("-" * 50)
    for num, (_, _, desc) in sorted(TESTS.items()):
        print(f"  {num:>2}. {desc}")
    print()


def run_test(num: int) -> tuple[bool, float]:
    """Run a single test. Returns (success, elapsed_seconds)."""
    module_name, func_name, desc = TESTS[num]

    start = time.time()
    try:
        # Import from the tests directory
        sys.path.insert(0, "/Users/user/Documents/TTS/sdk/tests")
        mod = importlib.import_module(module_name)
        func = getattr(mod, func_name)
        func()
        elapsed = time.time() - start
        return True, elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n[FAIL] Test {num} ({desc}) failed after {elapsed:.1f}s:")
        traceback.print_exc()
        return False, elapsed


def main():
    if "--list" in sys.argv:
        list_tests()
        return

    # Determine which tests to run
    if len(sys.argv) > 1 and sys.argv[1] != "--list":
        test_nums = [int(x) for x in sys.argv[1:]]
    else:
        test_nums = sorted(TESTS.keys())

    print("=" * 70)
    print("  SHUNYALABS TTS SDK - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"  Tests to run: {len(test_nums)}")
    print(f"  Test numbers: {test_nums}")
    print("=" * 70)

    results = {}
    total_start = time.time()

    for num in test_nums:
        if num not in TESTS:
            print(f"\n[WARN] Test {num} does not exist, skipping.")
            continue

        _, _, desc = TESTS[num]
        print(f"\n{'#' * 70}")
        print(f"  RUNNING TEST {num}: {desc}")
        print(f"{'#' * 70}\n")

        success, elapsed = run_test(num)
        results[num] = (success, elapsed, desc)

    total_elapsed = time.time() - total_start

    # Summary
    print("\n\n" + "=" * 70)
    print("  TEST SUITE SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0
    for num in sorted(results.keys()):
        success, elapsed, desc = results[num]
        status = "PASS" if success else "FAIL"
        icon = "+" if success else "X"
        print(f"  [{icon}] Test {num:>2}: {desc:<35} {status} ({elapsed:.1f}s)")
        if success:
            passed += 1
        else:
            failed += 1

    print("-" * 70)
    print(f"  Total: {passed + failed} | Passed: {passed} | Failed: {failed}")
    print(f"  Total time: {total_elapsed:.1f}s")
    print("=" * 70)

    # Exit with error code if any test failed
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
