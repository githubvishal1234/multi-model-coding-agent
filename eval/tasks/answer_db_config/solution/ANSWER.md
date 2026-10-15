The app gets its database URL from `load_database_url()` in `app/config.py`
(called by `app/db.py:connect`). The `APP_DATABASE_URL` environment variable overrides it;
the default is `sqlite:///data/app.db`. (`app/legacy.py:get_db` is unused by the app.)
