"""
pytest configuration for MTXT Python tests.

This file is automatically loaded by pytest and provides shared fixtures
and configuration for all test modules.
"""

import pytest
import sys


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "midi: marks tests that require MIDI support"
    )


@pytest.fixture(scope="session")
def mtxt_module():
    """
    Fixture that provides the mtxt module.

    Verifies the module is properly installed before running tests.
    """
    try:
        import mtxt
        return mtxt
    except ImportError as e:
        pytest.fail(
            f"Failed to import mtxt module: {e}\n\n"
            "Make sure you've built the module with:\n"
            "  maturin develop --features python,midi"
        )


@pytest.fixture(scope="session")
def has_midi(mtxt_module):
    """Check if MIDI support is available"""
    return hasattr(mtxt_module, 'midi_to_mtxt')


@pytest.fixture
def sample_mtxt_content():
    """Provides sample MTXT content for testing"""
    return """mtxt 1.0
meta global title "Test Song"
meta global artist "Test Artist"
0 tempo 120
0 timesig 4/4
0 note C4 dur=1 vel=0.8
1 note D4 dur=1 vel=0.8
2 note E4 dur=1 vel=0.8
"""


@pytest.fixture
def test_file_paths():
    """Provides paths to test data files"""
    from pathlib import Path

    tests_dir = Path(__file__).parent.parent
    snapshots = tests_dir / "snapshots"

    return {
        "basic": snapshots / "basic.in.mtxt",
        "transitions": snapshots / "transitions.in.mtxt",
    }
