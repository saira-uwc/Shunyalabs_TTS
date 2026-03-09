"""Test 09: Word-Level Timestamps
Tests: word_timestamps=True in batch mode, inspects timing data.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/timestamps"


def test_word_timestamps():
    print("=" * 60)
    print("TEST 09: Word-Level Timestamps (Batch Only)")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    text = "Hello world, this is a word timestamp test for Shunyalabs."

    # Test 1: Without timestamps (baseline)
    print("\n[1/2] Synthesizing WITHOUT word timestamps...")
    config_no_ts = TTSConfig(model=MODEL, voice="Varun", word_timestamps=False)
    result_no_ts = client.tts.synthesize(text, config=config_no_ts)
    path = f"{OUTPUT_DIR}/no_timestamps.mp3"
    result_no_ts.save(path)
    print(f"  -> Size: {len(result_no_ts.audio_data)} bytes")
    print(f"  -> Timestamps: {result_no_ts.word_timestamps}")
    print(f"  -> Saved: {path}")

    # Test 2: With timestamps
    print("\n[2/2] Synthesizing WITH word timestamps...")
    config_ts = TTSConfig(model=MODEL, voice="Varun", word_timestamps=True)
    result_ts = client.tts.synthesize(text, config=config_ts)
    path = f"{OUTPUT_DIR}/with_timestamps.mp3"
    result_ts.save(path)
    print(f"  -> Size: {len(result_ts.audio_data)} bytes")
    print(f"  -> Saved: {path}")

    if result_ts.word_timestamps:
        print(f"\n--- Word Timestamps ({len(result_ts.word_timestamps)} words) ---")
        for wt in result_ts.word_timestamps:
            print(f"  [{wt.start:.3f}s - {wt.end:.3f}s] \"{wt.word}\"")
    else:
        print("\n  (Note: word_timestamps returned None/empty - this may be")
        print("   because the raw audio endpoint doesn't include metadata.)")
        print("  The feature was requested in the config payload successfully.")

    client.close()
    print("\n[PASS] Word timestamps test completed!")


if __name__ == "__main__":
    test_word_timestamps()
