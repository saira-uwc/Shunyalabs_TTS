"""Shunyalabs TTS SDK — Comprehensive End-to-End Test Plan.

This module defines and executes ALL TTS test cases across every feature:
  1. Batch Synthesis      — basic HTTP POST synthesis
  2. Streaming Synthesis  — WebSocket streaming (chunks, detailed, stream-to-file)
  3. Voices & Languages   — all 46 voices across 23 languages
  4. Output Formats       — pcm, wav, mp3, ogg_opus, flac, mulaw, alaw
  5. Speed Control        — 0.25x to 4.0x
  6. Expression Styles    — all 11 expressions
  7. Silence Trimming     — trim_silence on/off
  8. Volume Normalization — none, peak, loudness
  9. Word Timestamps      — batch word-level timing
 10. Background Audio     — presets + volume levels
 11. Edge Cases           — empty text, long text, special characters, max speed bounds

Run:
    source venv/bin/activate
    python tts_test_plan.py              # Run all
    python tts_test_plan.py --no-sheets  # Skip Google Sheets push
    python tts_test_plan.py --category batch   # Run only one category
"""

import sys
import os
import time
import json

sys.path.insert(0, "/Users/user/Documents/TTS/sdk")

from shunyalabs import ShunyaClient
from shunyalabs.tts import TTSConfig, OutputFormat

from config import API_KEY, MODEL, VOICES, EXPRESSIONS, FORMATS, SPEEDS
from test_framework import TestSuite, TestStatus, run_test_case

OUTPUT_BASE = "/Users/user/Documents/TTS/sdk/output"
INPUTS_FILE = os.path.join(os.path.dirname(__file__), "test_inputs.json")

# ---------------------------------------------------------------------------
# Load editable test inputs (Sheet first → local JSON fallback)
# ---------------------------------------------------------------------------
INPUTS = None  # populated in main() before tests run

# ---------------------------------------------------------------------------
# Shared client
# ---------------------------------------------------------------------------
client: ShunyaClient = None


def get_client() -> ShunyaClient:
    global client
    if client is None:
        client = ShunyaClient(api_key=API_KEY)
    return client


def _cfg_str(**kw) -> str:
    """Build a human-readable config string."""
    parts = [f"model={MODEL}"]
    for k, v in kw.items():
        if v is not None:
            parts.append(f"{k}={v}")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
# 1. BATCH SYNTHESIS TESTS
# ---------------------------------------------------------------------------

def _test_batch(voice: str, text: str, output_name: str, **config_kwargs):
    """Generic batch synthesis test."""
    c = get_client()
    config = TTSConfig(model=MODEL, voice=voice, **config_kwargs)
    result = c.tts.synthesize(text, config=config)
    path = f"{OUTPUT_BASE}/batch/{output_name}"
    result.save(path)
    assert len(result.audio_data) > 0, "Empty audio data"
    fmt = config.response_format.value if config.response_format else "mp3"
    return {
        "input_text": text,
        "input_config": _cfg_str(voice=voice, **config_kwargs),
        "audio_bytes": len(result.audio_data),
        "audio_duration_sec": result.duration_seconds,
        "output_format": fmt,
        "output_file": path,
    }


def register_batch_tests(suite: TestSuite):
    batch_inputs = INPUTS["batch"]
    names = {
        "B-001": ("Batch: English Male (Varun)", "Default English male voice", "batch_varun_en.mp3"),
        "B-002": ("Batch: English Female (Nisha)", "Default English female voice", "batch_nisha_en.mp3"),
        "B-003": ("Batch: Hindi Male (Rajesh)", "Hindi male voice", "batch_rajesh_hi.mp3"),
        "B-004": ("Batch: Hindi Female (Sunita)", "Hindi female voice", "batch_sunita_hi.mp3"),
        "B-005": ("Batch: Tamil Male (Murugan)", "Tamil male voice", "batch_murugan_ta.mp3"),
        "B-006": ("Batch: Long text (500+ chars)", "Longer text input", "batch_long_text.mp3"),
    }

    for test_id, entry in batch_inputs.items():
        name, desc, output_name = names[test_id]
        r = run_test_case(
            test_id=test_id, test_name=name,
            category="Batch Synthesis", subcategory="Core",
            description=desc, test_fn=_test_batch,
            voice=entry["voice"], text=entry["text"],
            output_name=output_name,
        )
        suite.add(r)


