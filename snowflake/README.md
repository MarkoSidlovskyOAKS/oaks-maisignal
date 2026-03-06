# Snowflake — MAiSIGNAL Data Layer

Snowflake SQL scripts for the MAiSIGNAL data infrastructure.

## Data Layer Architecture

| Layer | Directory | Purpose |
|-------|-----------|---------|
| L0 | `L0/` | Raw source data, no transformations |
| L1 | `L1_filtered/` | Basic filtering, renaming, convention alignment |
| L2 | `L2_joined/` | Joins across tables and codelists |
| L3 | `L3_business/` | Real-world business objects and metrics |
| L4 | `L4_viz/` | Visualization-ready aggregations and outputs |

Currently only L0 is implemented.

## Prerequisites

### Install SnowSQL

```bash
brew install --cask snowflake-snowsql
```

Verify the installation:

```bash
snowsql --version
```

## Setup

### 1. Configure credentials

Copy the template and fill in your Snowflake credentials:

```bash
cp config/.env.example config/.env
```

Edit `config/.env` with your values. This file is gitignored — never commit it.

### 2. Run init scripts

```bash
./run.sh init/
```

This creates the database, schema (`l0`), warehouse (`maisignal_wh`), and service user in order.

**Important:** Edit `init/04_create_user.sql` and replace `<strong_password>` with a secure password before executing.

### 3. Create L0 tables

```bash
./run.sh L0/
```

### 4. Load seed data

```bash
./run.sh seed/
```

## Runner Script

`run.sh` is a SnowSQL wrapper that loads credentials from `config/.env` and executes SQL files.

```bash
# Run a single file
./run.sh L0/uzis_erecept.sql

# Run all files in a directory (sorted order)
./run.sh init/
./run.sh L0/
./run.sh seed/
```

## Tables

### `maisignal.l0.posledni_platne_hlaseni`

SUKL latest valid drug unavailability reports. Source: [SUKL Open Data](https://opendata.sukl.cz/).

| Column | Type | Description |
|--------|------|-------------|
| `kod_sukl` | `NUMBER NOT NULL` | SUKL drug code (primary identifier) |
| `nazev` | `VARCHAR` | Drug name |
| `doplnek` | `VARCHAR` | Drug supplement info |
| `reg` | `VARCHAR` | Registration number |
| `atc` | `VARCHAR` | ATC classification code |
| `typ_oznameni` | `VARCHAR` | Notification type |
| `platnost_od` | `DATE` | Valid from date |
| `datum_hlaseni` | `DATE` | Report date |
| `nahrazujici_lp` | `VARCHAR` | Substitute drug |
| `nahrazujici_lp_poznamka` | `VARCHAR` | Substitute drug note |
| `duvod_preruseni_ukonceni` | `VARCHAR` | Reason for interruption/termination |
| `termin_obnoveni` | `DATE` | Expected recovery date |

### `maisignal.l0.uzis_erecept`

UZIS eRECEPT reimbursement data for prescriber and pharmacy analysis.

| Column | Type | Description |
|--------|------|-------------|
| `icz_nazev_preskribujici` | `VARCHAR` | Prescriber facility name |
| `icz_nazev_vykazujici` | `VARCHAR` | Reporting pharmacy name |
| `lp_naz` | `VARCHAR` | Drug name (e.g. LYRICA, PREGLENIX) |
| `celkova_uhrada_kc` | `NUMBER(12,2)` | Total reimbursement in CZK |
| `atc5` | `VARCHAR` | ATC code with description |
| `kvartal` | `VARCHAR` | Quarter (e.g. Q3) |
| `rok` | `NUMBER` | Year |

### `maisignal.l0.client_portfolio`

Client-to-ATC code mapping for alert targeting.

| Column | Type | Description |
|--------|------|-------------|
| `user_email` | `VARCHAR NOT NULL` | Client email address |
| `company_name` | `VARCHAR NOT NULL` | Company name |
| `atc_portfolio` | `VARCHAR NOT NULL` | ATC code of interest |

### `maisignal.l0.client_brands`

Client-to-brand mapping for alert personalization.

| Column | Type | Description |
|--------|------|-------------|
| `user_email` | `VARCHAR NOT NULL` | Client email address |
| `company_name` | `VARCHAR NOT NULL` | Company name |
| `brand` | `VARCHAR NOT NULL` | Brand name |

### `maisignal.l0.notification_log`

Tracks all email alerts sent by the MAiSIGNAL system.

| Column | Type | Description |
|--------|------|-------------|
| `id` | `NUMBER AUTOINCREMENT` | Auto-generated row ID |
| `user_email` | `VARCHAR NOT NULL` | Recipient email |
| `company_name` | `VARCHAR NOT NULL` | Recipient company |
| `alert_type` | `VARCHAR NOT NULL` | Alert type identifier |
| `subject` | `VARCHAR NOT NULL` | Email subject line |
| `sent_at` | `TIMESTAMP_NTZ` | Timestamp (default: current) |
| `status` | `VARCHAR NOT NULL` | Delivery status |
| `ecomail_response` | `VARCHAR` | Raw API response from Ecomail |

## Linting

```bash
sqlfluff lint .
```

Configuration is in `.sqlfluff` (dialect: `snowflake`).
