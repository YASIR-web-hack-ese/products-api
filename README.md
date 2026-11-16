# Products API

A small FastAPI service for managing an in-memory product catalogue.

## Setup

This project uses Python 3.15 and `uv`.

```powershell
uv sync
```

## Run the API

```powershell
uv run fastapi dev src/products_api/main.py
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `/docs`.

## Test

```powershell
uv run pytest
```

The suite contains 15 tests covering health, documentation, product listing and filtering, lookup, creation, updates, deletion, validation, and summary totals.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/products` | List products; supports `category`, `max_price`, and `limit` |
| GET | `/products/{product_id}` | Get one product |
| POST | `/products` | Create a product |
| PATCH | `/products/{product_id}` | Update supplied product fields |
| DELETE | `/products/{product_id}` | Delete an out-of-stock product |
| GET | `/summary` | Get inventory totals by category |

## Bruno collection

The request collection is in [`bruno/products-api`](./bruno/products-api). Open it in Bruno and select the `local` environment, which uses `http://127.0.0.1:8000`.

## Project layout

```text
src/products_api/
  main.py       # FastAPI application and routes
  models.py     # Pydantic request and response models
tests/
  test_main.py  # API tests
bruno/
  products-api/ # Bruno requests and local environment
```