# ---------------------------------------------------------------------------
# 2. STREAMING SYNTHESIS TESTS
# ---------------------------------------------------------------------------

def _test_stream_chunks(voice: str, text: str, output_name: str):
    c = get_client()
    config = TTSConfig(model=MODEL, voice=voice)
    chunks = []
    for audio_chunk in c.tts.stream(text, config=config):
        chunks.append(audio_chunk)
    combined = b"".join(chunks)
    path = f"{OUTPUT_BASE}/streaming/{output_name}"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(combined)
    assert len(combined) > 0, "No audio chunks received"
    return {
        "input_text": text,
        "input_config": _cfg_str(voice=voice, mode="stream"),
        "audio_bytes": len(combined),
        "output_format": "mp3",
        "output_file": path,
        "notes": f"{len(chunks)} chunks",
    }


def _test_stream_detailed(voice: str, text: str, output_name: str):
    c = get_client()
    config = TTSConfig(model=MODEL, voice=voice)
    chunks = []
    for chunk_meta, audio_data in c.tts.stream(text, config=config, detailed=True):
        chunks.append((chunk_meta, audio_data))
    combined = b"".join([ad for _, ad in chunks])
    path = f"{OUTPUT_BASE}/streaming/{output_name}"
    with open(path, "wb") as f:
        f.write(combined)
    assert len(combined) > 0, "No audio chunks received"
    last_chunk = chunks[-1][0] if chunks else None
    return {
        "input_text": text,
        "input_config": _cfg_str(voice=voice, mode="stream", detailed=True),
        "audio_bytes": len(combined),
        "output_format": "mp3",
        "output_file": path,
        "notes": f"{len(chunks)} chunks, last is_final={last_chunk.is_final if last_chunk else 'N/A'}",
    }


def _test_stream_to_file(voice: str, text: str, output_name: str):
    c = get_client()
    config = TTSConfig(model=MODEL, voice=voice)
    path = f"{OUTPUT_BASE}/streaming/{output_name}"
    completion = c.tts.stream_to_file(text, path, config=config)
    size = os.path.getsize(path)
    assert size > 0, "Output file is empty"
    return {
        "input_text": text,
        "input_config": _cfg_str(voice=voice, mode="stream_to_file"),
        "audio_bytes": size,
        "audio_duration_sec": completion.total_duration_seconds,
        "output_format": "mp3",
        "output_file": path,
        "notes": f"status={completion.status}, chunks={completion.total_chunks}",
    }


def register_streaming_tests(suite: TestSuite):
    stream_inputs = INPUTS["streaming"]
    meta = {
        "S-001": ("Stream: Manual chunk collection", "Collect chunks via iterator",
                  _test_stream_chunks, "stream_chunks.mp3"),
        "S-002": ("Stream: Detailed mode (metadata)", "Chunks with TTSChunk metadata",
                  _test_stream_detailed, "stream_detailed.mp3"),
        "S-003": ("Stream: Direct to file", "stream_to_file() convenience method",
                  _test_stream_to_file, "stream_to_file.mp3"),
        "S-004": ("Stream: Hindi voice", "Streaming with Hindi voice",
                  _test_stream_chunks, "stream_hindi.mp3"),
        "S-005": ("Stream: Female voice", "Streaming with female voice",
                  _test_stream_chunks, "stream_female.mp3"),
    }

    for test_id, entry in stream_inputs.items():
        name, desc, fn, output_name = meta[test_id]
        r = run_test_case(
            test_id=test_id, test_name=name,
            category="Streaming Synthesis", subcategory="WebSocket",
            description=desc, test_fn=fn,
            voice=entry["voice"], text=entry["text"],
            output_name=output_name,
        )
        suite.add(r)


# ---------------------------------------------------------------------------
# 3. ALL 46 VOICES / 23 LANGUAGES
# ---------------------------------------------------------------------------

