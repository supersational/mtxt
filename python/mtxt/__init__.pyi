"""
MTXT Music Text Format - Type Stubs

A high-performance Python library for working with MTXT (Musical Text) format,
a human-readable text format for representing musical data.
"""

from typing import Optional, List, Tuple

__version__: str

class ParseError(ValueError):
    """Exception raised when MTXT content cannot be parsed"""
    pass

class ConversionError(RuntimeError):
    """Exception raised when conversion between formats fails"""
    pass

class MtxtFile:
    """
    Represents an MTXT file with its parsed records.

    This class provides methods to parse, inspect, and convert MTXT files.

    Examples:
        >>> import mtxt
        >>> # Parse from string
        >>> file = mtxt.parse("mtxt v1\\n0 note C4 dur=1")
        >>> print(file.version)
        >>>
        >>> # Load from file
        >>> file = mtxt.MtxtFile.from_file("song.mtxt")
        >>>
        >>> # Convert to MIDI
        >>> file.to_midi("output.mid")
    """

    def __init__(self) -> None:
        """Create a new empty MTXT file"""
        ...

    @staticmethod
    def parse(content: str) -> MtxtFile:
        """
        Parse an MTXT file from a string.

        Args:
            content: The MTXT content as a string

        Returns:
            The parsed MTXT file

        Raises:
            ParseError: If the content cannot be parsed
        """
        ...

    @staticmethod
    def from_file(path: str) -> MtxtFile:
        """
        Load an MTXT file from disk.

        Args:
            path: Path to the MTXT file

        Returns:
            The parsed MTXT file

        Raises:
            IOError: If the file cannot be read
            ParseError: If the content cannot be parsed
        """
        ...

    @staticmethod
    def from_midi(path: str, verbose: bool = False) -> MtxtFile:
        """
        Convert from MIDI file to MTXT.

        Args:
            path: Path to the MIDI file
            verbose: Whether to print conversion progress

        Returns:
            The converted MTXT file

        Raises:
            ConversionError: If the MIDI file cannot be converted
        """
        ...

    def to_midi(self, path: str, verbose: bool = False) -> None:
        """
        Convert this MTXT file to MIDI and save to disk.

        Args:
            path: Output path for the MIDI file
            verbose: Whether to print conversion progress

        Raises:
            ConversionError: If the conversion fails
        """
        ...

    def save(self, path: str) -> None:
        """
        Save this MTXT file to disk.

        Args:
            path: Output path for the MTXT file

        Raises:
            IOError: If the file cannot be written
        """
        ...

    @property
    def version(self) -> Optional[str]:
        """
        Get the MTXT version from the file header.

        Returns:
            The version string, or None if not present
        """
        ...

    @property
    def metadata(self) -> List[Tuple[str, str]]:
        """
        Get all global metadata as a list of tuples.

        Returns:
            List of (key, value) tuples
        """
        ...

    def get_meta(self, key: str) -> Optional[str]:
        """
        Get a specific global metadata value.

        Args:
            key: The metadata key

        Returns:
            The metadata value, or None if not found
        """
        ...

    def set_metadata(self, key: str, value: str) -> None:
        """
        Add or update a global metadata entry.

        Args:
            key: The metadata key
            value: The metadata value
        """
        ...

    @property
    def duration(self) -> Optional[float]:
        """
        Get the duration of the file in beats.

        Returns:
            The duration in beats, or None if no timed events
        """
        ...

    def __len__(self) -> int:
        """Get the number of records in the file"""
        ...

    def __str__(self) -> str:
        """Get string representation of the MTXT file"""
        ...

    def __repr__(self) -> str:
        """Get debug representation"""
        ...

def parse(content: str) -> MtxtFile:
    """
    Parse an MTXT string into an MtxtFile object.

    Args:
        content: The MTXT content as a string

    Returns:
        The parsed MTXT file

    Raises:
        ParseError: If the content cannot be parsed

    Example:
        >>> import mtxt
        >>> file = mtxt.parse("mtxt v1\\n0 note C4 dur=1")
        >>> print(file.version)
        v1
    """
    ...

def load(path: str) -> MtxtFile:
    """
    Load an MTXT file from disk.

    Args:
        path: Path to the MTXT file

    Returns:
        The parsed MTXT file

    Raises:
        IOError: If the file cannot be read
        ParseError: If the content cannot be parsed
    """
    ...

def midi_to_mtxt(midi_path: str, verbose: bool = False) -> MtxtFile:
    """
    Convert a MIDI file to MTXT format.

    Args:
        midi_path: Path to the input MIDI file
        verbose: Whether to print conversion progress

    Returns:
        The converted MTXT file

    Raises:
        ConversionError: If the conversion fails

    Example:
        >>> import mtxt
        >>> file = mtxt.midi_to_mtxt("song.mid")
        >>> file.save("song.mtxt")
    """
    ...

def mtxt_to_midi(mtxt_path: str, midi_path: str, verbose: bool = False) -> None:
    """
    Convert an MTXT file to MIDI format.

    Args:
        mtxt_path: Path to the input MTXT file
        midi_path: Path to the output MIDI file
        verbose: Whether to print conversion progress

    Raises:
        IOError: If files cannot be read/written
        ParseError: If the MTXT file cannot be parsed
        ConversionError: If the conversion fails

    Example:
        >>> import mtxt
        >>> mtxt.mtxt_to_midi("song.mtxt", "song.mid")
    """
    ...
