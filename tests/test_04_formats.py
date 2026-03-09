"""Test 04: All 7 Output Formats
Tests: pcm, wav, mp3, ogg_opus, flac, mulaw, alaw
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig, OutputFormat
from config import API_KEY, MODEL, FORMATS

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/formats"

# Map string format names to OutputFormat enum
FORMAT_MAP = {
    "pcm": OutputFormat.PCM,
    "wav": OutputFormat.WAV,
    "mp3": OutputFormat.MP3,
    "ogg_opus": OutputFormat.OGG_OPUS,
    "flac": OutputFormat.FLAC,
    "mulaw": OutputFormat.MULAW,
    "alaw": OutputFormat.ALAW,
}

# File extensions for each format
EXT_MAP = {
    "pcm": "pcm",
    "wav": "wav",
    "mp3": "mp3",
    "ogg_opus": "ogg",
    "flac": "flac",
    "mulaw": "raw",
    "alaw": "raw",
}


def test_formats():
    print("=" * 60)
    print("TEST 04: All 7 Output Formats")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    text = "Testing audio output format. This sentence should sound the same in every format."
    total = len(FORMATS)
    passed = 0
    failed = []

    for i, fmt in enumerate(FORMATS, 1):
        label = f"[{i}/{total}] Format: {fmt}"
        print(f"\n{label}")

        try:
            config = TTSConfig(
                model=MODEL,
                voice="Varun",
                response_format=FORMAT_MAP[fmt],
            )
            result = client.tts.synthesize(text, config=config)

            ext = EXT_MAP[fmt]
            path = f"{OUTPUT_DIR}/format_{fmt}.{ext}"
            result.save(path)

            print(f"  -> Size: {len(result.audio_data)} bytes")
            print(f"  -> Format reported: {result.format}")
            print(f"  -> Saved: {path}")
            assert len(result.audio_data) > 0, f"Empty audio for {fmt}"
            passed += 1
        except Exception as e:
            print(f"  -> FAILED: {e}")
            failed.append(fmt)

    client.close()

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} formats passed, {len(failed)} failed")
    if failed:
        print(f"  Failed formats: {', '.join(failed)}")
    else:
        print("[PASS] All 7 output formats tested successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_formats()
