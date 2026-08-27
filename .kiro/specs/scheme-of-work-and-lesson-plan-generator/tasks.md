# Implementation Plan: Scheme of Work and Lesson Plan Generator

## Overview

Build the `sowgen` package in Python 3.11 following the pipeline order in the design: scaffolding and pinned dependencies, then the schema models, loader and validator, then the allocation engine pinned by its property tests before any `.docx` code exists, then the template library and composer, then the two writers on shared atomic-write helpers, then the CLI, pipeline orchestration and generation report, then the whole-pipeline determinism and offline properties, and finally the curated Form 1 Mathematics data files and shipped template YAML transcribed from `assets/`.

Every component returns `ValidationError` values rather than raising for input-caused failures, so aggregate single-run reporting works end to end. All 30 correctness properties from the design are covered by a property-test sub-task naming its property number.

## Tasks

- [ ] 1. Project scaffolding and error vocabulary
  - [ ] 1.1 Create the project skeleton with exactly pinned dependencies
    - Write `pyproject.toml` declaring `python-docx==1.1.2`, `pydantic==2.9.2`, `PyYAML==6.0.2`, dev extras `pytest==8.3.3` and `hypothesis==6.112.1`, and the console script `sowgen = sowgen.cli:main`
    - Create the `src/sowgen/` package tree with `__init__.py` files for `schema/`, `templates/`, `render/`, and the `tests/{unit,properties,fixtures}/` directories with `conftest.py`
    - Add `.gitignore` entries for `out/` and `__pycache__/`, and configure pytest for `src` layout plus the committed Hypothesis database at `tests/.hypothesis/`
    - Include no HTTP client, no cloud SDK, and no language-model SDK in the manifest
    - _Requirements: 7.3, 7.4_

  - [ ] 1.2 Implement `errors.py` with the full error-code vocabulary
    - Define frozen `ValidationError` with `code`, `file_path`, `field_path`, `message`, `details`, and `sort_key()` returning `(file_path or "", field_path or "", code)`
    - Define `Severity` and a constant for each code in the design's error-code table, from `FILE_NOT_FOUND` through `OUTPUT_INSIDE_DATA_DIR`
    - Implement the multi-error report renderer producing the `[CODE] path / field: ... / message` block format, sorted by `sort_key()`
    - _Requirements: 2.2, 2.3, 2.10_

  - [ ]* 1.3 Write unit tests for error rendering and ordering
    - Assert report ordering is stable for errors differing only in code, field path, or file path
    - Assert rendered blocks include file path, field path, and message for field-scoped errors and omit them for non-file-scoped errors
    - _Requirements: 2.10_

- [ ] 2. Curated_Data_Schema models
  - [ ] 2.1 Implement `schema/syllabus.py`
    - Frozen pydantic models `SyllabusData`, `Topic`, `SubTopic`, `Objective` with the fields, required flags, and constraints declared in the design, including the identifier pattern, `order >= 1`, `planned_periods >= 1`, non-empty `competences`, and the optional `template_hint`
    - Declare `subject` and `form` as required data fields on `SyllabusData`, plus required `schema_version` and optional `source_note`
    - _Requirements: 1.1, 1.2, 1.3, 9.1_

  - [ ] 2.2 Implement `schema/textbook.py`
    - Frozen `TextbookMap` and `TextbookEntry` with `sub_topic_id`, `book_title`, `start_page >= 1`, `end_page >= 1`, optional `note`, and required `schema_version`
    - _Requirements: 1.1, 1.4_

  - [ ] 2.3 Implement `schema/calendar.py`
    - Frozen `CalendarData`, `Term`, `Week`, and the `WeekClassification` enum with values `teaching`, `holiday`, `examination`
    - Enforce `period_budget` required and `>= 0` for teaching weeks and absent-or-zero otherwise, ISO date parsing to `datetime.date`, and the optional `period_days` list of non-negative day offsets
    - _Requirements: 1.1, 1.5, 1.6_

  - [ ] 2.4 Implement `schema/describe.py`
    - `describe_schema(model)` walking a pydantic model depth-first and returning `FieldSpec(path, declared_type, required, constraints)` for every field, including nested models and list element types
    - _Requirements: 1.1_

  - [ ]* 2.5 Write unit tests for the schema declaration surface
    - Assert every required field of all three models appears in `describe_schema` output with the correct declared type and required flag
    - Assert the declaration includes the classification enum domain and the period-count constraints
    - _Requirements: 1.1_

