"""Test 05: Speed Control
Tests: 0.25x, 0.5x, 1.0x, 1.5x, 2.0x, 4.0x speed multipliers.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL, SPEEDS

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/speed"


def test_speed():
    print("=" * 60)
    print("TEST 05: Speed Control (0.25x to 4.0x)")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    text = "Testing speed control. This sentence is spoken at different speeds."
    total = len(SPEEDS)
    passed = 0
    failed = []
    results = {}

    for i, speed in enumerate(SPEEDS, 1):
        label = f"[{i}/{total}] Speed: {speed}x"
        print(f"\n{label}")

        try:
            config = TTSConfig(model=MODEL, voice="Varun", speed=speed)
            result = client.tts.synthesize(text, config=config)

            speed_str = str(speed).replace(".", "_")
            path = f"{OUTPUT_DIR}/speed_{speed_str}x.mp3"
            result.save(path)

            results[speed] = len(result.audio_data)
            print(f"  -> Size: {len(result.audio_data)} bytes")
            print(f"  -> Saved: {path}")
            assert len(result.audio_data) > 0
            passed += 1
        except Exception as e:
            print(f"  -> FAILED: {e}")
            failed.append(str(speed))

    # Compare sizes (slower should generally produce larger files)
    print("\n--- Size Comparison ---")
    for speed, size in sorted(results.items()):
        bar = "#" * (size // 1000)
        print(f"  {speed:>4}x: {size:>8} bytes {bar}")

    client.close()

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} speeds passed, {len(failed)} failed")
    if failed:
        print(f"  Failed speeds: {', '.join(failed)}")
    else:
        print("[PASS] All speed values tested successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_speed()
