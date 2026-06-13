# Loader Validation Report

## Scope

This report validates the schema-first refactor of the data layer in `src/data/loader.py` and `src/data/preprocess.py` against the actual MiraiKhoj candidate datasets.

Validated inputs:

- `data/raw/sample_candidates.json`
- `data/raw/candidates.jsonl`
- `data/schema/candidate_schema.json`

## Validation Method

The refactor was checked with:

1. Static syntax validation on the edited Python files.
2. Unit tests covering schema compatibility, nested-field preservation, optional-field handling, and candidate text construction.
3. Full dataset scanning of the sample corpus and the complete JSONL corpus through `validate_candidate_schema`.

## Results

### Unit Tests

- `9` tests executed.
- `9` tests passed.
- `0` failures.
- `0` errors after fixing the test import path bootstrap.

### Sample Dataset Compatibility

- `sample_candidates.json` records checked: `50`
- Valid records: `50`
- Invalid records: `0`

### JSONL Dataset Compatibility

- `candidates.jsonl` records checked: `100000`
- Valid records: `100000`
- Invalid records: `0`

## Final Validation Rules

The loader now validates the actual dataset structure rather than an invented flattened résumé shape. The checks include:

- required top-level objects: `profile`, `career_history`, `education`, `skills`, `certifications`, `languages`, `redrob_signals`
- required nested fields inside each object or list entry
- candidate ID format
- enum-like value constraints for current company size, education tier, skill proficiency, language proficiency, and preferred work mode
- bounded list sizes for the major repeated sections

## Outcome

The refactored data layer is schema-compatible with the real candidate data shipped in the workspace. Both the sample corpus and the full JSONL corpus passed validation without errors.

## Notes

- The only blocker encountered during validation was Python test discovery not adding `src/` to `sys.path`. That was corrected in the test modules.
- No data anomalies were observed in the provided sample or JSONL corpora during the final validation sweep.