- [ ] 3. Curated_Data_Loader
  - [ ] 3.1 Implement file reading, format dispatch, and pydantic-error translation in `loader.py`
    - `CuratedDataLoader.load(paths) -> LoadResult`, never raising for bad input: missing path yields `FILE_NOT_FOUND` naming the expected path, unknown extension yields `UNSUPPORTED_FORMAT`, `.json` via `json.loads` and `.yaml`/`.yml` via `yaml.safe_load`
    - Translate `json.JSONDecodeError` and `yaml.MarkedYAMLError` into `PARSE_ERROR` carrying line and column
    - Translate each entry of `pydantic.ValidationError.errors()` into one `ValidationError`: `missing` to `MISSING_REQUIRED_FIELD`, `*_type` to `TYPE_MISMATCH` with declared and received type, everything else to `CONSTRAINT_VIOLATION`, with `loc` rendered as a dotted and indexed field path
    - Attempt all three files even when an earlier one fails, and expose `load_from_documents(mapping)` so tests can drive the loader from in-memory objects
    - _Requirements: 1.7, 1.8, 1.9, 2.2, 2.3, 2.10, 7.2_

  - [ ] 3.2 Build `CuratedDataSet` with its derived indexes
    - Assemble `sub_topics_in_order` sorted by `(topic.order, sub_topic.order)`, `teaching_weeks_in_order` sorted by `(term.order, week_number)`, plus `sub_topic_by_id`, `textbook_by_sub_topic`, `week_by_number`, and the `SubTopicRef`/`WeekRef`/`DataPaths` records
    - Sort objectives by `order` so no index depends on physical file order
    - _Requirements: 1.2, 1.5, 7.6_

  - [ ]* 3.3 Build the Hypothesis strategies in `tests/strategies.py`
    - `valid_syllabus()`, `valid_calendar()`, `matched_dataset()`, `oversubscribed_dataset()`, and the `defect_injectors()` family described in the design's Testing Strategy, with unique identifiers, densely assigned `order` keys shuffled in the serialised form, and Unicode-bearing titles and objectives
    - Provide helpers to serialise a generated dataset to both JSON and YAML text
    - _Requirements: 1.7_

  - [ ]* 3.4 Write property test for load round trip across both encodings
    - **Property 1: Load round trip preserves records across both encodings**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.7**

  - [ ]* 3.5 Write property test for schema violation reporting
    - **Property 2: Every schema violation is reported at its field path with both types**
    - **Validates: Requirements 1.3, 1.6, 2.3**

  - [ ]* 3.6 Write property test for deleted required fields
    - **Property 3: Every deleted required field is reported at its field path**
    - **Validates: Requirement 2.2**

  - [ ]* 3.7 Write loader edge-case unit tests
    - Malformed JSON and malformed YAML fixtures asserting the reported parse line and column, a missing file asserting the expected path, and a `.txt` input asserting `UNSUPPORTED_FORMAT`
    - Assert one run reports errors originating in more than one file
    - _Requirements: 1.7, 1.8, 1.9, 2.10_

- [ ] 4. Data_Validator
  - [ ] 4.1 Implement all cross-file and range rules in `validator.py`
    - `DataValidator.validate(data)` running each rule independently and returning every error sorted: duplicate topic and sub-topic identifiers naming both field paths, referential integrity in both directions over sorted identifier sets, capacity arithmetic carrying `planned_total` and `available_total`, inverted week dates, inverted page ranges, `period_days` length/monotonicity/in-week feasibility, the default-date-rule week-length check, and non-zero `period_budget` on holiday or examination weeks
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_

  - [ ]* 4.2 Write property test for duplicate identifier reporting
    - **Property 4: Duplicate identifiers are reported with both occurrences**
    - **Validates: Requirement 2.4**

  - [ ]* 4.3 Write property test for bidirectional referential integrity
    - **Property 5: Referential integrity between Syllabus_Data and Textbook_Map holds in both directions**
    - **Validates: Requirements 2.5, 2.6**

  - [ ]* 4.4 Write property test for capacity checking
    - **Property 6: Capacity errors appear exactly when planned periods exceed available periods, and report both totals**
    - **Validates: Requirement 2.7**

  - [ ]* 4.5 Write property test for inverted range reporting
    - **Property 7: Inverted ranges are reported with their locators**
    - **Validates: Requirements 2.8, 2.9**

