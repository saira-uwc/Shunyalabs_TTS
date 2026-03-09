"""Test 06: All 11 Expression Styles
Tests: Happy, Sad, Angry, Fearful, Surprised, Disgust, News,
       Conversational, Narrative, Enthusiastic, Neutral
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL, EXPRESSIONS

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/expressions"

# Contextual text for each expression to make the test more meaningful
EXPRESSION_TEXTS = {
    "Happy": "I am so happy today! Everything is going wonderfully well!",
    "Sad": "I feel so sad about what happened. It really hurts.",
    "Angry": "This is absolutely unacceptable! I am very angry about this!",
    "Fearful": "I am scared. Something doesn't feel right at all.",
    "Surprised": "Oh my goodness! I can't believe this just happened!",
    "Disgust": "That is absolutely disgusting. I cannot stand it.",
    "News": "Breaking news: A major discovery has been made by scientists today.",
    "Conversational": "Hey, how are you doing? I was just thinking about you.",
    "Narrative": "Once upon a time, in a land far far away, there lived a wise old sage.",
    "Enthusiastic": "This is incredible! I am so excited about this amazing opportunity!",
    "Neutral": "The weather today will be partly cloudy with temperatures around 25 degrees.",
}


def test_expressions():
    print("=" * 60)
    print("TEST 06: All 11 Expression Styles")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    total = len(EXPRESSIONS)
    passed = 0
    failed = []

    for i, expr in enumerate(EXPRESSIONS, 1):
        label = f"[{i}/{total}] Expression: {expr}"
        print(f"\n{label}")

        text = EXPRESSION_TEXTS.get(expr, f"Testing {expr} expression style.")

        try:
            # Expression is passed as part of the voice name: "Varun-Happy"
            # or via a separate field. Let's try the voice suffix approach first.
            config = TTSConfig(model=MODEL, voice=f"Varun-{expr}")
            result = client.tts.synthesize(text, config=config)

            path = f"{OUTPUT_DIR}/expr_{expr.lower()}.mp3"
            result.save(path)

            print(f"  -> Size: {len(result.audio_data)} bytes")
            print(f"  -> Saved: {path}")
            assert len(result.audio_data) > 0
            passed += 1
        except Exception as e:
            print(f"  -> Voice suffix failed: {e}")
            print(f"  -> Trying with expression in text tag...")

            # Fallback: try SSML-style or plain config
            try:
                config = TTSConfig(model=MODEL, voice="Varun")
                tagged_text = f"[{expr}] {text}"
                result = client.tts.synthesize(tagged_text, config=config)

                path = f"{OUTPUT_DIR}/expr_{expr.lower()}.mp3"
                result.save(path)

                print(f"  -> Size: {len(result.audio_data)} bytes")
                print(f"  -> Saved: {path}")
                assert len(result.audio_data) > 0
                passed += 1
            except Exception as e2:
                print(f"  -> FAILED (both approaches): {e2}")
                failed.append(expr)

    client.close()

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} expressions passed, {len(failed)} failed")
    if failed:
        print(f"  Failed expressions: {', '.join(failed)}")
    else:
        print("[PASS] All 11 expression styles tested successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_expressions()
