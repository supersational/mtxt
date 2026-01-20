use crate::file::MtxtFile;
use crate::record_parser::parse_mtxt_line;
use crate::types::record::MtxtRecord;
use anyhow::{Result, bail};

pub struct MtxtParser {}

pub fn parse_mtxt(content: &str) -> Result<MtxtFile> {
    let mut parser = MtxtParser::new();
    parser.parse(content)
}

impl Default for MtxtParser {
    fn default() -> Self {
        Self::new()
    }
}

impl MtxtParser {
    pub fn new() -> Self {
        Self {}
    }

    pub fn parse(&mut self, content: &str) -> Result<MtxtFile> {
        let mut mtxt_file = MtxtFile::new();

        let mut has_mtxt_header = false;

        for (line_idx, line) in content.lines().enumerate() {
            let parsed = parse_mtxt_line(line);
            match parsed {
                Ok(record_line) => {
                    if matches!(record_line.record, MtxtRecord::Header { version: _ }) {
                        has_mtxt_header = true;
                    }
                    mtxt_file.records.push(record_line);
                }
                Err(e) => bail!("Line #{}: {}", line_idx + 1, e),
            }
        }

        if !has_mtxt_header {
            bail!("Missing version declaration");
        }

        Ok(mtxt_file)
    }
}