- [ ] 5. Allocation_Engine
  - [ ] 5.1 Implement the allocation records in `allocation.py`
    - Frozen `Assignment`, `WeekAllocation`, `AllocationPlan` with the fields declared in the design, plus `assignment_for(week_number, period_number)` resolving through `first_period <= n <= last_period` and `all_assignments()` yielding `(term_order, week_number, slot)` ascending
    - Return `WEEK_NOT_IN_PLAN` and `PERIOD_NOT_IN_WEEK` bounds information from the resolver rather than raising
    - _Requirements: 3.6, 5.8, 5.9_

  - [ ] 5.2 Implement the packing loop and finalisation pass
    - Greedy single-pass sequential packing over `sub_topics_in_order` and `teaching_weeks_in_order` with splitting, `take = min(remaining, capacity_left(week))`, a week cursor that never decreases, zero-budget teaching weeks skipped transparently, and `split_total` stamped on every part once known
    - Emit `UNASSIGNED_SUB_TOPICS` listing the current sub-topic and every sub-topic still queued, with total unplaced periods, when weeks run out
    - Finalisation groups drafts by week, assigns `slot` in insertion order, computes `first_period`/`last_period` from a running cursor, and resolves `period_dates` from `period_days` or the `start_date + (n - 1) days` default
    - Read only order, budget, and date fields; never read `subject` or `form`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 9.3_

  - [ ]* 5.3 Write property test for syllabus ordering of assignments
    - **Property 9: Assignments follow Syllabus_Data order**
    - **Validates: Requirement 3.1**

  - [ ]* 5.4 Write property test for teaching-week-only assignment
    - **Property 10: Only Teaching_Weeks receive assignments**
    - **Validates: Requirement 3.2**

  - [ ]* 5.5 Write property test for period budget respect
    - **Property 11: No week exceeds its Period_Budget**
    - **Validates: Requirement 3.3**

  - [ ]* 5.6 Write property test for period conservation and consecutive splits
    - **Property 12: Periods are conserved and splits are consecutive**
    - **Validates: Requirement 3.4**

  - [ ]* 5.7 Write property test for tight packing
    - **Property 13: Weeks are packed tightly before the next week is used**
    - **Validates: Requirement 3.5**

  - [ ]* 5.8 Write property test for assignment completeness
    - **Property 14: Every assignment is fully populated from the source data**
    - **Validates: Requirement 3.6**

  - [ ]* 5.9 Write property test for over-subscribed input
    - **Property 15: Over-subscribed input yields an error listing exactly the unassignable sub-topics**
    - **Validates: Requirement 3.7**

  - [ ]* 5.10 Write property test for allocation determinism
    - **Property 16: Allocation is deterministic**
    - **Validates: Requirement 3.8**

  - [ ]* 5.11 Write property test for subject and form independence
    - **Property 17: Allocation ignores subject and form**
    - **Validates: Requirement 9.3**

  - [ ]* 5.12 Write allocation edge-case unit tests
    - Zero-budget teaching weeks, single-period sub-topics, a sub-topic requiring more periods than a whole term provides, and allocation called without the validator in front of it
    - _Requirements: 3.2, 3.4, 3.7_

- [ ] 6. Checkpoint - allocation is fully pinned before any .docx code
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Template_Library and Content_Composer
  - [ ] 7.1 Implement `templates/library.py`
    - `TemplateLibrary.load(directory)` reading one YAML file per composed field with `field`, `default`, `by_topic`, `by_sub_topic`, `by_objective_verb`, and the shared `vocabulary.yaml`, returning `ValidationError`s naming the template file path and offending key for malformed files
    - Validate at load time that every placeholder used falls inside the closed set `topic_title`, `sub_topic_title`, `book_title`, `start_page`, `end_page`, `periods`, `objective_list`, `first_objective`, `competence`, `week_number`, `part_of`
    - `resolve(field, keys)` applying the selection order sub-topic hint, sub-topic id, topic id, leading objective verb, default, and reporting whether the default was used
    - _Requirements: 6.1, 6.2, 6.5_

  - [ ] 7.2 Implement `templates/composer.py`
    - `ContentComposer.compose(field, assignment, textbook)` rendering via `str.format_map` over the closed placeholder mapping, collapsing whitespace runs and stripping so block scalars do not leak line breaks into table cells
    - Derive the objective verb key from the first verb of the first objective in declared order, and append exactly one `TemplateSubstitution(field, keys_tried, resolved="default")` when the default branch is taken
    - Keep composition a pure function of `(field, keys, data)` with the substitution list as append-only bookkeeping that does not affect returned text
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

  - [ ]* 7.3 Write property test for template selection specificity and fallback recording
    - **Property 23: Template selection prefers the most specific key and records default fallbacks**
    - **Validates: Requirements 6.1, 6.5**

  - [ ]* 7.4 Write property test for composition determinism
    - **Property 24: Composition is deterministic**
    - **Validates: Requirement 6.4**

