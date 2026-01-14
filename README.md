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

# Access properties
print(file.version)           # "1.0"
print(file.duration)          # 0.0 (beats)
print(file.get_meta("title")) # metadata

# File I/O
file = mtxt.load("song.mtxt")
file.save("output.mtxt")

# MIDI conversion
file.to_midi("output.mid")
file2 = mtxt.MtxtFile.from_midi("input.mid")
```


### How to build the library

```bash
pip install maturin
maturin develop --features python,midi

# run tests
pytest tests/python/
```

## License

Original MTXT library: Copyright © 2025 Dani Biró
Python bindings: Copyright © 2026 Sven Hollowell

Licensed under the MIT License.
