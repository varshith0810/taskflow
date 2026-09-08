"""Small schema migration helpers for deployments without Alembic."""
from sqlalchemy import Engine, inspect, text
def ensure_user_organization_column(engine: Engine) -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "organization_name" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE users ADD COLUMN organization_name VARCHAR(128) DEFAULT '' NOT NULL"
        ))
