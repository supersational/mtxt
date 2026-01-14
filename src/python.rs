//! Python bindings for the mtxt library using PyO3

use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyRuntimeError, PyIOError};

use crate::file::MtxtFile as RustMtxtFile;
use crate::parser::parse_mtxt as rust_parse_mtxt;

#[cfg(feature = "midi")]
use crate::midi::{convert_midi_to_mtxt as rust_convert_midi_to_mtxt, convert_mtxt_to_midi as rust_convert_mtxt_to_midi};

pyo3::create_exception!(mtxt, ParseError, PyValueError);
pyo3::create_exception!(mtxt, ConversionError, PyRuntimeError);

/// MTXT file with parsed records
#[pyclass(name = "MtxtFile", unsendable)]
#[derive(Clone)]
pub struct PyMtxtFile {
    inner: RustMtxtFile,
}

#[pymethods]
impl PyMtxtFile {
    #[new]
    fn new() -> Self {
        PyMtxtFile {
            inner: RustMtxtFile::new(),
        }
    }

    #[staticmethod]
    fn parse(content: &str) -> PyResult<Self> {
        match rust_parse_mtxt(content) {
            Ok(file) => Ok(PyMtxtFile { inner: file }),
            Err(e) => Err(ParseError::new_err(format!("Failed to parse MTXT: {}", e))),
        }
    }

    #[staticmethod]
    fn from_file(path: &str) -> PyResult<Self> {
        let content = std::fs::read_to_string(path)
            .map_err(|e| PyIOError::new_err(format!("Failed to read file '{}': {}", path, e)))?;
        Self::parse(&content)
    }

    #[cfg(feature = "midi")]
    #[staticmethod]
    #[pyo3(signature = (path, verbose=false))]
    fn from_midi(path: &str, verbose: bool) -> PyResult<Self> {
        match rust_convert_midi_to_mtxt(path, verbose) {
            Ok(file) => Ok(PyMtxtFile { inner: file }),
            Err(e) => Err(ConversionError::new_err(format!("Failed to convert MIDI: {}", e))),
        }
    }

    #[cfg(feature = "midi")]
    #[pyo3(signature = (path, verbose=false))]
    fn to_midi(&self, path: &str, verbose: bool) -> PyResult<()> {
        match rust_convert_mtxt_to_midi(&self.inner, path, verbose) {
            Ok(_) => Ok(()),
            Err(e) => Err(ConversionError::new_err(format!("Failed to convert to MIDI: {}", e))),
        }
    }

    fn save(&self, path: &str) -> PyResult<()> {
        let content = self.inner.to_string();
        std::fs::write(path, content)
            .map_err(|e| PyIOError::new_err(format!("Failed to write file '{}': {}", path, e)))
    }

    #[getter]
    fn version(&self) -> Option<String> {
        self.inner.get_version().map(|v| v.to_string())
    }

    #[getter]
    fn metadata(&self) -> PyResult<Vec<(String, String)>> {
        Ok(self.inner
            .get_global_meta()
            .into_iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect())
    }

    fn get_meta(&self, key: &str) -> Option<String> {
        self.inner.get_global_meta_value(key).map(|v| v.to_string())
    }

    fn set_metadata(&mut self, key: String, value: String) {
        self.inner.add_global_meta(key, value);
    }

    #[getter]
    fn duration(&self) -> Option<f64> {
        self.inner.duration().map(|bt| bt.as_f64())
    }

    fn __len__(&self) -> usize {
        self.inner.get_records().len()
    }

    fn __str__(&self) -> String {
        self.inner.to_string()
    }

    fn __repr__(&self) -> String {
        format!(
            "MtxtFile(version={:?}, records={}, duration={:?})",
            self.version(),
            self.__len__(),
            self.duration()
        )
    }
}

/// Parse MTXT content
///
/// Raises ParseError if invalid.
#[pyfunction]
fn parse(content: &str) -> PyResult<PyMtxtFile> {
    PyMtxtFile::parse(content)
}

/// Load MTXT from file
///
/// Raises IOError or ParseError.
#[pyfunction]
fn load(path: &str) -> PyResult<PyMtxtFile> {
    PyMtxtFile::from_file(path)
}

/// Convert MIDI to MTXT
///
/// Example:
///     file = mtxt.midi_to_mtxt("song.mid")
///     file.save("song.mtxt")
#[cfg(feature = "midi")]
#[pyfunction]
#[pyo3(signature = (midi_path, verbose=false))]
fn midi_to_mtxt(midi_path: &str, verbose: bool) -> PyResult<PyMtxtFile> {
    PyMtxtFile::from_midi(midi_path, verbose)
}

/// Convert MTXT to MIDI
///
/// Example:
///     mtxt.mtxt_to_midi("song.mtxt", "song.mid")
#[cfg(feature = "midi")]
#[pyfunction]
#[pyo3(signature = (mtxt_path, midi_path, verbose=false))]
fn mtxt_to_midi(mtxt_path: &str, midi_path: &str, verbose: bool) -> PyResult<()> {
    let file = PyMtxtFile::from_file(mtxt_path)?;
    file.to_midi(midi_path, verbose)
}

/// High-performance MTXT (Musical Text) format library
///
/// Parse, convert, and manipulate musical data. Fast Rust-based implementation.
///
/// Example:
///     file = mtxt.parse("mtxt 1.0\\n0 note C4 dur=1")
///     print(file.version, file.duration)
///     file.to_midi("output.mid")
#[pymodule]
fn mtxt(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyMtxtFile>()?;
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    m.add_function(wrap_pyfunction!(load, m)?)?;

    #[cfg(feature = "midi")]
    {
        m.add_function(wrap_pyfunction!(midi_to_mtxt, m)?)?;
        m.add_function(wrap_pyfunction!(mtxt_to_midi, m)?)?;
    }

    m.add("ParseError", m.py().get_type::<ParseError>())?;
    m.add("ConversionError", m.py().get_type::<ConversionError>())?;

    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}
