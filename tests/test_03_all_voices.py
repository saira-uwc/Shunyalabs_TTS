"""Test 03: All 46 Voices Across 23 Languages
Tests: Every male and female speaker for each supported language.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL, VOICES

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/voices"

# Sample text per language for natural-sounding output
LANG_TEXTS = {
    "Assamese":   "নমস্কাৰ, এইটো এটা পৰীক্ষা।",
    "Bengali":    "হ্যালো, এটি একটি পরীক্ষা।",
    "Bodo":       "Hello, this is a test in Bodo voice.",
    "Dogri":      "Hello, this is a test in Dogri voice.",
    "English":    "Hello, this is a voice quality test for the English language.",
    "Gujarati":   "હેલો, આ ગુજરાતી ભાષાની પરીક્ષા છે.",
    "Hindi":      "नमस्ते, यह हिंदी भाषा का परीक्षण है।",
    "Kannada":    "ಹಲೋ, ಇದು ಕನ್ನಡ ಭಾಷೆಯ ಪರೀಕ್ಷೆ.",
    "Kashmiri":   "Hello, this is a test in Kashmiri voice.",
    "Konkani":    "Hello, this is a test in Konkani voice.",
    "Maithili":   "Hello, this is a test in Maithili voice.",
    "Malayalam":  "ഹലോ, ഇത് മലയാളം ഭാഷാ പരീക്ഷണം ആണ്.",
    "Manipuri":   "Hello, this is a test in Manipuri voice.",
    "Marathi":    "हॅलो, ही मराठी भाषेची चाचणी आहे.",
    "Nepali":     "नमस्ते, यो नेपाली भाषाको परीक्षण हो।",
    "Odia":       "ହେଲୋ, ଏହା ଓଡିଆ ଭାଷାର ପରୀକ୍ଷା।",
    "Punjabi":    "ਹੈਲੋ, ਇਹ ਪੰਜਾਬੀ ਭਾਸ਼ਾ ਦੀ ਪਰੀਖਿਆ ਹੈ।",
    "Sanskrit":   "नमस्ते, एतत् संस्कृत भाषायाः परीक्षणम् अस्ति।",
    "Santali":    "Hello, this is a test in Santali voice.",
    "Sindhi":     "Hello, this is a test in Sindhi voice.",
    "Tamil":      "வணக்கம், இது தமிழ் மொழி சோதனை.",
    "Telugu":     "హలో, ఇది తెలుగు భాషా పరీక్ష.",
    "Urdu":       "ہیلو، یہ اردو زبان کا ٹیسٹ ہے۔",
}


def test_all_voices():
    print("=" * 60)
    print("TEST 03: All 46 Voices Across 23 Languages")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    total = len(VOICES) * 2  # male + female
    count = 0
    passed = 0
    failed = []

    for lang, speakers in VOICES.items():
        text = LANG_TEXTS.get(lang, f"Hello, this is a test for {lang}.")

        for gender, voice in speakers.items():
            count += 1
            label = f"[{count}/{total}] {lang} - {voice} ({gender})"
            print(f"\n{label}")

            try:
                config = TTSConfig(model=MODEL, voice=voice)
                result = client.tts.synthesize(text, config=config)

                safe_lang = lang.lower().replace(" ", "_")
                path = f"{OUTPUT_DIR}/{safe_lang}_{voice.lower()}_{gender}.mp3"
                result.save(path)

                print(f"  -> {len(result.audio_data)} bytes -> {path}")
                assert len(result.audio_data) > 0
                passed += 1
            except Exception as e:
                print(f"  -> FAILED: {e}")
                failed.append(f"{voice} ({lang}, {gender})")

    client.close()

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed, {len(failed)} failed")
    if failed:
        print(f"  Failed voices: {', '.join(failed)}")
    else:
        print("[PASS] All 46 voices tested successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_all_voices()
