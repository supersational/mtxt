#!/usr/bin/env python3
"""
Edge case tests for MTXT Python bindings.

Tests unusual scenarios, boundary conditions, and potential failure modes.
"""

import sys
import os
import tempfile
from pathlib import Path


def test_load_same_file_multiple_times():
    """Test loading the same file multiple times doesn't cause issues"""
    import mtxt

    content = """mtxt 1.0
meta global title "Test"
0 tempo 120
0 note C4 dur=1
"""

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mtxt', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        # Load same file multiple times
        file1 = mtxt.load(temp_path)
        file2 = mtxt.load(temp_path)
        file3 = mtxt.load(temp_path)

        # All should be independent
        file1.set_metadata("test1", "value1")
        file2.set_metadata("test2", "value2")
        file3.set_metadata("test3", "value3")

        # Check independence
        assert file1.get_meta("test1") == "value1"
        assert file1.get_meta("test2") is None
        assert file1.get_meta("test3") is None

        assert file2.get_meta("test1") is None
        assert file2.get_meta("test2") == "value2"
        assert file2.get_meta("test3") is None

        assert file3.get_meta("test1") is None
        assert file3.get_meta("test2") is None
        assert file3.get_meta("test3") == "value3"

        print("✓ Multiple loads are independent")

    finally:
        os.unlink(temp_path)


def test_bidirectional_conversion_chain():
    """Test conversion chains: MTXT → MIDI → MTXT → MIDI"""
    import mtxt

    content = """mtxt 1.0
meta global title "Chain Test"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note E4 dur=1 vel=0.8
2 note G4 dur=1 vel=0.8
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        paths = {
            'mtxt1': os.path.join(tmpdir, 'file1.mtxt'),
            'midi1': os.path.join(tmpdir, 'file1.mid'),
            'mtxt2': os.path.join(tmpdir, 'file2.mtxt'),
            'midi2': os.path.join(tmpdir, 'file2.mid'),
        }

        # MTXT → MIDI → MTXT → MIDI
        file1 = mtxt.parse(content)
        file1.save(paths['mtxt1'])
        print(f"  1. Saved MTXT: {os.path.getsize(paths['mtxt1'])} bytes")

        file1.to_midi(paths['midi1'])
        print(f"  2. Converted to MIDI: {os.path.getsize(paths['midi1'])} bytes")

        file2 = mtxt.MtxtFile.from_midi(paths['midi1'])
        file2.save(paths['mtxt2'])
        print(f"  3. Converted back to MTXT: {os.path.getsize(paths['mtxt2'])} bytes")

        file2.to_midi(paths['midi2'])
        print(f"  4. Converted to MIDI again: {os.path.getsize(paths['midi2'])} bytes")

        # Check all files exist
        for name, path in paths.items():
            assert os.path.exists(path), f"{name} doesn't exist"
            assert os.path.getsize(path) > 0, f"{name} is empty"

        # Check basic properties preserved
        assert file2.version is not None
        assert file2.duration is not None

        print("✓ Bidirectional conversion chain works")


def test_parse_vs_load_consistency():
    """Test that parse(string) and load(file) produce identical results"""
    import mtxt

    content = """mtxt 1.0
meta global title "Consistency Test"
meta global artist "Test Artist"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=1 vel=0.75
"""

    # Parse from string
    file_from_parse = mtxt.parse(content)

    # Save and load from file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mtxt', delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        file_from_load = mtxt.load(temp_path)

        # Compare properties
        assert file_from_parse.version == file_from_load.version
        assert file_from_parse.duration == file_from_load.duration
        assert len(file_from_parse) == len(file_from_load)
        assert dict(file_from_parse.metadata) == dict(file_from_load.metadata)

        # Serialize both
        serialized_parse = str(file_from_parse)
        serialized_load = str(file_from_load)

        # Should be identical
        assert serialized_parse == serialized_load

        print("✓ parse() and load() are consistent")

    finally:
        os.unlink(temp_path)


def test_repeated_serialization():
    """Test serializing and re-parsing multiple times remains stable"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    file = mtxt.parse(content)

    # Serialize and re-parse 5 times
    for i in range(5):
        serialized = str(file)
        file = mtxt.parse(serialized)

        # Properties should remain stable
        assert file.version == "1.0"
        assert len(file) >= 3  # At least version, tempo, note

    print("✓ Repeated serialization is stable")