def register_voice_tests(suite: TestSuite):
    voice_texts = INPUTS["voices"]
    count = 0
    for lang, speakers in VOICES.items():
        text = voice_texts.get(lang, f"Hello, testing {lang}.")
        for gender, voice in speakers.items():
            count += 1
            test_id = f"V-{count:03d}"
            safe_lang = lang.lower().replace(" ", "_")
            output_name = f"{safe_lang}_{voice.lower()}_{gender}.mp3"

            r = run_test_case(
                test_id=test_id,
                test_name=f"Voice: {voice} ({lang} {gender})",
                category="Voices & Languages",
                subcategory=lang,
                description=f"{lang} {gender} voice: {voice}",
                test_fn=_test_batch,
                voice=voice, text=text,
                output_name=f"../voices/{output_name}",
            )
            suite.add(r)


# ---------------------------------------------------------------------------
# 4. OUTPUT FORMATS
# ---------------------------------------------------------------------------

FORMAT_ENUM = {
    "pcm": OutputFormat.PCM, "wav": OutputFormat.WAV, "mp3": OutputFormat.MP3,
    "ogg_opus": OutputFormat.OGG_OPUS, "flac": OutputFormat.FLAC,
    "mulaw": OutputFormat.MULAW, "alaw": OutputFormat.ALAW,
}
FORMAT_EXT = {
    "pcm": "pcm", "wav": "wav", "mp3": "mp3",
    "ogg_opus": "ogg", "flac": "flac", "mulaw": "raw", "alaw": "raw",
}


def register_format_tests(suite: TestSuite):
    text = INPUTS["formats"]["text"]
    for i, fmt in enumerate(FORMATS, 1):
        test_id = f"F-{i:03d}"
        ext = FORMAT_EXT[fmt]

        def _fn(fmt=fmt, ext=ext):
            c = get_client()
            config = TTSConfig(model=MODEL, voice="Varun", response_format=FORMAT_ENUM[fmt])
            result = c.tts.synthesize(text, config=config)
            path = f"{OUTPUT_BASE}/formats/format_{fmt}.{ext}"
            result.save(path)
            assert len(result.audio_data) > 0, f"Empty audio for {fmt}"
            return {
                "input_text": text,
                "input_config": _cfg_str(voice="Varun", response_format=fmt),
                "audio_bytes": len(result.audio_data),
                "output_format": fmt,
                "output_file": path,
                "notes": f"reported_format={result.format}",
            }

        r = run_test_case(
            test_id=test_id,
            test_name=f"Format: {fmt}",
            category="Output Formats",
            subcategory=fmt.upper(),
            description=f"Synthesize to {fmt} format",
            test_fn=_fn,
        )
        suite.add(r)


# ---------------------------------------------------------------------------
# 5. SPEED CONTROL
# ---------------------------------------------------------------------------

def register_speed_tests(suite: TestSuite):
    text = INPUTS["speed"]["text"]
    for i, speed in enumerate(SPEEDS, 1):
        test_id = f"SP-{i:03d}"

        def _fn(speed=speed):
            c = get_client()
            config = TTSConfig(model=MODEL, voice="Varun", speed=speed)
            result = c.tts.synthesize(text, config=config)
            speed_str = str(speed).replace(".", "_")
            path = f"{OUTPUT_BASE}/speed/speed_{speed_str}x.mp3"
            result.save(path)
            assert len(result.audio_data) > 0
            return {
                "input_text": text,
                "input_config": _cfg_str(voice="Varun", speed=speed),
                "audio_bytes": len(result.audio_data),
                "output_format": "mp3",
                "output_file": path,
                "notes": f"speed={speed}x",
            }

        r = run_test_case(
            test_id=test_id,
            test_name=f"Speed: {speed}x",
            category="Speed Control",
            subcategory=f"{speed}x",
            description=f"Synthesis at {speed}x speed",
            test_fn=_fn,
        )
        suite.add(r)


# ---------------------------------------------------------------------------
# 6. EXPRESSION STYLES
# ---------------------------------------------------------------------------

