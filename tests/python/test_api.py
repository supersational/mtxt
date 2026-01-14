#!/usr/bin/env python3
"""
Test script for the mtxt Python bindings.

Run this after building with: maturin develop
"""

import sys


def test_basic_parsing():
    """Test basic MTXT parsing"""
    print("Test 1: Basic parsing...")
    import mtxt

    content = """mtxt 1.0
meta global title "Test Song"
meta global composer "Test Composer"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=1 vel=0.8
2 note E4 dur=1 vel=0.8
3 note F4 dur=1 vel=0.8
"""

    file = mtxt.parse(content)

    assert file.version == "1.0", f"Expected version '1.0', got '{file.version}'"
    assert len(file) > 0, "File should have records"
    assert file.duration is not None, "File should have duration"
    assert file.duration == 3.0, f"Expected duration 3.0, got {file.duration}"

    # Check metadata
    metadata_dict = dict(file.metadata)
    assert "title" in metadata_dict, "Should have title metadata"
    assert metadata_dict["title"] == '"Test Song"', f"Wrong title: {metadata_dict['title']}"

    # Test get_meta
    title = file.get_meta("title")
    assert title == '"Test Song"', f"get_meta failed: {title}"

    print("  ✓ Parsing works")
    print(f"  ✓ Version: {file.version}")
    print(f"  ✓ Duration: {file.duration} beats")
    print(f"  ✓ Records: {len(file)}")
    print(f"  ✓ Metadata: {dict(file.metadata)}")


def test_file_io():
    """Test file I/O operations"""
    print("\nTest 2: File I/O...")
    import mtxt
    import tempfile
    import os

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    # Parse and save
    file = mtxt.parse(content)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mtxt', delete=False) as f:
        temp_path = f.name

    try:
        file.save(temp_path)
        print(f"  ✓ Saved to {temp_path}")

        # Load back
        file2 = mtxt.load(temp_path)
        assert file2.version == "1.0", "Loaded file should have same version"
        print(f"  ✓ Loaded from file")

        # Also test from_file
        file3 = mtxt.MtxtFile.from_file(temp_path)
        assert file3.version == "1.0", "from_file should work"
        print(f"  ✓ MtxtFile.from_file works")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_string_representation():
    """Test string representations"""
    print("\nTest 3: String representations...")
    import mtxt

    content = """mtxt 1.0
0 tempo 120
0 note C4 dur=1
"""

    file = mtxt.parse(content)

    # Test __str__
    str_repr = str(file)
    assert "mtxt 1.0" in str_repr, "__str__ should contain version"
    assert "tempo 120" in str_repr, "__str__ should contain tempo"
    print(f"  ✓ __str__ works")

    # Test __repr__
    repr_str = repr(file)
    assert "MtxtFile" in repr_str, "__repr__ should contain class name"
    assert "1.0" in repr_str, "__repr__ should contain version"
    print(f"  ✓ __repr__ works: {repr_str}")


def test_metadata_manipulation():
    """Test metadata manipulation"""
    print("\nTest 4: Metadata manipulation...")
    import mtxt

    file = mtxt.MtxtFile()

    # Test set_metadata
    file.set_metadata("title", '"My Song"')
    file.set_metadata("artist", '"My Artist"')

    # Test get_meta
    title = file.get_meta("title")
    artist = file.get_meta("artist")

    assert title == '"My Song"', f"set_metadata failed for title: {title}"
    assert artist == '"My Artist"', f"set_metadata failed for artist: {artist}"

    print(f"  ✓ Metadata manipulation works")
    print(f"  ✓ Title: {title}")
    print(f"  ✓ Artist: {artist}")


def test_error_handling():
    """Test error handling"""
    print("\nTest 5: Error handling...")
    import mtxt

    # Test parse error
    try:
        mtxt.parse("invalid content")
        assert False, "Should have raised ParseError"
    except mtxt.ParseError as e:
        print(f"  ✓ ParseError raised correctly: {e}")

    # Test file not found
    try:
        mtxt.load("/nonexistent/file.mtxt")
        assert False, "Should have raised IOError"
    except IOError as e:
        print(f"  ✓ IOError raised correctly for missing file")


def test_midi_conversion():
    """Test MIDI conversion (if available)"""
    print("\nTest 6: MIDI conversion...")
    import mtxt

    # Check if MIDI feature is available
    if not hasattr(mtxt, 'midi_to_mtxt'):
        print("  ⊘ MIDI conversion not available (midi feature not enabled)")
        return

    import tempfile
    import os

    content = """mtxt 1.0
meta global title "Test MIDI Conversion"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=1 vel=0.8
"""

    file = mtxt.parse(content)

    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
        midi_path = f.name

    try:
        # Convert to MIDI
        file.to_midi(midi_path, verbose=False)
        assert os.path.exists(midi_path), "MIDI file should exist"
        print(f"  ✓ Converted to MIDI: {midi_path}")

        # Convert back to MTXT
        file2 = mtxt.MtxtFile.from_midi(midi_path, verbose=False)
        assert file2.version is not None, "Converted file should have version"
        print(f"  ✓ Converted from MIDI back to MTXT")

        # Test the convenience functions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mtxt', delete=False) as f2:
            mtxt_path = f2.name

        try:
            file.save(mtxt_path)

            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f3:
                midi_path2 = f3.name

            try:
                # Test mtxt_to_midi convenience function
                mtxt.mtxt_to_midi(mtxt_path, midi_path2, verbose=False)
                assert os.path.exists(midi_path2), "MIDI file should exist"
                print(f"  ✓ mtxt_to_midi convenience function works")

            finally:
                if os.path.exists(midi_path2):
                    os.unlink(midi_path2)
        finally:
            if os.path.exists(mtxt_path):
                os.unlink(mtxt_path)

    finally:
        if os.path.exists(midi_path):
            os.unlink(midi_path)


def test_version():
    """Test version attribute"""
    print("\nTest 7: Version...")
    import mtxt

    assert hasattr(mtxt, '__version__'), "Should have __version__ attribute"
    version = mtxt.__version__
    assert isinstance(version, str), "Version should be a string"
    assert len(version) > 0, "Version should not be empty"
    print(f"  ✓ mtxt version: {version}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("MTXT Python Bindings Test Suite")
    print("=" * 60)

    try:
        import mtxt
        print(f"✓ Successfully imported mtxt module")
        print(f"✓ Version: {mtxt.__version__}")
        print()
    except ImportError as e:
        print(f"✗ Failed to import mtxt: {e}")
        print()
        print("Make sure you've built the module with:")
        print("  maturin develop")
        return 1

    tests = [
        test_basic_parsing,
        test_file_io,
        test_string_representation,
        test_metadata_manipulation,
        test_error_handling,
        test_midi_conversion,
        test_version,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed.append(test.__name__)

    print()
    print("=" * 60)
    if failed:
        print(f"✗ {len(failed)} test(s) failed: {', '.join(failed)}")
        return 1
    else:
        print(f"✓ All {len(tests)} tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
