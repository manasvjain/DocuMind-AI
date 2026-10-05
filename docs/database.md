# Database
Production target: PostgreSQL + PostGIS. SQLite is used for local tests.
Tables: users, projects, imagery, processing_jobs, model_versions, predictions, buildings, roads, water_bodies, vegetation, parcels, roof_predictions, audit_logs.
PostgreSQL uses native geometry when GeoAlchemy2 is available; SQLite uses JSON-compatible geometries.
