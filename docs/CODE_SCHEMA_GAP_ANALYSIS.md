# Code Schema Gap Analysis

**Project:** MiraiKhoj  
**Tagline:** _Finding Talent Beyond Keywords._  
**Scope:** Review of `src/data/loader.py`, `src/data/preprocess.py`, `src/career/career_analyzer.py`, and `src/behavior/signal_engine.py` against the actual Redrob dataset schema.

## Executive Summary

The current codebase does not yet align with the real dataset structure.

The biggest issue is that the code assumes a flattened résumé-like payload, while the dataset is actually a nested object graph centered on `profile`, structured `career_history`, structured `education`, structured `skills`, optional `certifications`, optional `languages`, and a required `redrob_signals` object.

As a result, the current implementation:

- invents fields that do not exist in the dataset,
- ignores required nested structures,
- flattens structured arrays into strings too early,
- misses all 23 behavioral signal fields,
- and cannot reliably compute career or behavioral scores from the actual data.

## Architecture Mismatch Diagram

```mermaid
flowchart LR
    A[Actual Dataset Schema] --> B[profile]
    A --> C[career_history[]]
    A --> D[education[]]
    A --> E[skills[]]
    A --> F[redrob_signals{}]

    G[Current Loader Assumption] --> H[Flat fields: headline, summary, current_title, current_company]
    I[Current Scorers] --> H
    H --> J[Schema Gap]
    B --> J
    C --> J
    D --> J
    E --> J
    F --> J
```

## 1. `src/data/loader.py`

### Invented Fields

The loader creates or expects these flattened fields at the top level:

- `headline`
- `summary`
- `current_title`
- `current_company`
- `career_history` as a string
- `skills` as a string
- `certifications` as a string
- `candidate_text`
- `raw_record`

### Why These Are Incorrect

In the real schema:

- `headline`, `summary`, `current_title`, and `current_company` live inside `profile`, not at the top level.
- `career_history` is an array of structured objects, not a string.
- `skills` is an array of structured objects with `name`, `proficiency`, `endorsements`, and optional `duration_months`.
- `certifications` is an array of structured objects, not a pipe-delimited string.
- `languages` is a real dataset field but is ignored by the loader.
- `redrob_signals` is a critical nested object but is not loaded into the normalized candidate representation.

### Missing Fields

The loader does not preserve or normalize:

- `profile.anonymized_name`
- `profile.location`
- `profile.country`
- `profile.years_of_experience`
- `profile.current_company_size`
- `profile.current_industry`
- all `career_history` item fields
- all `education` item fields
- all `skills` item fields
- all `languages` item fields
- all `redrob_signals` fields

### Incorrect Assumptions

- `candidate_id` fallback to `row_{line_number}` is unsafe because the schema already defines a strict `CAND_[0-9]{7}` pattern.
- The loader assumes the source may contain `title` or `company` at the top level, but the real source nests those under `profile` and `career_history`.
- The loader assumes string coercion is good enough for career history and skills, but the dataset requires object-level preservation for downstream scoring.

## 2. `src/data/preprocess.py`

### Invented / Over-simplified Behavior

This module only normalizes whitespace and splits on line breaks. That is not enough for the actual dataset.

### Missing Responsibilities

It does not:

- extract structured fields from `profile`, `career_history`, `education`, `skills`, or `redrob_signals`,
- preserve structured array boundaries,
- validate mandatory nested objects,
- or produce a candidate text representation that includes the actual available fields from the dataset.

### Schema Mismatch

The candidate text builder in the current code only references flattened fields like:

- `headline`
- `summary`
- `current_title`
- `current_company`
- `career_history`
- `skills`
- `certifications`

That matches the code’s internal model, not the actual dataset.

## 3. `src/career/career_analyzer.py`

### Invented Fields and Terms

The career analyzer uses or assumes:

- flat `headline`, `summary`, `current_title`, `current_company`
- flattened `career_history`, `skills`, `certifications`
- heuristic role labels such as `ai engineer`, `ml engineer`, `search engineer`, `recommendation engineer`
- heuristic company-quality terms such as `product`, `startup`, `saas`

### Why This Is a Problem

The actual dataset provides structured career history and education, plus a current profile block. The analyzer does not use:

