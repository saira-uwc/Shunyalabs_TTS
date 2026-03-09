"""Test 07: Silence Trimming
Tests: trim_silence=True vs trim_silence=False and compares output sizes.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/silence"


def test_trim_silence():
    print("=" * 60)
    print("TEST 07: Silence Trimming")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    text = "Hello. This sentence has pauses. Testing silence trimming feature."

    # Test 1: Without trimming (default)
    print("\n[1/2] Synthesizing WITHOUT silence trimming...")
    config_no_trim = TTSConfig(model=MODEL, voice="Varun", trim_silence=False)
    result_no_trim = client.tts.synthesize(text, config=config_no_trim)
    path = f"{OUTPUT_DIR}/no_trim.mp3"
    result_no_trim.save(path)
    print(f"  -> Size: {len(result_no_trim.audio_data)} bytes")
    print(f"  -> Saved: {path}")

    # Test 2: With trimming
    print("\n[2/2] Synthesizing WITH silence trimming...")
    config_trim = TTSConfig(model=MODEL, voice="Varun", trim_silence=True)
    result_trim = client.tts.synthesize(text, config=config_trim)
    path = f"{OUTPUT_DIR}/trimmed.mp3"
    result_trim.save(path)
    print(f"  -> Size: {len(result_trim.audio_data)} bytes")
    print(f"  -> Saved: {path}")

    # Compare
    diff = len(result_no_trim.audio_data) - len(result_trim.audio_data)
    pct = (diff / len(result_no_trim.audio_data) * 100) if len(result_no_trim.audio_data) > 0 else 0
    print(f"\n--- Comparison ---")
    print(f"  Without trim: {len(result_no_trim.audio_data)} bytes")
    print(f"  With trim:    {len(result_trim.audio_data)} bytes")
    print(f"  Difference:   {diff} bytes ({pct:.1f}% reduction)")

    client.close()
    print("\n[PASS] Silence trimming test completed!")


if __name__ == "__main__":
    test_trim_silence()