def test_midi_roundtrip_preserves_structure():
    """Test MIDI roundtrip preserves basic musical structure"""
    import mtxt

    content = """mtxt 1.0
meta global title "Structure Test"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=1 vel=0.8
2 note E4 dur=1 vel=0.8
3 note F4 dur=1 vel=0.8
4 note G4 dur=1 vel=0.8
"""

    with tempfile.TemporaryFile(suffix='.mid') as midi_file:
        # Convert to MIDI
        file1 = mtxt.parse(content)
        original_duration = file1.duration

        # Use a named temporary file for MIDI
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            midi_path = f.name

        try:
            file1.to_midi(midi_path)

            # Convert back
            file2 = mtxt.MtxtFile.from_midi(midi_path)

            # Duration should be approximately preserved
            assert file2.duration is not None
            duration_diff = abs(file2.duration - original_duration)
            assert duration_diff < 1.0, f"Duration changed too much: {duration_diff}"

            # Should still have a tempo and notes
            assert file2.version is not None
            assert len(file2) > 0

            print("✓ MIDI roundtrip preserves structure")

        finally:
            os.unlink(midi_path)


def test_empty_metadata_operations():
    """Test files with no metadata handle operations correctly"""
    import mtxt

    # File with no metadata
    content = """mtxt 1.0
0 tempo 120
0 note C4
"""

    file = mtxt.parse(content)

    # Metadata should be empty
    assert len(file.metadata) == 0

    # Getting non-existent metadata
    assert file.get_meta("nonexistent") is None
    assert file.get_meta("title") is None

    # Setting metadata on empty file
    file.set_metadata("new_key", "new_value")
    assert file.get_meta("new_key") == "new_value"
    assert len(file.metadata) == 1

    print("✓ Empty metadata operations work")


def test_overwrite_same_file():
    """Test overwriting the same file multiple times"""
    import mtxt

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mtxt', delete=False) as f:
        temp_path = f.name

    try:
        # Write and overwrite multiple times
        for i in range(5):
            content = f"""mtxt 1.0
meta global iteration "{i}"
0 tempo {100 + i * 10}
0 note C4
"""
            file = mtxt.parse(content)
            file.save(temp_path)

            # Load back and verify
            loaded = mtxt.load(temp_path)
            assert loaded.get_meta("iteration") == f'"{i}"'

        print("✓ Overwriting same file works")

    finally:
        os.unlink(temp_path)


def test_concurrent_file_objects():
    """Test multiple file objects from same source don't interfere"""
    import mtxt

    content = """mtxt 1.0
meta global title "Original"
0 tempo 120
0 note C4
"""

    # Create multiple objects from same content
    file1 = mtxt.parse(content)
    file2 = mtxt.parse(content)
    file3 = mtxt.parse(content)

    # Modify each differently
    file1.set_metadata("id", "file1")
    file2.set_metadata("id", "file2")
    file3.set_metadata("id", "file3")

    # Verify no cross-contamination
    assert file1.get_meta("id") == "file1"
    assert file2.get_meta("id") == "file2"
    assert file3.get_meta("id") == "file3"

    # Original title should still be in all
    assert file1.get_meta("title") == '"Original"'
    assert file2.get_meta("title") == '"Original"'
    assert file3.get_meta("title") == '"Original"'

    print("✓ Concurrent file objects are independent")


def test_large_file_handling():
    """Test handling of files with many records"""
    import mtxt

    # Generate a file with many notes
    lines = ["mtxt 1.0", "0 tempo 120"]

    # Add 1000 notes
    for i in range(1000):
        beat = i * 0.25  # 250 beats total
        pitch = 60 + (i % 12)  # Cycle through octave
        lines.append(f"{beat} note C4 vel=0.8")

    content = "\n".join(lines)

    file = mtxt.parse(content)

    assert len(file) >= 1000  # At least 1000 records plus header/tempo
    assert file.duration is not None
    assert file.duration >= 249.0  # Should be around 250 beats

    # Serialize should work
    serialized = str(file)
    assert len(serialized) > 10000  # Should be substantial

    print(f"✓ Large file handling works ({len(file)} records)")


