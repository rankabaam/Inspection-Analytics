# Inspection Analytics Demo

An independent analytics portfolio example using **fabricated community-facility inspection records**, not workplace inspection data.

This standard-library Python project validates synthetic records, calculates monthly finding rates and follow-up metrics, and generates an offline HTML report plus a summary CSV.

> **Portfolio boundary:** None of the employer's data, checklist wording, internal thresholds, personnel names, procedures, operational findings, or original report layouts are included.

## Quick start

Python 3.10+; no third-party packages.

```bash
python src/quality.py --input sample_data/checks.csv --output output/report.html --summary output/summary.csv
python -m unittest discover -s tests -v
```

[View the sample HTML output](demo/preview.html) (download and open locally).

## Definitions

- **Checks:** number of distinct records in the period
- **Checks with findings:** cases with a positive finding indicator
- **Finding rate:** checks with findings divided by all checks
- **Follow-ups:** cases flagged as follow-up inspections
- **Repeat findings:** follow-ups marked as repeat observations
- **Repeat rate:** repeat findings divided by follow-up checks

The synthetic trends do not establish causality or predict performance of any real-world inspection program.

## Contents

| Path | Description |
|---|---|
| `src/quality.py` | Validated input and calculations |
| `sample_data/checks.csv` | Invented records |
| `demo/preview.html` | Example HTML report |
| `demo/summary.csv` | Example aggregate report |
| `tests/test_quality.py` | Regression tests |

The repository represents generic analytical skills and does not expose workplace systems.