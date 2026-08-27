# Requirements Document

## Introduction

This feature is an offline generator that produces a Form 1 Mathematics scheme of work and lesson plans as `.docx` documents from hand-curated structured data files. The curated data files are transcribed once from the existing O Level Mathematics syllabus, the Form 1 Mathematics textbook, and the 2026 academic calendar, and they are the single source of truth for generation. No PDF parsing, no OCR, no network access, and no language-model calls are involved.

The pipeline runs in one direction: curated data files produce a scheme of work document, and the scheme of work then supplies the topics, sub-topics, and objectives used to produce lesson plan documents. Generated content is assembled from deterministic rule-based templates that reuse vocabulary from the sample documents in `assets/sample`, so the same curated input always yields byte-identical output.

Version 1 is hardcoded to Form 1 Mathematics. The curated data schema and generation components are structured so that other subjects and forms can be added later without redesign, but no other subject or form is delivered in this version.

## Glossary

- **Generator**: The complete offline software system delivered by this feature, comprising the Curated_Data_Loader, Data_Validator, Allocation_Engine, Content_Composer, Scheme_Writer, and Lesson_Plan_Writer.
- **Curated_Data_Files**: The set of hand-authored JSON or YAML files in the workspace holding syllabus data, textbook page mapping, and calendar data for Form 1 Mathematics.
- **Syllabus_Data**: The Curated_Data_File describing topics, sub-topics, specific objectives, competencies, and the planned number of periods for each sub-topic.
- **Textbook_Map**: The Curated_Data_File mapping each sub-topic identifier to textbook title and page ranges used as teaching and learning resources.
- **Calendar_Data**: The Curated_Data_File describing the academic year, terms, numbered teaching weeks with start and end dates, holiday periods, examination periods, and the number of Mathematics periods available per week.
- **Curated_Data_Loader**: The Generator component that reads and deserialises the Curated_Data_Files into in-memory records.
- **Data_Validator**: The Generator component that checks Curated_Data_Files against the Curated_Data_Schema and against cross-file consistency rules.
- **Curated_Data_Schema**: The declared structure, field names, field types, and required fields for each Curated_Data_File.
- **Allocation_Engine**: The Generator component that assigns sub-topics and periods to numbered teaching weeks.
- **Allocation_Plan**: The in-memory result produced by the Allocation_Engine, listing for each teaching week the assigned sub-topics, period counts, and specific objectives.
- **Content_Composer**: The Generator component that produces teaching and learning strategies, resources, assessment text, teacher activities, student activities, and consolidation text from rule-based templates.
- **Template_Library**: The fixed set of rule-based text templates and phrase vocabulary derived from the sample documents in `assets/sample`.
- **Scheme_Writer**: The Generator component that renders the Allocation_Plan into a scheme of work `.docx` document.
- **Scheme_Document**: The generated scheme of work `.docx` document.
- **Lesson_Plan_Writer**: The Generator component that renders a single lesson plan `.docx` document.
- **Lesson_Plan_Document**: The generated lesson plan `.docx` document.
- **Teaching_Week**: A numbered week in the Calendar_Data that is available for teaching, meaning the week is not marked as a holiday period and not marked as an examination period.
- **Period_Budget**: The number of Mathematics periods available in a single Teaching_Week, taken from the Calendar_Data.
- **Validation_Error**: A structured message produced by the Data_Validator containing an error code, the offending file path, the offending field path, and a human-readable description.

## Requirements

### Requirement 1: Curated data schema and loading

**User Story:** As a teacher maintaining the generator, I want a documented schema for the curated syllabus, textbook, and calendar files, so that I can transcribe source material once and know exactly what the Generator expects.

#### Acceptance Criteria

