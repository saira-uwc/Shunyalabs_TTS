"""Test 01: Basic TTS Batch Synthesis (HTTP)
Tests: ShunyaClient.tts.synthesize() with default config.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/batch"


def test_batch_basic():
    print("=" * 60)
    print("TEST 01: Basic Batch TTS Synthesis")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)

    # Test 1: Simple English synthesis
    print("\n[1/3] Synthesizing English text with Varun (male)...")
    config = TTSConfig(model=MODEL, voice="Varun")
    result = client.tts.synthesize(
        "Hello, welcome to the Shunyalabs text to speech testing suite.",
        config=config,
    )
    path = f"{OUTPUT_DIR}/basic_varun_en.mp3"
    result.save(path)
    print(f"  -> Saved: {path}")
    print(f"  -> Audio size: {len(result.audio_data)} bytes")
    print(f"  -> Format: {result.format}")
    print(f"  -> Sample rate: {result.sample_rate} Hz")
    print(f"  -> Duration: {result.duration_seconds}s")
    assert len(result.audio_data) > 0, "Audio data is empty!"

    # Test 2: Female voice
    print("\n[2/3] Synthesizing English text with Nisha (female)...")
    config = TTSConfig(model=MODEL, voice="Nisha")
    result = client.tts.synthesize(
        "This is a test of the female English voice.",
        config=config,
    )
    path = f"{OUTPUT_DIR}/basic_nisha_en.mp3"
    result.save(path)
    print(f"  -> Saved: {path}")
    print(f"  -> Audio size: {len(result.audio_data)} bytes")
    assert len(result.audio_data) > 0, "Audio data is empty!"

    # Test 3: Hindi synthesis
    print("\n[3/3] Synthesizing Hindi text with Rajesh (male)...")
    config = TTSConfig(model=MODEL, voice="Rajesh")
    result = client.tts.synthesize(
        "नमस्ते, शुन्यलैब्स टेक्स्ट टू स्पीच टेस्टिंग सूट में आपका स्वागत है।",
        config=config,
    )
    path = f"{OUTPUT_DIR}/basic_rajesh_hi.mp3"
    result.save(path)
    print(f"  -> Saved: {path}")
    print(f"  -> Audio size: {len(result.audio_data)} bytes")
    assert len(result.audio_data) > 0, "Audio data is empty!"

    client.close()
    print("\n[PASS] Basic batch synthesis test completed successfully!")


if __name__ == "__main__":
    test_batch_basic()