- [ ] 8. Document writers, shared docx helpers, and the generation report
  - [ ] 8.1 Implement `render/docx_util.py`
    - `atomic_write(document, target, overwrite)`: refuse with `OUTPUT_EXISTS` when the target exists without overwrite, create parent directories, write to a sibling temp file, normalise, then `os.replace`, mapping any `OSError` to `OUTPUT_NOT_WRITABLE` with the path and OS message and removing the temp file
    - `normalise_docx(path)` rewriting the archive with entries in sorted name order, every `ZipInfo.date_time` set to `(1980, 1, 1, 0, 0, 0)`, fixed `create_system` and fixed deflate level
    - Fixed core properties (`created`, `modified`, `last_modified_by`, `revision`), plus cell and paragraph helpers used by both writers
    - Expose a pre-check that verifies every target path in a multi-document run before the first write
    - _Requirements: 4.11, 7.1, 8.3_

  - [ ] 8.2 Implement `render/scheme_layout.py`
    - The eight column labels in fixed left-to-right order, fixed column widths in EMU, `Table Grid` style, bold repeat-on-each-page header row, landscape A4 page setup, and 9pt body text, all as constants with no auto-fit
    - _Requirements: 4.2_

  - [ ] 8.3 Implement `render/scheme_writer.py`
    - Heading block with `SCHEME OF WORK`, subject and class, and academic year taken from the plan, plus the term week ranges
    - One body row per assignment from `plan.all_assignments()`, populating Week (with `{term_title} W{n}` on the first row of each term), Periods, Topic/Sub-topic with the split part suffix, numbered Specific Objectives in declared order, composed Strategies, resources from `Textbook_Map` as `{book_title}, pages {start}-{end}` plus the resources template line, composed Assessment, and an empty Remarks cell
    - Write through `atomic_write`, returning a `WriteResult` carrying the path and row count
    - _Requirements: 4.1, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 8.2_

  - [ ] 8.4 Implement `render/lesson_layout.py`
    - The eleven field labels from the design's lesson plan table, the two-column label/value header table geometry, the labelled prose sections, and the `DD/MM/YYYY` date format
    - _Requirements: 5.2_

  - [ ] 8.5 Implement `render/lesson_writer.py`
    - `write_one` validating the request before any rendering: unknown week yields `WEEK_NOT_IN_PLAN` with the plan's min and max week numbers, out-of-range period yields `PERIOD_NOT_IN_WEEK` with the requested period and the week's assigned count
    - Populate Date from `week.period_dates[period - 1]`, Subject and Class from the plan, Topic/Sub-topic and numbered Objectives from the resolved assignment, Competence as a bulleted list of the sub-topic's competences, and composed Teacher Activities, Student Activities, Assessment, and Consolidation
    - `write_week` resolving the week once then writing exactly `periods_assigned` documents named `lesson-plan-w{week:02d}-p{period}.docx`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_

  - [ ] 8.6 Implement `report.py`
    - `GenerationReport` with `generated_from`, `academic_year`, `subject`, `form`, `outputs`, `template_substitutions` sorted by `(field, sub_topic_id)`, and `ReportTotals` for rows, lesson plans, weeks used and periods allocated
    - Serialise to `generation-report.json` with no timestamp field, and render the short stdout summary
    - _Requirements: 6.5, 7.1, 8.5_

  - [ ]* 8.7 Write property test for scheme row fidelity
    - **Property 18: Every scheme row reproduces its source assignment**
    - **Validates: Requirements 4.1, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9**

  - [ ]* 8.8 Write property test for scheme row count and order
    - **Property 19: Scheme rows match the plan in count and order**
    - **Validates: Requirement 4.3**

  - [ ]* 8.9 Write property test for lesson plan fidelity
    - **Property 20: Every valid week and period request produces a lesson plan faithful to its assignment**
    - **Validates: Requirements 5.1, 5.3, 5.4, 5.5, 5.6, 5.7**

  - [ ]* 8.10 Write property test for lesson plan request bounds
    - **Property 21: Lesson plan requests succeed exactly when the week and period exist, and errors name the valid bounds**
    - **Validates: Requirements 5.8, 5.9**

  - [ ]* 8.11 Write property test for whole-week lesson plan requests
    - **Property 22: A whole-week request writes one document per assigned period**
    - **Validates: Requirement 5.10**

  - [ ]* 8.12 Write property test for generation report accuracy
    - **Property 30: The generation report matches what was written**
    - **Validates: Requirement 8.5**

  - [ ]* 8.13 Write document structure unit and editability tests
    - Assert the fixed scheme column header order, the lesson plan field labels, and the heading block contents
    - Reopen generated files with `python-docx` and assert table cells expose editable text runs with no document protection element
    - Assert an unwritable output path reports the path and the OS error
    - _Requirements: 4.2, 4.10, 4.11, 5.2, 8.4_