1. THE Generator SHALL define a Curated_Data_Schema for Syllabus_Data, Textbook_Map, and Calendar_Data, declaring for each field its name, type, and whether the field is required.
2. THE Syllabus_Data SHALL represent each topic with a unique topic identifier, a topic title, and an ordered list of sub-topics.
3. THE Syllabus_Data SHALL represent each sub-topic with a unique sub-topic identifier, a sub-topic title, an ordered list of specific objectives, at least one competence statement, and a planned period count expressed as a positive integer.
4. THE Textbook_Map SHALL represent each entry with a sub-topic identifier, a textbook title, and a page range expressed as a start page and an end page.
5. THE Calendar_Data SHALL represent the academic year, an ordered list of terms, and for each term an ordered list of numbered weeks with a start date, an end date, and a week classification of teaching, holiday, or examination.
6. THE Calendar_Data SHALL represent the Period_Budget for each week marked as teaching, expressed as a non-negative integer.
7. THE Curated_Data_Loader SHALL read Curated_Data_Files from the local file system in JSON or YAML format.
8. IF a Curated_Data_File is absent from the expected path, THEN THE Curated_Data_Loader SHALL stop generation and emit a Validation_Error naming the expected path.
9. IF a Curated_Data_File contains syntax that the Curated_Data_Loader cannot deserialise, THEN THE Curated_Data_Loader SHALL stop generation and emit a Validation_Error naming the file path and the reported parse position.

### Requirement 2: Curated data validation

**User Story:** As a teacher maintaining the generator, I want the Generator to check my curated data before producing documents, so that mistakes in transcription surface as clear errors instead of silently wrong schemes.

#### Acceptance Criteria

1. WHEN the Data_Validator runs, THE Data_Validator SHALL check every Curated_Data_File against the Curated_Data_Schema before the Allocation_Engine starts.
2. IF a required field declared in the Curated_Data_Schema is missing, THEN THE Data_Validator SHALL emit a Validation_Error naming the file path and the field path.
3. IF a field value has a type other than the type declared in the Curated_Data_Schema, THEN THE Data_Validator SHALL emit a Validation_Error naming the file path, the field path, the declared type, and the received type.
4. IF two topics or two sub-topics in the Syllabus_Data share the same identifier, THEN THE Data_Validator SHALL emit a Validation_Error naming both occurrences.
5. IF a sub-topic in the Syllabus_Data has no matching entry in the Textbook_Map, THEN THE Data_Validator SHALL emit a Validation_Error naming the sub-topic identifier.
6. IF a Textbook_Map entry references a sub-topic identifier that is absent from the Syllabus_Data, THEN THE Data_Validator SHALL emit a Validation_Error naming the sub-topic identifier.
7. IF the sum of planned period counts across all sub-topics in the Syllabus_Data exceeds the sum of Period_Budget values across all Teaching_Weeks in the Calendar_Data, THEN THE Data_Validator SHALL emit a Validation_Error stating the total planned period count and the total available period count.
8. IF a week in the Calendar_Data has an end date earlier than the start date of the same week, THEN THE Data_Validator SHALL emit a Validation_Error naming the term and the week number.
9. IF a Textbook_Map entry has an end page lower than the start page of the same entry, THEN THE Data_Validator SHALL emit a Validation_Error naming the sub-topic identifier.
10. WHEN the Data_Validator finds one or more Validation_Errors, THE Data_Validator SHALL report every Validation_Error found in a single run and stop generation without writing any output document.
11. WHEN the Data_Validator finds no Validation_Error, THE Generator SHALL proceed to allocation.

### Requirement 3: Week-to-topic allocation

**User Story:** As a teacher, I want sub-topics spread across the teaching weeks of the academic calendar, so that the scheme of work respects holidays, examination periods, and the periods available each week.

#### Acceptance Criteria