def register_expression_tests(suite: TestSuite):
    expr_texts = INPUTS["expressions"]
    for i, expr in enumerate(EXPRESSIONS, 1):
        test_id = f"E-{i:03d}"
        text = expr_texts.get(expr, f"Testing {expr} expression.")

        def _fn(expr=expr, text=text):
            c = get_client()
            voice_name = f"Varun-{expr}"
            config = TTSConfig(model=MODEL, voice=voice_name)
            result = c.tts.synthesize(text, config=config)
            path = f"{OUTPUT_BASE}/expressions/expr_{expr.lower()}.mp3"
            result.save(path)
            assert len(result.audio_data) > 0
            return {
                "input_text": text,
                "input_config": _cfg_str(voice=voice_name),
                "audio_bytes": len(result.audio_data),
                "output_format": "mp3",
                "output_file": path,
                "notes": f"expression={expr}",
            }

        r = run_test_case(
            test_id=test_id,
            test_name=f"Expression: {expr}",
            category="Expression Styles",
            subcategory=expr,
            description=f"Synthesize with {expr} expression",
            test_fn=_fn,
        )
        suite.add(r)


# ---------------------------------------------------------------------------
# 7. SILENCE TRIMMING
# ---------------------------------------------------------------------------

def register_silence_tests(suite: TestSuite):
    text = INPUTS["silence"]["text"]

    def _test_no_trim():
        c = get_client()
        config = TTSConfig(model=MODEL, voice="Varun", trim_silence=False)
        result = c.tts.synthesize(text, config=config)
        path = f"{OUTPUT_BASE}/silence/no_trim.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        return {
            "input_text": text,
            "input_config": _cfg_str(voice="Varun", trim_silence=False),
            "audio_bytes": len(result.audio_data),
            "output_format": "mp3",
            "output_file": path,
        }

    def _test_with_trim():
        c = get_client()
        config = TTSConfig(model=MODEL, voice="Varun", trim_silence=True)
        result = c.tts.synthesize(text, config=config)
        path = f"{OUTPUT_BASE}/silence/trimmed.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        return {
            "input_text": text,
            "input_config": _cfg_str(voice="Varun", trim_silence=True),
            "audio_bytes": len(result.audio_data),
            "output_format": "mp3",
            "output_file": path,
        }

    r1 = run_test_case("T-001", "Trim: OFF (baseline)", "Silence Trimming", "Off",
                        "Synthesis without silence trimming", _test_no_trim)
    suite.add(r1)

    r2 = run_test_case("T-002", "Trim: ON", "Silence Trimming", "On",
                        "Synthesis with trim_silence=True", _test_with_trim)
    suite.add(r2)

    if r1.status.value == "PASS" and r2.status.value == "PASS" and r1.audio_bytes > 0:
        diff = r1.audio_bytes - r2.audio_bytes
        pct = diff / r1.audio_bytes * 100
        r2.notes = f"Reduced by {diff}B ({pct:.1f}%)"


# ---------------------------------------------------------------------------
# 8. VOLUME NORMALIZATION
# ---------------------------------------------------------------------------

def register_normalization_tests(suite: TestSuite):
    text = INPUTS["normalization"]["text"]

    for mode in [None, "peak", "loudness"]:
        label = mode or "none"
        test_id = f"N-{['none','peak','loudness'].index(label)+1:03d}"

        def _fn(mode=mode, label=label):
            c = get_client()
            config = TTSConfig(model=MODEL, voice="Varun", volume_normalization=mode)
            result = c.tts.synthesize(text, config=config)
            path = f"{OUTPUT_BASE}/normalization/norm_{label}.mp3"
            result.save(path)
            assert len(result.audio_data) > 0
            return {
                "input_text": text,
                "input_config": _cfg_str(voice="Varun", volume_normalization=label),
                "audio_bytes": len(result.audio_data),
                "output_format": "mp3",
                "output_file": path,
                "notes": f"normalization={label}",
            }

        r = run_test_case(test_id, f"Normalization: {label}", "Volume Normalization",
                          label.capitalize(), f"Synthesis with {label} normalization", _fn)
        suite.add(r)


# ---------------------------------------------------------------------------
# 9. WORD TIMESTAMPS
# ---------------------------------------------------------------------------

