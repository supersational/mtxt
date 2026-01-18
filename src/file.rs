use crate::process::process_records;
use crate::types::beat_time::BeatTime;
use crate::types::output_record::MtxtOutputRecord;
use crate::types::record::{MtxtRecord, MtxtRecordLine};
use crate::types::version::Version;
use std::fmt;

#[derive(Debug, Clone)]
pub struct MtxtFile {
    pub records: Vec<MtxtRecordLine>,
}

impl Default for MtxtFile {
    fn default() -> Self {
        Self::new()
    }
}

impl MtxtFile {
    pub fn new() -> Self {
        Self {
            records: Vec::new(),
        }
    }

    pub fn from_records(records: Vec<MtxtRecordLine>) -> Self {
        Self { records }
    }

    /// Get all records (underlying MtxtRecord values)
    pub fn get_records(&self) -> Vec<&MtxtRecord> {
        self.records.iter().map(|line| &line.record).collect()
    }

    /// Get the version from the records
    pub fn get_version(&self) -> Option<&Version> {
        self.records.iter().find_map(|line| match &line.record {
            MtxtRecord::Header { version } => Some(version),
            _ => None,
        })
    }

    pub fn get_global_meta(&self) -> Vec<(&str, &str)> {
        self.records
            .iter()
            .filter_map(|line| match &line.record {
                MtxtRecord::GlobalMeta { meta_type, value } => {
                    Some((meta_type.as_str(), value.as_str()))
                }
                _ => None,
            })
            .collect()
    }

    /// Get a specific global meta value
    pub fn get_global_meta_value(&self, meta_type: &str) -> Option<&str> {
        self.records.iter().find_map(|line| match &line.record {
            MtxtRecord::GlobalMeta {
                meta_type: mt,
                value,
            } if mt == meta_type => Some(value.as_str()),
            _ => None,
        })
    }

    pub fn duration(&self) -> Option<BeatTime> {
        fn record_time(record: &MtxtRecord) -> Option<BeatTime> {
            record.time()
        }

        self.records
            .iter()
            .fold(None, |max, line| match (max, record_time(&line.record)) {
                (Some(m), Some(t)) if t <= m => Some(m),
                (Some(_), None) => max,
                (_, Some(t)) => Some(t),
                (None, None) => None,
            })
    }

    pub fn add_global_meta(&mut self, meta_type: String, value: String) {
        self.records
            .push(MtxtRecordLine::new(MtxtRecord::GlobalMeta {
                meta_type,
                value,
            }));
    }

    pub fn get_output_records(&self) -> Vec<MtxtOutputRecord> {
        let records: Vec<MtxtRecord> = self
            .records
            .iter()
            .map(|line| line.record.clone())
            .collect();
        process_records(&records)
    }
}

impl fmt::Display for MtxtFile {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let mut i = 0usize;
        while i < self.records.len() {
            let line = &self.records[i];
            let record = &line.record;
            let inline_comment = &line.comment;
            match record {
                // File-level records don't have timestamps
                MtxtRecord::Header { .. } | MtxtRecord::GlobalMeta { .. } => {
                    write!(f, "{}", record)?;
                    if let Some(comment) = inline_comment {
                        write!(f, " // {}", comment)?;
                    }
                    writeln!(f)?;
                }
                // Formatting-only records
                MtxtRecord::EmptyLine => {
                    if let Some(comment) = inline_comment {
                        writeln!(f, "// {}", comment)?;
                    } else {
                        writeln!(f)?;
                    }
                }
                // Timed or directive records: print with timestamp
                _ => {
                    let time = record.time();

                    let with_time = match time {
                        Some(time) => format!("{} {}", time, record),
                        None => format!("{}", record),
                    };

                    write!(f, "{}", with_time)?;
                    if let Some(comment) = inline_comment {
                        write!(f, " // {}", comment)?;
                    }
                    writeln!(f)?;
                }
            }
            i += 1;
        }
        Ok(())
    }
}