- [ ] 9. Checkpoint - documents render correctly from a plan
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. CLI and pipeline orchestration
  - [ ] 10.1 Implement `pipeline.py`
    - Orchestrate load, validate, allocate, compose, write, report, calling the allocator only when validation returns no errors and constructing no writer until allocation succeeds
    - Copy `subject`, `form`, and `academic_year` into the plan from the data rather than from the engine, and aggregate loader, validator, allocator and writer errors into one sorted report
    - _Requirements: 2.1, 2.10, 2.11, 8.1, 8.5_

  - [ ] 10.2 Implement `cli.py`
    - `argparse` subcommands `validate`, `scheme`, `lesson`, `all`, `schema` with the flags in the design, curated data paths always explicit arguments, `--templates` defaulting to the packaged directory, and `--scheme-name` defaulting to a pure function of subject, form and academic year
    - Reject an output directory that equals, contains, or is contained by any curated data file directory with `OUTPUT_INSIDE_DATA_DIR`
    - Exit codes 0 success, 1 unexpected internal error with traceback, 2 validation or request errors, 3 output conflict or write failure
    - _Requirements: 1.1, 8.2, 8.3, 9.2, 9.4_

  - [ ]* 10.3 Write CLI and pipeline ordering unit tests
    - Assert argument parsing for every subcommand, the derived default scheme filename, the output-directory overlap rejection, and each exit code
    - Assert the validator runs before the allocator and that no writer is constructed when validation fails
    - _Requirements: 2.1, 8.2, 9.2_

  - [ ]* 10.4 Write property test for aggregate reporting with no output written
    - **Property 8: All injected defects are reported in one run and no document is written**
    - **Validates: Requirements 2.1, 2.10**

- [ ] 11. Whole-pipeline determinism and offline guarantees
  - [ ]* 11.1 Write property test for repeated-run identity
    - **Property 25: Repeated runs produce identical documents**
    - **Validates: Requirement 7.1**

  - [ ]* 11.2 Write property test for clock independence
    - **Property 26: Output is independent of the system clock**
    - **Validates: Requirement 7.5**

  - [ ]* 11.3 Write property test for physical record order independence
    - **Property 27: Output is independent of physical record order in the input files**
    - **Validates: Requirement 7.6**

  - [ ]* 11.4 Write property test for edited data flowing through
    - **Property 28: Edited data flows through to output without code changes**
    - **Validates: Requirement 8.1**

  - [ ]* 11.5 Write property test for overwrite behaviour
    - **Property 29: Existing output is replaced only with the overwrite option**
    - **Validates: Requirement 8.3**

  - [ ]* 11.6 Write offline and clock-usage smoke tests
    - Run the full pipeline with `socket.socket` patched to raise and assert success
    - Assert the dependency manifest contains no HTTP client, cloud SDK, or language-model SDK and requires no API key
    - Scan the `src/sowgen` tree and assert `date.today`, `datetime.now`, and `time.time` appear nowhere
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