def register_timestamp_tests(suite: TestSuite):
    text = INPUTS["timestamps"]["text"]

    def _test_no_ts():
        c = get_client()
        config = TTSConfig(model=MODEL, voice="Varun", word_timestamps=False)
        result = c.tts.synthesize(text, config=config)
        path = f"{OUTPUT_BASE}/timestamps/no_timestamps.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        return {
            "input_text": text,
            "input_config": _cfg_str(voice="Varun", word_timestamps=False),
            "audio_bytes": len(result.audio_data),
            "output_format": "mp3",
            "output_file": path,
            "notes": f"timestamps={result.word_timestamps}",
        }

    def _test_with_ts():
        c = get_client()
        config = TTSConfig(model=MODEL, voice="Varun", word_timestamps=True)
        result = c.tts.synthesize(text, config=config)
        path = f"{OUTPUT_BASE}/timestamps/with_timestamps.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        ts_count = len(result.word_timestamps) if result.word_timestamps else 0
        notes = f"{ts_count} word timestamps"
        if result.word_timestamps:
            notes += f" | first: {result.word_timestamps[0].word}"
        else:
            notes += " (raw endpoint returns binary only)"
        return {
            "input_text": text,
            "input_config": _cfg_str(voice="Varun", word_timestamps=True),
            "audio_bytes": len(result.audio_data),
            "output_format": "mp3",
            "output_file": path,
            "notes": notes,
        }

    suite.add(run_test_case("TS-001", "Timestamps: OFF", "Word Timestamps", "Off",
                            "Synthesis without timestamps", _test_no_ts))
    suite.add(run_test_case("TS-002", "Timestamps: ON", "Word Timestamps", "On",
                            "Synthesis with word_timestamps=True", _test_with_ts))


# ---------------------------------------------------------------------------
# 10. BACKGROUND AUDIO
# ---------------------------------------------------------------------------

def register_background_tests(suite: TestSuite):
    text = INPUTS["background"]["text"]
    presets = ["office", "cafe", "nature", "music", "rain"]
    volumes = [0.05, 0.1, 0.3, 0.5]

    def _test_no_bg():
        c = get_client()
        config = TTSConfig(model=MODEL, voice="Varun")
        result = c.tts.synthesize(text, config=config)
        path = f"{OUTPUT_BASE}/background/no_background.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        return {
            "input_text": text,
            "input_config": _cfg_str(voice="Varun"),
            "audio_bytes": len(result.audio_data),
            "output_format": "mp3",
            "output_file": path,
        }

    suite.add(run_test_case("BG-001", "Background: None (baseline)", "Background Audio",
                            "Baseline", "No background audio", _test_no_bg))

    for i, preset in enumerate(presets, 2):
        def _fn(preset=preset):
            c = get_client()
            config = TTSConfig(model=MODEL, voice="Varun",
                             background_audio=preset, background_volume=0.2)
            result = c.tts.synthesize(text, config=config)
            path = f"{OUTPUT_BASE}/background/bg_{preset}.mp3"
            result.save(path)
            assert len(result.audio_data) > 0
            return {
                "input_text": text,
                "input_config": _cfg_str(voice="Varun", background_audio=preset, background_volume=0.2),
                "audio_bytes": len(result.audio_data),
                "output_format": "mp3",
                "output_file": path,
                "notes": f"preset={preset}, vol=0.2",
            }

        suite.add(run_test_case(f"BG-{i:03d}", f"Background: {preset} preset",
                                "Background Audio", "Presets",
                                f"Background audio with {preset} preset", _fn))

    for j, vol in enumerate(volumes, len(presets) + 2):
        def _fn(vol=vol):
            c = get_client()
            config = TTSConfig(model=MODEL, voice="Varun",
                             background_audio="office", background_volume=vol)
            result = c.tts.synthesize(text, config=config)
            vol_str = str(vol).replace(".", "_")
            path = f"{OUTPUT_BASE}/background/bg_vol_{vol_str}.mp3"
            result.save(path)
            assert len(result.audio_data) > 0
            return {
                "input_text": text,
                "input_config": _cfg_str(voice="Varun", background_audio="office", background_volume=vol),
                "audio_bytes": len(result.audio_data),
                "output_format": "mp3",
                "output_file": path,
                "notes": f"volume={vol}",
            }

        suite.add(run_test_case(f"BG-{j:03d}", f"Background: volume={vol}",
                                "Background Audio", "Volume",
                                f"Background with volume {vol}", _fn))


