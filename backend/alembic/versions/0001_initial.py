"""Initial SVAMITRAI schema."""

from alembic import op

from app.db.base import Base
from app.models import *  # noqa: F401,F403

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS postgis")
    Base.metadata.create_all(bind=bind)
    if bind.dialect.name == "postgresql":
        for table, col, name in [
            ("predictions", "geometry", "ix_predictions_geometry_gist"),
            ("buildings", "geometry", "ix_buildings_geometry_gist"),
            ("roads", "geometry", "ix_roads_geometry_gist"),
            ("water_bodies", "geometry", "ix_water_bodies_geometry_gist"),
            ("vegetation", "geometry", "ix_vegetation_geometry_gist"),
            ("parcels", "geometry", "ix_parcels_geometry_gist"),
        ]:
            bind.exec_driver_sql(f'CREATE INDEX IF NOT EXISTS "{name}" ON "{table}" USING GIST ("{col}")')


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
