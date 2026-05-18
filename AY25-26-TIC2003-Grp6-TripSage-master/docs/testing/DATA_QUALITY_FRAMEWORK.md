# TripSage Data Quality Framework

## Purpose

This framework defines the minimum data quality checks used to validate data across the raw, core, analytics, and gold layers.

## Core Principles

- Validate data as close to the source as possible
- Enforce stronger rules at each downstream layer
- Use simple reconciliation checks for trust and traceability
- Treat failures by severity so critical issues are handled first

## Layer Checks

### Raw Layer

Purpose: confirm the ingestion feed is complete and usable.

Checks:

- Row count check against crawler output or source file count
- Null check on source identifier and URL fields
- Duplicate check on source page or post key
- Freshness check on ingestion timestamp
- Basic format check for HTML/text payload availability

### Core Layer

Purpose: confirm raw data has been cleaned and standardized.

Checks:

- Row count reconciliation from raw to core
- Null check on primary keys and mandatory business fields
- Domain check for fields such as rating, category, and date
- Duplicate check on business keys after deduplication
- Referential check between core entities and core reviews

### Analytics Layer

Purpose: confirm derived metrics are complete and mathematically valid.

Checks:

- Row count check for expected output tables
- Null check on metric columns such as sentiment score or keyword list
- Range check for scores and percentages
- Coverage check to ensure most core records have analytic outputs
- Consistency check between source reviews and derived aggregates

### Gold Layer

Purpose: confirm dashboard-ready outputs are trustworthy and stable.

Checks:

- Row count reconciliation between core/analytics and gold views
- Null check on dashboard critical fields
- Domain check on ranking and score fields
- Aggregate validation for summary views
- Schema contract check for presentation tables

## Simple Rule Set

| Check Type | Example Rule | Severity |
|---|---|---|
| Row count reconciliation | Raw rows should match expected ingest volume; core and gold differences must be explainable | High |
| Null value check | Primary keys, URLs, and required metrics cannot be null | High |
| Duplicate check | One business key should map to one active record | High |
| Domain check | Ratings must stay within valid ranges | Medium |
| Freshness check | New raw data should appear within the expected SLA | Medium |
| Schema check | Required columns must exist in each layer | High |

## Reconciliation Approach

1. Compare source and target row counts after each load.
2. Explain differences caused by filtering, deduplication, or aggregation.
3. Check key metrics such as total reviews, total entities, and summary counts.
4. Flag any mismatch that cannot be traced to a known transformation rule.

## Basic Thresholds

- Raw to core reconciliation: should be close to 100 percent after known exclusions
- Core to analytics reconciliation: should match expected transformation coverage
- Gold view reconciliation: should be fully explainable from core and analytics inputs
- Null checks: critical keys should be 0 percent null

## Failure Handling

- High severity: stop the pipeline or block release until fixed
- Medium severity: log the issue and retry or investigate in the next cycle
- Low severity: monitor and track as a non-blocking issue

## Recommended Checks To Start With

- Row count check
- Null value check
- Duplicate check
- Schema check
- Range/domain check