- `profile.years_of_experience`
- `profile.current_company_size`
- `profile.current_industry`
- `career_history[].industry`
- `career_history[].company_size`
- `education[].tier`
- `skills[].proficiency`
- `skills[].endorsements`
- `skills[].duration_months`

### Missing Fields

Important dataset fields ignored by the career analyzer include:

- education prestige / tier
- skill proficiency level
- per-skill endorsement volume
- actual current company size and industry
- candidate location and country
- explicit current years of experience

### Incorrect Assumptions

- It treats natural-language text as the primary source of truth, when the dataset already contains structured fields that should drive scoring.
- It uses a consulting-only penalty based on keywords in text, but the dataset has structured company and industry history that would make this more accurate.
- It does not inspect `career_history` as objects, so it cannot reliably infer career progression across roles.

## 4. `src/behavior/signal_engine.py`

### Invented Fields

The behavioral engine expects these fields:

- `available`
- `immediately_available`
- `response_rate`
- `recruiter_interest`
- `interview_completion`
- `github_activity`
- `recent_activity`
- `linkedin_connection`
- `profile_completeness`
- `location`
- `notice_period_days`

### Why These Are Incorrect

The actual dataset does not expose those names at the top level.
The real behavioral signals live inside `redrob_signals` and are named differently, for example:

- `open_to_work_flag`
- `recruiter_response_rate`
- `avg_response_time_hours`
- `profile_completeness_score`
- `github_activity_score`
- `search_appearance_30d`
- `saved_by_recruiters_30d`
- `interview_completion_rate`
- `offer_acceptance_rate`
- `verified_email`
- `verified_phone`
- `linkedin_connected`
- `willing_to_relocate`
- `preferred_work_mode`

### Missing Fields

The behavioral engine ignores the following real signal groups:

- signup recency
- last active date
- recruiter views received
- applications submitted
- skill assessment scores
- recruiter saves
- search appearances
- verification flags
- offer acceptance history
- explicit preferred work mode

### Incorrect Assumptions

- The code treats `profile_completeness` as a free-form field, but the dataset stores `profile_completeness_score` inside `redrob_signals`.
- The code checks `github_activity`, but the dataset uses `github_activity_score` with `-1` as a missing-data sentinel.
- The code checks `linkedin_connection`, but the dataset uses `linkedin_connected`.
- The code checks `notice_period_days` at the flat level, while the dataset stores it in `redrob_signals`.
- The code invents `recruiter_interest` and `recent_activity`, neither of which exists in the schema.

## Gap Summary Table

| Area | Code Assumption | Actual Dataset | Impact |
| --- | --- | --- | --- |
| Candidate shape | Flat résumé object | Nested profile + arrays + signals | High |
| Career history | Flattened text blob | Array of structured objects | High |
| Skills | Text list | Array of skill objects | High |
| Certifications | Text list | Array of certification objects | Medium |
| Behavioral signals | Loose flat fields | Required `redrob_signals` object with 23 fields | High |
| Location | Flat string and heuristic | `profile.location` plus `preferred_work_mode` / relocation flags | Medium |
| Experience | Derived from text | Explicit numeric field in `profile` | High |
| Profile quality | Heuristic completeness | Structured completeness score and verification flags | High |
| Search/retrieval fit | Keyword heuristics only | Possible from skills, descriptions, and history | Medium |

## Consequences If Unchanged

If the code is run against the real dataset as-is:

- important fields will be silently ignored,
- behavioral scoring will use the wrong signals,
- career scoring will misread structured data as blobs,
- candidate explanations will be based on incomplete evidence,
- and ranking quality will be weaker than the dataset supports.

## Recommended Remediation Order

1. Parse `profile` into a first-class object instead of flattening it.
2. Preserve structured `career_history`, `education`, `skills`, and `redrob_signals` arrays/objects.
3. Update behavioral scoring to consume the actual `redrob_signals` schema.
4. Update career scoring to use structured experience, education tier, and company metadata.
5. Keep candidate text generation as a secondary representation, not the source of truth.

## Current Best-Fit Interpretation

The existing code is best understood as an early proof-of-concept for free-text candidate ranking. It is not yet schema-aligned with the actual Redrob dataset.
