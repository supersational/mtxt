use crate::BeatTime;
use crate::types::record::MtxtRecordLine;

pub fn transform(records: &[MtxtRecordLine], offset: f32) -> Vec<MtxtRecordLine> {
    if offset == 0.0 {
        return records.to_vec();
    }

    let abs_offset = offset.abs();
    let beat = abs_offset.floor() as u32;
    let frac = abs_offset.fract();
    let offset_time = BeatTime::from_parts(beat, frac);
    let is_negative = offset < 0.0;

    records
        .iter()
        .filter_map(|line| {
            let mut new_line = line.clone();
            if let Some(time) = new_line.record.time() {
                if is_negative {
                    if time < offset_time {
                        return None;
                    }
                    new_line.record.set_time(time - offset_time);
                } else {
                    new_line.record.set_time(time + offset_time);
                }
            }
            Some(new_line)
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::util::assert_eq_records;

    #[test]
    fn test_offset_positive() {
        let input = r#"
mtxt 1.0
ch=1
1.0 note C4
2.0 note E4
"#;
        let expected = r#"
mtxt 1.0
ch=1
2.5 note C4
3.5 note E4
"#;

        assert_eq_records(input, |r| transform(r, 1.5), expected);
    }

    #[test]
    fn test_offset_negative() {
        let input = r#"
mtxt 1.0
ch=1
2.0 note C4
3.0 note E4
"#;
        let expected = r#"
mtxt 1.0
ch=1
1.5 note C4
2.5 note E4
"#;

        assert_eq_records(input, |r| transform(r, -0.5), expected);
    }

    #[test]
    fn test_offset_negative_remove() {
        let input = r#"
mtxt 1.0
ch=1
1.0 note C4
2.0 note E4
3.0 note G4
"#;
        let expected = r#"
mtxt 1.0
ch=1
0.5 note E4
1.5 note G4
"#;

        assert_eq_records(input, |r| transform(r, -1.5), expected);
    }
}