- [ ] 12. Curated Form 1 Mathematics dataset and shipped templates
  - [ ] 12.1 Transcribe `data/form1-mathematics/syllabus.json`
    - Author the full Form 1 Mathematics topic and sub-topic structure from `assets/syllabus/MATHEMATICS SYLLABUS - O Level Final.pdf` with `subject`, `form`, `schema_version`, dense `order` keys, unique identifiers, specific objectives, at least one competence per sub-topic, and `planned_periods` totalling no more than the calendar budget
    - Record provenance in `source_note`
    - _Requirements: 1.2, 1.3, 9.1, 9.4_

  - [ ] 12.2 Transcribe `data/form1-mathematics/textbook_map.json`
    - One entry per sub-topic identifier in the syllabus, with book title and page range read from `assets/textbook/MATHEMATICS F1 New - WazaElimu.com.pdf`, exercise references in `note`
    - _Requirements: 1.4, 2.5, 2.6_

  - [ ] 12.3 Transcribe `data/form1-mathematics/calendar.json`
    - Academic year, terms, and numbered weeks with start and end dates and classifications read from `assets/calendar/calendar 2026.png`, with `period_budget` on every teaching week and `period_days` where the Mathematics periods are not on consecutive days
    - _Requirements: 1.5, 1.6, 7.5_

  - [ ] 12.4 Author the shipped `templates/` YAML files
    - One file per composed field plus `vocabulary.yaml`, with phrasing transcribed from `assets/sample/schemeOfWork/SCHEME-MATH F1 2026 - W.docx` and `assets/sample/lessonPlan/MATHEMATICS LESSON FI (1).docx`, keeping their verbs and wording
    - Provide a declared default for every field, topic and sub-topic overrides for the shipped syllabus, objective-verb entries for the common verbs, and a `source:` provenance comment at the head of each file
    - _Requirements: 6.1, 6.2, 6.5_

  - [ ]* 12.5 Write an integration test over the shipped dataset
    - Assert `sowgen validate` reports no error on the shipped data files, then generate the scheme and a full week of lesson plans into `tmp_path` and assert the row count matches the assignment count and the report matches the files on disk
    - _Requirements: 2.11, 4.1, 5.10, 8.5, 9.4_

- [ ] 13. Final checkpoint - full pipeline on real data
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Property 8 lands with the pipeline rather than the validator because its "no document is written" clause needs the write stage to exist; Properties 1 - 7 fully pin the loader and validator on their own
- Allocation properties 9 - 17 all complete before task 8 begins, so the packing algorithm is pinned before any `.docx` code exists
- Property tests run at `max_examples=100` minimum, and the allocation properties at 300 as the design specifies
- Writers are always pointed at `tmp_path` in tests; nothing under `data/` or `out/` is written by the test suite
- Nothing in `src/` reads `assets/`; those files are human source material for tasks 12.1 - 12.4

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["2.1", "2.2", "2.3", "1.3"] },
    { "id": 3, "tasks": ["2.4", "3.1"] },
    { "id": 4, "tasks": ["3.2", "2.5"] },
    { "id": 5, "tasks": ["4.1", "3.3"] },
    { "id": 6, "tasks": ["5.1", "3.4", "3.5", "3.6", "3.7"] },
    { "id": 7, "tasks": ["5.2", "4.2", "4.3", "4.4", "4.5"] },
    { "id": 8, "tasks": ["7.1", "8.1", "8.2", "8.4", "5.3", "5.4", "5.5", "5.6", "5.7", "5.8", "5.9", "5.10", "5.11", "5.12"] },
    { "id": 9, "tasks": ["7.2", "8.3", "8.5", "8.6"] },
    { "id": 10, "tasks": ["10.1", "7.3", "7.4", "8.7", "8.8", "8.9", "8.10", "8.11", "8.12", "8.13"] },
    { "id": 11, "tasks": ["10.2"] },
    { "id": 12, "tasks": ["12.1", "12.2", "12.3", "12.4", "10.3", "10.4"] },
    { "id": 13, "tasks": ["11.1", "11.2", "11.3", "11.4", "11.5", "11.6"] },
    { "id": 14, "tasks": ["12.5"] }
  ]
}
```
