"""Add route privacy and acceptance fields to existing scrap requests."""
from sqlalchemy import inspect


def upgrade(engine) -> None:
    columns = {column["name"] for column in inspect(engine).get_columns("scrap_requests")}
    additions = {
        "area_label": "VARCHAR(120)",
        "accepted_by_saleng_id": "INTEGER",
        "accepted_at": "DATETIME",
    }
    missing = [(name, sql_type) for name, sql_type in additions.items() if name not in columns]
    if not missing:
        return
    with engine.begin() as connection:
        for name, sql_type in missing:
            connection.exec_driver_sql(
                f"ALTER TABLE scrap_requests ADD COLUMN {name} {sql_type}"
            )