def test_midi_file_not_found():
    """Test proper error handling for non-existent MIDI files"""
    import mtxt

    try:
        mtxt.MtxtFile.from_midi("/nonexistent/path/file.mid")
        assert False, "Should have raised error"
    except Exception as e:
        assert "nonexistent" in str(e).lower() or "no such file" in str(e).lower()
        print(f"✓ MIDI file not found handled: {type(e).__name__}")


def test_mtxt_file_not_found():
    """Test proper error handling for non-existent MTXT files"""
    import mtxt

    try:
        mtxt.load("/nonexistent/path/file.mtxt")
        assert False, "Should have raised IOError"
    except IOError as e:
        assert "nonexistent" in str(e).lower()
        print(f"✓ MTXT file not found handled: {type(e).__name__}")


def test_invalid_midi_conversion():
    """Test error handling for invalid MIDI conversion attempts"""
    import mtxt

    file = mtxt.parse("mtxt 1.0\n0 tempo 120")

    # Try to write to invalid path
    try:
        file.to_midi("/root/impossible/path/file.mid")
        assert False, "Should have raised error"
    except Exception as e:
        # Should be ConversionError, IOError, or OSError
        assert "ConversionError" in type(e).__name__ or "IOError" in type(e).__name__ or "OSError" in type(e).__name__
        print(f"✓ Invalid MIDI path handled: {type(e).__name__}")


def test_string_representation_stability():
    """Test __str__ and __repr__ are stable across operations"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4
"""

    file = mtxt.parse(content)

    # Get initial representations
    str1 = str(file)
    repr1 = repr(file)

    # Do some operations
    file.set_metadata("test", "value")
    file.get_meta("test")

    # Get representations again
    str2 = str(file)
    repr2 = repr(file)

    # str should change (metadata added)
    assert str1 != str2
    assert "test" in str2

    # repr format should be consistent
    assert "MtxtFile" in repr1
    assert "MtxtFile" in repr2
    assert "version" in repr1.lower()
    assert "version" in repr2.lower()

    print("✓ String representations are stable")


def test_zero_duration_file():
    """Test files with no timed events (duration = None or 0)"""
    import mtxt

    # File with only header
    minimal = mtxt.parse("mtxt 1.0")
    assert minimal.duration is None or minimal.duration == 0

    # File with only global metadata
    metadata_only = mtxt.parse("""mtxt 1.0
meta global title "No Music"
meta global artist "Nobody"
""")
    assert metadata_only.duration is None or metadata_only.duration == 0

    print("✓ Zero duration files handled")


def test_mixed_load_methods():
    """Test mixing parse(), load(), and from_midi() in same session"""
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        mtxt_path = os.path.join(tmpdir, "test.mtxt")
        midi_path = os.path.join(tmpdir, "test.mid")

        # Write files
        with open(mtxt_path, 'w') as f:
            f.write(content)

        # Load via parse
        file1 = mtxt.parse(content)
        file1.to_midi(midi_path)

        # Load via load
        file2 = mtxt.load(mtxt_path)

        # Load via from_midi
        file3 = mtxt.MtxtFile.from_midi(midi_path)

        # All should work independently
        file1.set_metadata("source", "parse")
        file2.set_metadata("source", "load")
        file3.set_metadata("source", "from_midi")

        assert file1.get_meta("source") == "parse"
        assert file2.get_meta("source") == "load"
        assert file3.get_meta("source") == "from_midi"

        print("✓ Mixed load methods work independently")


def main():
    """Run all edge case tests"""
    print("=" * 70)
    print("MTXT Edge Case Test Suite")
    print("=" * 70)

    try:
        import mtxt
        print(f"✓ Successfully imported mtxt v{mtxt.__version__}\n")
    except ImportError as e:
        print(f"✗ Failed to import mtxt: {e}")
        print("\nMake sure you've built the module with:")
        print("  maturin develop --features python,midi")
        return 1

    tests = [
        test_load_same_file_multiple_times,
        test_bidirectional_conversion_chain,
        test_parse_vs_load_consistency,
        test_repeated_serialization,
        test_midi_roundtrip_preserves_structure,
        test_empty_metadata_operations,
        test_overwrite_same_file,
        test_concurrent_file_objects,
        test_large_file_handling,
        test_midi_file_not_found,
        test_mtxt_file_not_found,
        test_invalid_midi_conversion,
        test_string_representation_stability,
        test_zero_duration_file,
        test_mixed_load_methods,
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
        print(f"✓ All {len(tests)} edge case tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
