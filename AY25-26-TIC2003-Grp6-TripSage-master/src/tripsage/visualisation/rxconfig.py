import os
import reflex as rx

_db_user = os.getenv("DB_USER")
_db_password = os.getenv("DB_PASSWORD")
_db_host = os.getenv("DB_HOST")
_db_port = os.getenv("DB_PORT")
_db_name = os.getenv("DB_NAME")
_db_schema = os.getenv("DB_SCHEMA_VISUALISATION")

if all([_db_user, _db_password, _db_host, _db_port, _db_name, _db_schema]):
    db_url = (
        f"postgresql://{_db_user}:{_db_password}"
        f"@{_db_host}:{_db_port}/{_db_name}"
        f"?options=-csearch_path%3D{_db_schema}"
    )
else:
    db_url = "sqlite:///tripsage.db"

config = rx.Config(
    app_name="tripsage",
    db_url=db_url,
    plugins=[
        rx.plugins.SitemapPlugin(),
    ],
)