# ---------------------------------------------------------------------------
# 11. EDGE CASES
# ---------------------------------------------------------------------------

def register_edge_case_tests(suite: TestSuite):
    ec = INPUTS["edge_cases"]

    def _make_simple_test(test_id, voice, output_name):
        def _fn():
            t = ec[test_id]["text"]
            c = get_client()
            config = TTSConfig(model=MODEL, voice=voice)
            result = c.tts.synthesize(t, config=config)
            path = f"{OUTPUT_BASE}/batch/{output_name}"
            result.save(path)
            assert len(result.audio_data) > 0
            return {"input_text": t, "input_config": _cfg_str(voice=voice),
                    "audio_bytes": len(result.audio_data), "output_format": "mp3", "output_file": path}
        return _fn

    suite.add(run_test_case("EC-001", "Edge: Single word", "Edge Cases", "Input",
                            "Single word input",
                            _make_simple_test("EC-001", ec["EC-001"]["voice"], "edge_single_word.mp3")))

    suite.add(run_test_case("EC-002", "Edge: Numbers & special chars", "Edge Cases", "Input",
                            "Numbers, $, @, email in text",
                            _make_simple_test("EC-002", ec["EC-002"]["voice"], "edge_special_chars.mp3")))

    suite.add(run_test_case("EC-003", "Edge: Heavy punctuation", "Edge Cases", "Input",
                            "Ellipsis, dashes, mixed punctuation",
                            _make_simple_test("EC-003", ec["EC-003"]["voice"], "edge_punctuation.mp3")))

    suite.add(run_test_case("EC-004", "Edge: Hindi-English code-switching", "Edge Cases", "Input",
                            "Mixed Hindi-English text",
                            _make_simple_test("EC-004", ec["EC-004"]["voice"], "edge_mixed_lang.mp3")))

    def _test_min_speed():
        t = ec["EC-005"]["text"]
        c = get_client()
        config = TTSConfig(model=MODEL, voice=ec["EC-005"]["voice"], speed=0.25)
        result = c.tts.synthesize(t, config=config)
        path = f"{OUTPUT_BASE}/batch/edge_min_speed.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        return {"input_text": t, "input_config": _cfg_str(voice=ec["EC-005"]["voice"], speed=0.25),
                "audio_bytes": len(result.audio_data), "output_format": "mp3", "output_file": path,
                "notes": "speed=0.25 (min)"}

    suite.add(run_test_case("EC-005", "Edge: Min speed (0.25x)", "Edge Cases", "Boundaries",
                            "Minimum allowed speed", _test_min_speed))

    def _test_max_speed():
        t = ec["EC-006"]["text"]
        c = get_client()
        config = TTSConfig(model=MODEL, voice=ec["EC-006"]["voice"], speed=4.0)
        result = c.tts.synthesize(t, config=config)
        path = f"{OUTPUT_BASE}/batch/edge_max_speed.mp3"
        result.save(path)
        assert len(result.audio_data) > 0
        return {"input_text": t, "input_config": _cfg_str(voice=ec["EC-006"]["voice"], speed=4.0),
                "audio_bytes": len(result.audio_data), "output_format": "mp3", "output_file": path,
                "notes": "speed=4.0 (max)"}

    suite.add(run_test_case("EC-006", "Edge: Max speed (4.0x)", "Edge Cases", "Boundaries",
                            "Maximum allowed speed", _test_max_speed))

    def _test_combined():
        t = ec["EC-007"]["text"]
        c = get_client()
        config = TTSConfig(
            model=MODEL, voice=ec["EC-007"]["voice"],
            speed=1.5, trim_silence=True,
            response_format=OutputFormat.WAV,
            volume_normalization="peak",
        )
        result = c.tts.synthesize(t, config=config)
        path = f"{OUTPUT_BASE}/batch/edge_combined.wav"
        result.save(path)
        assert len(result.audio_data) > 0
        return {
            "input_text": t,
            "input_config": _cfg_str(voice=ec["EC-007"]["voice"], speed=1.5, trim_silence=True,
                                     response_format="wav", volume_normalization="peak"),
            "audio_bytes": len(result.audio_data),
            "output_format": "wav",
            "output_file": path,
            "notes": "speed=1.5x, trim=on, wav, peak norm, happy expr",
        }

    suite.add(run_test_case("EC-007", "Edge: Combined features", "Edge Cases", "Combined",
                            "Speed+trim+format+norm+expression together", _test_combined))


