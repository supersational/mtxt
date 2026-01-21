# MTXT - Music Text Format - Python Bindings

This is a Python binding to the [MTXT](https://github.com/danibiro/mtxt) library. See their readme for more information on the project and format details. 



## What is MTXT?

MTXT is a human-editable, text-based format for representing musical performance data. It stores events with precise timing, pitch, and expression values in a simple line-based structure that's easy to edit without requiring specialized tools.

The format is designed for cases where exact performance details matter - arbitrary timings, micro-tuning, dynamic changes, and other expressive parameters. MTXT avoids binary encoding, making it suitable for manual and AI-assisted editing.



### Usage

```python
import mtxt

# Parse MTXT
file = mtxt.parse("""mtxt 1.0
0 tempo 120
0 note C4 dur=1 vel=0.8
""")
# Or using file I/O
file = mtxt.load("song.mtxt")
file.save("output.mtxt")


# Access properties
print(file.version)           # "1.0"
print(file.duration)          # 0.0 (beats)
print(file.get_meta("title")) # metadata


# MIDI conversion
file.to_midi("output.mid")
file_from_midi = mtxt.MtxtFile.from_midi("output.mid")

# Print as mtxt string
print(file_from_midi)
# Prints: MtxtFile(version=Some("1.0"), records=3, duration=Some(0.0))
print(repr(file_from_midi))
```


### How to build the library

```bash
pip install maturin
maturin develop --features python,midi

# run tests
pytest tests/python/
```

For more details on the MTXT format specification and CLI options, see the [main MTXT repository](https://github.com/Daninet/mtxt).


## License

Original MTXT library: Copyright © 2025 Dani Biró
Python bindings: Copyright © 2026 Sven Hollowell

MTXT specification and reference implementation are dual-licensed under the Apache-2.0 license or the MIT license, at your option.

