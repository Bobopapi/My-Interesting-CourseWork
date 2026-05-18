# AY25-26-TIC2003-Grp6-TripSage

TripSage is a Japan travel-data pipeline and local dashboard project. The current codebase crawls Japan-Guide and Tabelog content, stores raw and structured data in PostgreSQL, builds parquet layers for analytics, and serves a Reflex-based visualisation app with a SQLite fallback.

## Current Layout

- `src/tripsage/crawlers/`: Japan-Guide, forum, review, and Tabelog crawlers.
- `src/tripsage/db/`: PostgreSQL connection helpers and repository logic.
- `src/tripsage/pipelines/`: crawl, silver, analytics, and end-to-end runners.
- `src/tripsage/analytics/`: parquet analytics and presentation-layer builders.
- `src/tripsage/visualisation/`: Reflex app, app config, styles, and local UI data.
- `sql/`: schema bootstrap, app role setup, ingest procedures, and bronze pull functions.
- `data/raw/`, `data/core/`, `data/analytics/`, `data/presentation/`: generated outputs.
- `e2e/`: Playwright-based pytest checks.
- `requirements.txt`: pinned Python dependencies.

## Setup

Create and activate a virtual environment, then install the pinned dependencies:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If you plan to run the browser tests, install the Playwright binaries after the dependency install:

```powershell
python -m playwright install
```

`nltk` is pinned in `requirements.txt`, but the application source does not import it yet.

## Database Configuration

`src/tripsage/db/connection.py` reads these variables from `.env`:

```env
DB_HOST=localhost
DB_NAME=TripSage
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

The Reflex app also reads the visualisation schema from `src/tripsage/visualisation/rxconfig.py`:

```env
DB_SCHEMA_VISUALISATION=public
```

If any of the Reflex database variables are missing, the app falls back to `sqlite:///tripsage.db`.

## Database Bootstrap

Run the SQL files in this order:

```powershell
psql -h localhost -U postgres -d TripSage -f sql/00_admin_setup.sql
psql -h localhost -U postgres -d TripSage -f sql/10_app_role_and_ingest.sql
psql -h localhost -U postgres -d TripSage -f sql/30_bronze_pull_procs.sql
```

`sql/00_admin_setup.sql` includes `sql/01_setup_schema.sql`, so the schema file does not need to be executed separately unless you are bootstrapping by hand.

## Pipeline

Run the full pipeline from the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m tripsage.pipelines.run_all
```

That executes crawl -> silver -> analytics in sequence.

The analytics layer writes these parquet outputs:

- `data/analytics/review_sentiment.parquet`
- `data/analytics/review_keywords.parquet`
- `data/analytics/entity_metrics.parquet`
- `data/presentation/viz_entities.parquet`
- `data/presentation/viz_reviews.parquet`
- `data/presentation/viz_prefecture_summary.parquet`
- `data/presentation/viz_category_summary.parquet`
- `data/presentation/viz_monthly_review_activity.parquet`
- `data/presentation/viz_keywords_summary.parquet`
- `data/presentation/viz_local_insights.parquet` when forum data is available

## Dashboard

The visualisation app lives in `src/tripsage/visualisation/` and is powered by Reflex.

```powershell
cd src/tripsage/visualisation
reflex db init
reflex run
```

The app prefers PostgreSQL when the `.env` values and `DB_SCHEMA_VISUALISATION` are set. If not, it loads from the local SQLite fallback.

## Tests

Run the E2E suite with:

```powershell
pytest e2e
```

`pytest.ini` already points pytest at the `e2e/` folder.
