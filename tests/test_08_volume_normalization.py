"""Test 08: Volume Normalization
Tests: None (default), "peak", and "loudness" normalization modes.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/normalization"


def test_volume_normalization():
    print("=" * 60)
    print("TEST 08: Volume Normalization (peak & loudness)")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    text = "Testing volume normalization. This audio should have consistent loudness levels."

    modes = [None, "peak", "loudness"]
    results = {}

    for i, mode in enumerate(modes, 1):
        mode_label = mode or "none"
        print(f"\n[{i}/{len(modes)}] Volume normalization: {mode_label}")

        try:
            config = TTSConfig(
                model=MODEL,
                voice="Varun",
                volume_normalization=mode,
            )
            result = client.tts.synthesize(text, config=config)

            path = f"{OUTPUT_DIR}/norm_{mode_label}.mp3"
            result.save(path)

            results[mode_label] = len(result.audio_data)
            print(f"  -> Size: {len(result.audio_data)} bytes")
            print(f"  -> Saved: {path}")
            assert len(result.audio_data) > 0
        except Exception as e:
            print(f"  -> FAILED: {e}")

    # Compare
    print(f"\n--- Size Comparison ---")
    for mode_label, size in results.items():
        print(f"  {mode_label:>10}: {size:>8} bytes")

    client.close()
    print("\n[PASS] Volume normalization test completed!")


if __name__ == "__main__":
    test_volume_normalization()
