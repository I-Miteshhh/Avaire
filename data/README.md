# Avaire Sample Data

This directory contains seed data and utilities for bootstrapping the Avaire MVP database.

## Contents

- `generate_sample_data.py` – deterministic generator that produces JSON/SQL seed files with 120 catalog items, sample users, Style DNA profiles, try-on history, and feedback stubs.
- `catalog_seed.json` – machine-generated catalog dump (120 outfits) organised across Indian wear, Western wear, and fusion categories (generated on demand by the script).
- `users_seed.json` – baseline user accounts without passwords (for analytics/testing only).
- `style_dna_seed.json` – Style DNA profiles keyed by user id.
- `init.sql` – PostgreSQL bootstrap script that creates tables (mirroring SQLAlchemy models) and ingests JSON seed data.
- `sample_images/` – placeholder structure for product and user images (empty by default) to be synced with S3 or local storage.

## Generating Data

```powershell
cd data
python generate_sample_data.py
```

The script regenerates all JSON files and rewrites `init.sql` with the latest deterministic content. It does **not** overwrite any existing images.

## Loading Data into PostgreSQL

With Docker Compose running, execute:

```powershell
psql postgresql://avaire_user:avaire_password@localhost:5432/avaire_db -f data/init.sql
```

This will create the schema and load sample data. The SQL script uses standard PostgreSQL JSON functions, so no extensions are required.

## File Naming Conventions

- Catalog images follow `outfit_<id>.jpg`
- User uploads follow `user_<id>_original.jpg`
- Try-on results follow `tryon_<session_id>.jpg`

In the MVP these live under `storage/` locally. For production, switch the storage backend to S3 and upload referenced assets accordingly.
