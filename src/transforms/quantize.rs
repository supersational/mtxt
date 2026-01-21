use crate::types::record::{MtxtRecord, MtxtRecordLine};

pub fn transform(
    records: &[MtxtRecordLine],
    grid: u32,
    swing: f32,
    humanize: f32,
) -> Vec<MtxtRecordLine> {
    if grid == 0 {
        return records.to_vec();
    }

    records
        .iter()
        .map(|line| {
            let mut new_line = line.clone();
            match &mut new_line.record {
                MtxtRecord::Note { time, .. }
                | MtxtRecord::NoteOn { time, .. }
                | MtxtRecord::NoteOff { time, .. }
                | MtxtRecord::ControlChange { time, .. }
                | MtxtRecord::Voice { time, .. }
                | MtxtRecord::Tempo { time, .. }
                | MtxtRecord::TimeSignature { time, .. }
                | MtxtRecord::Tuning { time, .. }
                | MtxtRecord::Reset { time, .. }
                | MtxtRecord::SysEx { time, .. } => {
                    *time = time.quantize(grid, swing, humanize);
                }
                MtxtRecord::Meta { time, .. } => {
                    if let Some(t) = time {
                        *t = t.quantize(grid, swing, humanize);
                    }
                }
                _ => {}
            }
            new_line
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::util::assert_eq_records;

    #[test]
    fn test_quantize() {
        let input = r#"
mtxt 1.0
1.01 note C4
2.02 note E4
3.99 note G4
"#;
        let expected = r#"
mtxt 1.0
1.0 note C4
2.0 note E4
4.0 note G4
"#;
        assert_eq_records(input, |r| transform(r, 4, 0.0, 0.0), expected);
    }
}
