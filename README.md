# AEGIS Apparel

AEGIS is a split frontend/backend storefront with a FastAPI API and a React 19 frontend.

## Local setup

Backend:

```bash
cd backend
cp .env.example .env  # if present
pip install -r requirements.txt
uvicorn server:app --reload
```

Frontend:

```bash
cd frontend
yarn install
yarn start
```

## Environment

- `MONGO_URL`
- `DB_NAME`
- `REACT_APP_BACKEND_URL`
- `CORS_ORIGINS`
- `SENTRY_DSN`
- `SENTRY_ENVIRONMENT`
- `SENTRY_RELEASE`
- `SENTRY_TRACES_SAMPLE_RATE`

For frontend source-map upload or release automation, keep the Sentry auth token in CI as `SENTRY_AUTH_TOKEN` along with `SENTRY_ORG` and `SENTRY_PROJECT`.

## Notes

- The storefront UI is public, but order entry can be kept hidden until launch.
- Backend tests expect the API to be reachable via `REACT_APP_BACKEND_URL`.
