# GCP Deployment
Production topology: Cloud Run API, Cloud Run worker/job, Cloud SQL PostgreSQL/PostGIS, Cloud Storage, Pub/Sub, Artifact Registry, Secret Manager and Cloud Logging. Large orthophotos should go directly to GCS using signed URLs where practical.
Never commit credentials, service-account JSON, passwords or JWT secrets.