1. THE Allocation_Engine SHALL assign sub-topics to Teaching_Weeks in the order the sub-topics appear in the Syllabus_Data.
2. THE Allocation_Engine SHALL exclude weeks classified as holiday and weeks classified as examination from sub-topic assignment.
3. THE Allocation_Engine SHALL limit the total periods assigned to a single Teaching_Week to the Period_Budget declared for that Teaching_Week in the Calendar_Data.
4. WHERE a sub-topic has a planned period count greater than the remaining periods of the current Teaching_Week, THE Allocation_Engine SHALL split the sub-topic across consecutive Teaching_Weeks and record the period count assigned in each of those Teaching_Weeks.
5. WHEN a Teaching_Week has remaining periods after a sub-topic is fully assigned, THE Allocation_Engine SHALL assign the next sub-topic in order to the remaining periods of that same Teaching_Week.
6. THE Allocation_Engine SHALL record, for each assignment, the week number, the term, the topic identifier, the sub-topic identifier, the assigned period count, and the specific objectives taken from the Syllabus_Data.
7. IF sub-topics remain unassigned after all Teaching_Weeks reach their Period_Budget, THEN THE Allocation_Engine SHALL stop generation and emit a Validation_Error listing the unassigned sub-topic identifiers.
8. WHEN the Allocation_Engine receives identical Syllabus_Data and Calendar_Data, THE Allocation_Engine SHALL produce an identical Allocation_Plan.

### Requirement 4: Scheme of work document generation

**User Story:** As a teacher, I want a scheme of work .docx that matches the layout of my existing sample, so that I can submit it without reformatting.

#### Acceptance Criteria

1. WHEN the Scheme_Writer runs on a valid Allocation_Plan, THE Scheme_Writer SHALL write a Scheme_Document in `.docx` format to the configured output path.
2. THE Scheme_Document SHALL contain a table with the columns Week, Periods, Topic/Sub-topic, Specific Objectives, Teaching/Learning Strategies, Teaching/Learning Resources, Assessment, and Remarks, in that left-to-right order.
3. THE Scheme_Document SHALL contain one table row for each assignment recorded in the Allocation_Plan, ordered by term and then by week number ascending.
4. THE Scheme_Document SHALL populate the Week cell with the week number and the Periods cell with the period count assigned to that row.
5. THE Scheme_Document SHALL populate the Topic/Sub-topic cell with the topic title and the sub-topic title taken from the Syllabus_Data.
6. THE Scheme_Document SHALL populate the Specific Objectives cell with the specific objectives recorded for that assignment in the Allocation_Plan.
7. THE Scheme_Document SHALL populate the Teaching/Learning Resources cell with the textbook title and page range taken from the Textbook_Map for the assigned sub-topic.
8. THE Scheme_Document SHALL populate the Teaching/Learning Strategies and Assessment cells with text produced by the Content_Composer for the assigned sub-topic.
9. THE Scheme_Document SHALL populate the Remarks cell as empty for the teacher to complete by hand.
10. THE Scheme_Document SHALL contain a heading section stating the subject as Mathematics, the class as Form 1, and the academic year taken from the Calendar_Data.
11. IF the configured output path is not writable, THEN THE Scheme_Writer SHALL stop generation and report the output path and the reported file system error.

### Requirement 5: Lesson plan document generation

**User Story:** As a teacher, I want a lesson plan .docx for a chosen week and period that carries the objectives from the scheme of work, so that the plan and the scheme stay aligned.

#### Acceptance Criteria

1. WHEN the Lesson_Plan_Writer receives a week number and a period number that exist in the Allocation_Plan, THE Lesson_Plan_Writer SHALL write a Lesson_Plan_Document in `.docx` format to the configured output path.
2. THE Lesson_Plan_Document SHALL contain the fields Date, Subject, Class, Period, Topic/Sub-topic, Competence, Objectives, Teacher Activities, Student Activities, Assessment, and Consolidation.
3. THE Lesson_Plan_Writer SHALL populate the Topic/Sub-topic field and the Objectives field from the Allocation_Plan entry for the requested week number and period number.
4. THE Lesson_Plan_Writer SHALL populate the Competence field from the competence statement declared for the assigned sub-topic in the Syllabus_Data.
5. THE Lesson_Plan_Writer SHALL populate the Date field from the start date of the requested Teaching_Week in the Calendar_Data offset by the requested period number within that week.
6. THE Lesson_Plan_Writer SHALL populate the Subject field with Mathematics and the Class field with Form 1.
7. THE Lesson_Plan_Writer SHALL populate the Teacher Activities, Student Activities, Assessment, and Consolidation fields with text produced by the Content_Composer for the assigned sub-topic and its objectives.
8. IF the requested week number is absent from the Allocation_Plan, THEN THE Lesson_Plan_Writer SHALL stop generation and report the requested week number and the range of week numbers present in the Allocation_Plan.
9. IF the requested period number exceeds the period count assigned to the requested week in the Allocation_Plan, THEN THE Lesson_Plan_Writer SHALL stop generation and report the requested period number and the assigned period count for that week.
10. WHERE the caller requests lesson plans for an entire Teaching_Week, THE Lesson_Plan_Writer SHALL write one Lesson_Plan_Document for each period assigned to that Teaching_Week in the Allocation_Plan.

