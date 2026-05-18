# TripSage ETL Test Plan

## Purpose

This document defines a simple software test plan for the ETL pipeline across the raw, core, analytics, and gold layers. The focus is on data correctness, completeness, transformation logic, and reconciliation.

## Scope

- Raw layer: crawler output and landing data
- Core layer: cleaned, standardized, and deduplicated data
- Analytics layer: sentiment, keyword, and aggregation outputs
- Gold layer: dashboard-ready views and summaries

## Test Strategy

The tests follow common data engineering principles:

- Validate data at every layer, not only at the end
- Check schema, volume, nullability, and business rules
- Reconcile record counts between source and target where applicable
- Verify transformations are deterministic and repeatable
- Focus on critical paths first, then edge cases

## Test Cases

| ID | Layer | Test Case | Objective | Expected Result |
|---|---|---|---|---|
| ETL-01 | Raw | Source file/page ingestion | Confirm raw data is captured from the crawler without truncation or corruption | Raw records are loaded successfully and match the expected input format |
| ETL-02 | Raw | Raw schema validation | Check required fields such as source id, url, text/html, and scraped timestamp | Required columns exist and data types are valid |
| ETL-03 | Raw | Duplicate raw record check | Ensure the same page/post is not ingested multiple times unintentionally | Duplicate count is zero or within approved tolerance |
| ETL-04 | Core | Cleaning and standardization | Validate parsing, trimming, type conversion, and standard date/rating formatting | Core records are standardized consistently |
| ETL-05 | Core | Deduplication logic | Confirm duplicate entities or reviews are removed based on the defined business key | Only one active record remains per business key |
| ETL-06 | Core | Mandatory field check | Verify no nulls in primary keys and other critical fields | Primary keys and mandatory fields are populated |
| ETL-07 | Core | Source-to-core reconciliation | Compare row counts between raw and core after filtering and deduplication | Count difference is explained and within expected range |
| ETL-08 | Analytics | Metric generation check | Validate sentiment, keyword, and aggregate outputs are produced correctly | Analytics tables are created and populated with expected values |
| ETL-09 | Gold | Gold view completeness | Ensure dashboard-ready views include all expected columns and records | Gold views contain the agreed schema and no missing required fields |
| ETL-10 | Gold | End-to-end reconciliation | Compare core, analytics, and gold counts/aggregates for key entities and reviews | Key totals align or differences are explainable by transformation rules |

## Entry Criteria

- Source data is available
- ETL job runs successfully at least once in the target environment
- Required schemas and tables exist

## Exit Criteria

- All critical tests pass
- Any failed checks have documented root cause and resolution
- Reconciliation differences are understood and accepted

## Notes

- Keep the test set lightweight and repeatable.
- Prioritize row count checks, null checks, schema checks, and deduplication checks before advanced validation.
- Use the same test logic for manual validation and future automation.