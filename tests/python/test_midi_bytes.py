#!/usr/bin/env python3
"""
Tests for MIDI bytes operations (to_midi_bytes / from_midi_bytes).

Tests the new bytes-based API for working with MIDI data in memory.
"""

import sys
import tempfile
import os


def test_to_midi_bytes_basic():
    """Test converting MTXT to MIDI bytes"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    file = mtxt.parse(content)
    midi_bytes = file.to_midi_bytes()

    # Should return bytes
    assert isinstance(midi_bytes, bytes), f"Expected bytes, got {type(midi_bytes)}"

    # Should have MIDI header
    assert midi_bytes[:4] == b'MThd', f"Invalid MIDI header: {midi_bytes[:4]}"

    # Should have reasonable size
    assert len(midi_bytes) > 20, f"MIDI too small: {len(midi_bytes)} bytes"
    assert len(midi_bytes) < 10000, f"MIDI too large: {len(midi_bytes)} bytes"

    print(f"✓ to_midi_bytes() returns valid MIDI ({len(midi_bytes)} bytes)")


def test_from_midi_bytes_basic():
    """Test parsing MIDI from bytes"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
1 note E4 dur=1
"""

    # Convert to bytes
    file1 = mtxt.parse(content)
    midi_bytes = file1.to_midi_bytes()

    # Parse from bytes
    file2 = mtxt.MtxtFile.from_midi_bytes(midi_bytes)

    # Should have version and duration
    assert file2.version is not None, "Missing version"
    assert file2.duration is not None, "Missing duration"

    # Should have records
    assert len(file2) > 0, "No records parsed"

    print(f"✓ from_midi_bytes() parsed {len(file2)} records")


def test_bytes_vs_file_equivalence():
    """Test that bytes methods produce same result as file methods"""
    import mtxt

    content = """mtxt 1.0
meta global title "Test"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=1 vel=0.8
2 note E4 dur=1 vel=0.8
"""

    file = mtxt.parse(content)

    # Get bytes via new method
    bytes_direct = file.to_midi_bytes()

    # Get bytes via file method
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        file.to_midi(tmp_path)
        with open(tmp_path, 'rb') as f:
            bytes_from_file = f.read()

        # Should be identical
        assert bytes_direct == bytes_from_file, \
            f"Bytes differ: {len(bytes_direct)} vs {len(bytes_from_file)}"

        print(f"✓ Bytes methods equivalent to file methods ({len(bytes_direct)} bytes)")

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_roundtrip_bytes():
    """Test MTXT → bytes → MTXT roundtrip"""
    import mtxt

    content = """mtxt 1.0
meta global title "Roundtrip Test"
meta global artist "Tester"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=0.5 vel=0.7
1.5 note E4 dur=0.5 vel=0.9
2 note F4 dur=1 vel=0.75
"""

    file1 = mtxt.parse(content)
    original_duration = file1.duration

    # Convert to MIDI bytes
    midi_bytes = file1.to_midi_bytes()

    # Parse back
    file2 = mtxt.MtxtFile.from_midi_bytes(midi_bytes)

    # Duration should be approximately preserved
    assert file2.duration is not None
    duration_diff = abs(file2.duration - original_duration)
    assert duration_diff < 1.0, f"Duration changed too much: {duration_diff}"

    # Should have version
    assert file2.version is not None

    # Should have records
    assert len(file2) > 0

    print(f"✓ Roundtrip preserves structure (duration {file1.duration} → {file2.duration})")


def test_bytes_with_metadata():
    """Test that metadata is preserved through bytes conversion"""
    import mtxt

    content = """mtxt 1.0
meta global title "Song Title"
meta global artist "Artist Name"
meta global composer "Composer"
0 tempo 120
0 note C4 dur=1
"""

    file1 = mtxt.parse(content)
    midi_bytes = file1.to_midi_bytes()
    file2 = mtxt.MtxtFile.from_midi_bytes(midi_bytes)

    # MIDI preserves some metadata (at least title)
    metadata = dict(file2.metadata)
    assert len(metadata) > 0, "No metadata preserved"

    # At least title should be there
    title = file2.get_meta("title")
    assert title is not None, "Title not preserved in MIDI"

    print(f"✓ Metadata preserved through bytes ({len(metadata)} entries)")


def test_bytes_empty_file():
    """Test bytes methods with minimal file"""
    import mtxt

    content = "mtxt 1.0\n0 tempo 120\n"

    file1 = mtxt.parse(content)
    midi_bytes = file1.to_midi_bytes()

    # Should still produce valid MIDI
    assert len(midi_bytes) > 20, "MIDI too small"
    assert midi_bytes[:4] == b'MThd', "Invalid MIDI header"

    # Should be parseable
    file2 = mtxt.MtxtFile.from_midi_bytes(midi_bytes)
    assert file2.version is not None

    print(f"✓ Empty file produces valid MIDI ({len(midi_bytes)} bytes)")


def test_bytes_large_file():
    """Test bytes methods with file containing many notes"""
    import mtxt

    # Generate file with 100 notes
    lines = ["mtxt 1.0", "0 tempo 120"]
    for i in range(100):
        beat = i * 0.25
        lines.append(f"{beat} note C4 dur=0.25 vel=0.8")

    content = "\n".join(lines)

    file1 = mtxt.parse(content)
    midi_bytes = file1.to_midi_bytes()

    # Should be reasonably sized
    assert len(midi_bytes) > 100, "MIDI too small for 100 notes"
    assert len(midi_bytes) < 50000, "MIDI unexpectedly large"

    # Should be parseable
    file2 = mtxt.MtxtFile.from_midi_bytes(midi_bytes)
    assert len(file2) > 50, f"Too few records: {len(file2)}"

    print(f"✓ Large file (100 notes) → {len(midi_bytes)} bytes → {len(file2)} records")


def test_bytes_basic_api():
    """Test that bytes API works without verbose parameter (simplified in v0.9)"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    file = mtxt.parse(content)

    # Test to_midi_bytes works
    midi_bytes = file.to_midi_bytes()
    assert len(midi_bytes) > 0, "should produce bytes"

    # Test from_midi_bytes works
    file2 = mtxt.MtxtFile.from_midi_bytes(midi_bytes)
    assert file2.version is not None

    print(f"✓ bytes API works (verbose removed in v0.9)")