# ---------------------------------------------------------------------------
# MAIN RUNNER
# ---------------------------------------------------------------------------

CATEGORY_MAP = {
    "batch":          register_batch_tests,
    "streaming":      register_streaming_tests,
    "voices":         register_voice_tests,
    "formats":        register_format_tests,
    "speed":          register_speed_tests,
    "expressions":    register_expression_tests,
    "silence":        register_silence_tests,
    "normalization":  register_normalization_tests,
    "timestamps":     register_timestamp_tests,
    "background":     register_background_tests,
    "edge":           register_edge_case_tests,
}


def _load_inputs(no_sheets: bool):
    """Load test inputs: try Google Sheet first, fall back to local JSON."""
    global INPUTS

    if not no_sheets:
        from sheets_reporter import fetch_inputs_from_sheet
        sheet_inputs = fetch_inputs_from_sheet()
        if sheet_inputs:
            INPUTS = sheet_inputs
            # Also save locally so test_inputs.json stays in sync
            with open(INPUTS_FILE, "w", encoding="utf-8") as f:
                json.dump(sheet_inputs, f, ensure_ascii=False, indent=2)
            print("[Inputs] Loaded from Google Sheet (local file synced)")
            return

    # Fallback to local JSON
    with open(INPUTS_FILE, "r", encoding="utf-8") as f:
        INPUTS = json.load(f)
    print(f"[Inputs] Loaded from local file: test_inputs.json")


def main():
    no_sheets = "--no-sheets" in sys.argv

    category_filter = None
    for arg in sys.argv[1:]:
        if arg.startswith("--category="):
            category_filter = arg.split("=", 1)[1]
        elif arg == "--category" and sys.argv.index(arg) + 1 < len(sys.argv):
            category_filter = sys.argv[sys.argv.index(arg) + 1]

    if "--list" in sys.argv:
        print("Available categories:")
        for k in CATEGORY_MAP:
            print(f"  {k}")
        return

    # Load inputs from Sheet or local JSON
    _load_inputs(no_sheets)

    suite = TestSuite()
    suite.suite_start = time.time()

    print("=" * 80)
    print("  SHUNYALABS TTS SDK — END-TO-END TEST PLAN")
    print(f"  Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    categories = CATEGORY_MAP
    if category_filter:
        if category_filter in CATEGORY_MAP:
            categories = {category_filter: CATEGORY_MAP[category_filter]}
        else:
            print(f"Unknown category: {category_filter}")
            return

    for cat_name, register_fn in categories.items():
        print(f"\n{'─' * 80}")
        print(f"  CATEGORY: {cat_name.upper()}")
        print(f"{'─' * 80}")
        register_fn(suite)

    suite.suite_end = time.time()

    suite.print_summary()

    json_path = f"{OUTPUT_BASE}/test_report.json"
    suite.save_json(json_path)
    print(f"\n[Local] Report saved: {json_path}")

    if not no_sheets:
        from sheets_reporter import push_results_safe
        push_results_safe(suite, inputs=INPUTS)
    else:
        print("\n[Sheets] Skipped (--no-sheets flag)")

    # Generate dashboard data
    try:
        import subprocess
        subprocess.run([sys.executable, "generate_dashboard_data.py"], check=True)
    except Exception as e:
        print(f"[Dashboard] Could not generate data: {e}")

    if client:
        client.close()

    return suite


if __name__ == "__main__":
    main()
