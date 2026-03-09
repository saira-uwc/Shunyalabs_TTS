"""Test 02: TTS Streaming Synthesis (WebSocket)
Tests: ShunyaClient.tts.stream(), stream_to_file(), and detailed mode.
"""

import sys
sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig
from config import API_KEY, MODEL

OUTPUT_DIR = "/Users/user/Documents/TTS/sdk/output/streaming"


def test_streaming():
    print("=" * 60)
    print("TEST 02: Streaming TTS Synthesis (WebSocket)")
    print("=" * 60)

    client = ShunyaClient(api_key=API_KEY)
    config = TTSConfig(model=MODEL, voice="Varun")

    # Test 1: Basic streaming - collect chunks manually
    print("\n[1/3] Streaming synthesis (manual chunk collection)...")
    chunks = []
    for audio_chunk in client.tts.stream(
        "Hello, this is a streaming synthesis test. We are testing the WebSocket connection.",
        config=config,
    ):
        chunks.append(audio_chunk)
        print(f"  -> Received chunk: {len(audio_chunk)} bytes")

    combined = b"".join(chunks)
    path = f"{OUTPUT_DIR}/stream_basic.mp3"
    with open(path, "wb") as f:
        f.write(combined)
    print(f"  -> Total chunks: {len(chunks)}")
    print(f"  -> Total size: {len(combined)} bytes")
    print(f"  -> Saved: {path}")
    assert len(combined) > 0, "No audio data received!"

    # Test 2: Detailed streaming (with chunk metadata)
    print("\n[2/3] Streaming synthesis (detailed mode with metadata)...")
    chunks_detailed = []
    for chunk_meta, audio_data in client.tts.stream(
        "Testing detailed streaming mode with chunk metadata.",
        config=config,
        detailed=True,
    ):
        chunks_detailed.append((chunk_meta, audio_data))
        print(f"  -> Chunk #{chunk_meta.chunk_index}: {len(audio_data)} bytes, "
              f"is_final={chunk_meta.is_final}")

    combined = b"".join([ad for _, ad in chunks_detailed])
    path = f"{OUTPUT_DIR}/stream_detailed.mp3"
    with open(path, "wb") as f:
        f.write(combined)
    print(f"  -> Total chunks: {len(chunks_detailed)}")
    print(f"  -> Saved: {path}")

    # Test 3: Stream to file directly
    print("\n[3/3] Stream-to-file synthesis...")
    path = f"{OUTPUT_DIR}/stream_to_file.mp3"
    completion = client.tts.stream_to_file(
        "This audio is being streamed directly to a file on disk.",
        path,
        config=config,
    )
    print(f"  -> Saved: {path}")
    print(f"  -> Status: {completion.status}")
    print(f"  -> Total chunks: {completion.total_chunks}")
    print(f"  -> Duration: {completion.total_duration_seconds}s")

    client.close()
    print("\n[PASS] Streaming synthesis test completed successfully!")


if __name__ == "__main__":
    test_streaming()
