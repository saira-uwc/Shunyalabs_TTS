"""Test 10: Background Audio with Volume Control
Tests: background_audio presets + background_volume levels.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/background"

# Common background audio preset names to try
BG_PRESETS = ["office", "cafe", "nature", "music", "rain"]
BG_VOLUMES = [0.05, 0.1, 0.3, 0.5]


def test_background_audio():
    print("=" * 60)
    print("TEST 10: Background Audio with Volume Control")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    text = "This audio has background sound mixed in. Listen carefully to the background."

    # Test 1: No background (baseline)
    print("\n[Baseline] No background audio...")
    config_base = TTSConfig(model=MODEL, voice="Varun")
    result_base = client.tts.synthesize(text, config=config_base)
    path = f"{OUTPUT_DIR}/no_background.mp3"
    result_base.save(path)
    print(f"  -> Size: {len(result_base.audio_data)} bytes -> {path}")

    # Test 2: Try different background presets
    print("\n--- Testing Background Presets ---")
    passed_presets = []
    for preset in BG_PRESETS:
        print(f"\n  Preset: '{preset}'")
        try:
            config = TTSConfig(
                model=MODEL,
                voice="Varun",
                background_audio=preset,
                background_volume=0.2,
            )
            result = client.tts.synthesize(text, config=config)
            path = f"{OUTPUT_DIR}/bg_{preset}.mp3"
            result.save(path)
            print(f"    -> Size: {len(result.audio_data)} bytes -> {path}")
            passed_presets.append(preset)
        except Exception as e:
            print(f"    -> Failed: {e}")

    # Test 3: Volume levels with a working preset (or first one)
    test_preset = passed_presets[0] if passed_presets else "office"
    print(f"\n--- Testing Volume Levels (preset: '{test_preset}') ---")
    for vol in BG_VOLUMES:
        print(f"\n  Volume: {vol}")
        try:
            config = TTSConfig(
                model=MODEL,
                voice="Varun",
                background_audio=test_preset,
                background_volume=vol,
            )
            result = client.tts.synthesize(text, config=config)
            vol_str = str(vol).replace(".", "_")
            path = f"{OUTPUT_DIR}/bg_vol_{vol_str}.mp3"
            result.save(path)
            print(f"    -> Size: {len(result.audio_data)} bytes -> {path}")
        except Exception as e:
            print(f"    -> Failed: {e}")

    client.close()
    print("\n[PASS] Background audio test completed!")


if __name__ == "__main__":
    test_background_audio()
