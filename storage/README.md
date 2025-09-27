# Avaire Storage Layer

This directory holds generated assets for the virtual try-on pipeline and catalog placeholders.

## Layout

```
storage/
├── catalog/         # Product imagery referenced by seed data
├── uploads/         # Raw user uploads (per session)
└── results/         # Synthesized try-on renders
```

## Configuration

The backend uses a unified storage client (`backend/services/storage.py`) that supports:

- **Local mode** (default): files are written under this folder and exposed via `/storage/**`.
- **S3 mode**: set `STORAGE_BACKEND=s3` plus the following environment variables:
  - `S3_BUCKET_NAME`
  - `AWS_REGION` (or `AWS_DEFAULT_REGION`)
  - `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
  - Optional `STORAGE_PUBLIC_URL` for CDN domain (otherwise a public S3 URL is used).

When S3 mode is enabled the service writes to disk first (for ML processing) and then uploads to S3 with `public-read` ACL so the frontend can access the asset immediately.

## Sample Assets

During development drop placeholder images under `storage/catalog/` and the `frontend/public/images/` folder. The data generator references filenames like `outfit_001.jpg` and `hero-fusion.jpg`.