def test_bytes_api_exists():
    """Test that new API methods exist and are accessible"""
    import mtxt

    # Should be instance methods
    assert hasattr(mtxt.MtxtFile, 'to_midi_bytes'), "Missing to_midi_bytes"
    assert hasattr(mtxt.MtxtFile, 'from_midi_bytes'), "Missing from_midi_bytes (class)"

    # Should be callable
    assert callable(mtxt.MtxtFile.to_midi_bytes), "to_midi_bytes not callable"
    assert callable(mtxt.MtxtFile.from_midi_bytes), "from_midi_bytes not callable"

    # Should also have module-level function for consistency
    assert hasattr(mtxt, 'from_midi_bytes'), "Missing from_midi_bytes (module-level)"
    assert callable(mtxt.from_midi_bytes), "Module-level from_midi_bytes not callable"

    print(f"✓ API methods exist (instance + module-level)")


def test_bytes_error_handling():
    """Test error handling for invalid MIDI bytes"""
    import mtxt

    # Invalid MIDI data
    invalid_bytes = b"Not a MIDI file"

    try:
        mtxt.MtxtFile.from_midi_bytes(invalid_bytes)
        assert False, "Should have raised ConversionError"
    except mtxt.ConversionError as e:
        assert "MIDI" in str(e) or "parse" in str(e).lower(), f"Unexpected error: {e}"
        print(f"✓ Invalid MIDI bytes raise ConversionError: {type(e).__name__}")


def test_bytes_use_case_http():
    """Test simulated HTTP use case"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    # Simulate server: serialize for transmission
    file = mtxt.parse(content)
    midi_data = file.to_midi_bytes()

    # Simulate client: receive and parse
    received_file = mtxt.MtxtFile.from_midi_bytes(midi_data)

    assert received_file.version is not None
    assert received_file.duration is not None

    print(f"✓ HTTP-like use case: {len(midi_data)} bytes transmitted")


def test_bytes_use_case_database():
    """Test simulated database storage use case"""
    import mtxt

    content = """mtxt 1.0
meta global title "DB Test"
0 tempo 120
0 note C4 dur=1
"""

    file = mtxt.parse(content)

    # Simulate storing in database
    db_record = {
        'song_id': 123,
        'title': 'DB Test',
        'midi_data': file.to_midi_bytes()
    }

    # Simulate loading from database
    loaded_file = mtxt.MtxtFile.from_midi_bytes(db_record['midi_data'])

    assert loaded_file.version is not None
    assert loaded_file.get_meta('title') is not None

    print(f"✓ Database-like use case: {len(db_record['midi_data'])} bytes stored")


def test_module_level_consistency():
    """Test module-level from_midi_bytes matches pattern of parse/load"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    file = mtxt.parse(content)
    midi_bytes = file.to_midi_bytes()

    # Both should work and produce equivalent results
    file_via_class = mtxt.MtxtFile.from_midi_bytes(midi_bytes)
    file_via_module = mtxt.from_midi_bytes(midi_bytes)

    assert file_via_class.version == file_via_module.version
    assert file_via_class.duration == file_via_module.duration
    assert len(file_via_class) == len(file_via_module)

    # Check consistency with other module-level functions
    assert callable(mtxt.parse), "parse should be callable"
    assert callable(mtxt.load), "load should be callable"
    assert callable(mtxt.midi_to_mtxt), "midi_to_mtxt should be callable"
    assert callable(mtxt.from_midi_bytes), "from_midi_bytes should be callable"

    print(f"✓ Module-level API consistent: parse/load/midi_to_mtxt/from_midi_bytes")


def main():
    """Run all bytes tests"""
    print("=" * 70)
    print("MTXT MIDI Bytes API Test Suite")
    print("=" * 70)

    try:
        import mtxt
        print(f"✓ Successfully imported mtxt v{mtxt.__version__}\n")
    except ImportError as e:
        print(f"✗ Failed to import mtxt: {e}")
        print("\nMake sure you've built the module with:")
        print("  maturin develop --features python,midi")
        return 1

    # Check for MIDI support
    if not hasattr(mtxt, 'midi_to_mtxt'):
        print("✗ MIDI support not available (midi feature not enabled)")
        return 1

    tests = [
        test_to_midi_bytes_basic,
        test_from_midi_bytes_basic,
        test_bytes_vs_file_equivalence,
        test_roundtrip_bytes,
        test_bytes_with_metadata,
        test_bytes_empty_file,
        test_bytes_large_file,
        test_bytes_verbose,
        test_bytes_api_exists,
        test_bytes_error_handling,
        test_bytes_use_case_http,
        test_bytes_use_case_database,
        test_module_level_consistency,
    ]

    failed = []
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. {test.__name__}")
        print(f"   {test.__doc__}")
        try:
            test()
        except Exception as e:
            print(f"   ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed.append(test.__name__)

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    if failed:
        print(f"✗ {len(failed)} test(s) failed out of {len(tests)}:")
        for test in failed:
            print(f"  - {test}")
        return 1
    else:
        print(f"✓ All {len(tests)} MIDI bytes tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