### Requirement 6: Rule-based content composition

**User Story:** As a teacher, I want generated activity and assessment wording that reads like my existing documents, so that the output needs little editing.

#### Acceptance Criteria

1. THE Content_Composer SHALL select text from the Template_Library using the topic identifier, the sub-topic identifier, and the specific objectives as selection keys.
2. THE Template_Library SHALL draw its phrase vocabulary from the sample scheme of work and sample lesson plan stored under `assets/sample`.
3. THE Content_Composer SHALL produce text using only the Template_Library and the Curated_Data_Files as input sources.
4. WHEN the Content_Composer receives identical selection keys, THE Content_Composer SHALL return identical text.
5. IF the Template_Library holds no template matching a selection key, THEN THE Content_Composer SHALL apply the declared default template for the requested field and record the substitution in the generation report.

### Requirement 7: Determinism and offline operation

**User Story:** As a teacher, I want generation to run entirely on my machine and produce the same result every time, so that I can trust and re-run it without surprises.

#### Acceptance Criteria

1. WHEN the Generator runs twice on identical Curated_Data_Files with identical command arguments, THE Generator SHALL produce output documents with identical content.
2. THE Generator SHALL read input only from the local file system.
3. THE Generator SHALL complete generation without issuing network requests.
4. THE Generator SHALL complete generation without invoking a language model service and without requiring an API key.
5. THE Generator SHALL derive every date in output documents from the Calendar_Data rather than from the system clock.
6. THE Generator SHALL order every generated list, table row, and document sequence by an explicit key declared in the Curated_Data_Files.

### Requirement 8: Correction and regeneration path

**User Story:** As a teacher, I want a clear way to fix wrong output, so that I can either correct the source data and regenerate or edit the finished document by hand.

#### Acceptance Criteria

1. WHEN the Generator runs after a Curated_Data_File is edited, THE Generator SHALL produce output documents reflecting the edited Curated_Data_File without requiring changes to Generator source code.
2. THE Generator SHALL write output documents to a configured output directory that is separate from the directory holding the Curated_Data_Files.
3. WHERE an output document already exists at the target path, THE Generator SHALL overwrite the existing document only when the caller supplies the overwrite option, and otherwise stop and report the existing path.
4. THE Generator SHALL produce Scheme_Document and Lesson_Plan_Document files that open in a word processor with editable text and editable table cells.
5. WHEN generation completes, THE Generator SHALL write a generation report listing each output path, the count of table rows or lesson plans written, and each default template substitution recorded by the Content_Composer.

### Requirement 9: Extension boundary for later subjects and forms

**User Story:** As a maintainer, I want Form 1 Mathematics to be data rather than hardcoded logic wherever practical, so that adding another subject or form later does not require a rewrite.

#### Acceptance Criteria

1. THE Curated_Data_Schema SHALL declare subject and form as fields of the Syllabus_Data rather than as fixed values in Generator source code.
2. THE Generator SHALL accept the paths of the Curated_Data_Files as command arguments.
3. THE Allocation_Engine SHALL operate on Syllabus_Data and Calendar_Data records without referencing the subject value or the form value.
4. THE Generator SHALL support Form 1 Mathematics as the only delivered subject and form combination in this version.
