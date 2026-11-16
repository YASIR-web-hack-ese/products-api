from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import products_api.main as main_module
from products_api.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_products():
    original_products = deepcopy(main_module.products)
    original_next_id = main_module.next_id
    yield
    main_module.products.clear()
    main_module.products.update(original_products)
    main_module.next_id = original_next_id


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_docs_are_available():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_list_products_returns_seeded_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 4


def test_list_products_filters_by_category():
    response = client.get("/products", params={"category": "rice"})

    assert response.status_code == 200
    assert {product["id"] for product in response.json()} == {"P101", "P104"}


def test_list_products_filters_by_max_price():
    response = client.get("/products", params={"max_price": 650})

    assert response.status_code == 200
    assert {product["id"] for product in response.json()} == {"P102", "P103"}


def test_list_products_respects_limit():
    response = client.get("/products", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_product_returns_product():
    response = client.get("/products/P101")

    assert response.status_code == 200
    assert response.json()["name"] == "Basmati rice 5kg"


def test_get_missing_product_returns_not_found():
    response = client.get("/products/P999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product P999 not found"}


def test_create_product_returns_created_product():
    response = client.post(
        "/products",
        json={
            "name": "Whole wheat flour 1kg",
            "price": 180,
            "category": "flour",
            "in_stock": 25,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": "P105",
        "name": "Whole wheat flour 1kg",
        "price": 180,
        "category": "flour",
        "in_stock": 25,
    }


def test_create_product_rejects_invalid_price():
    response = client.post(
        "/products",
        json={
            "name": "Invalid product",
            "price": 0,
            "category": "rice",
        },
    )

    assert response.status_code == 422


def test_update_product_changes_supplied_fields():
    response = client.patch(
        "/products/P101",
        json={"price": 2500, "in_stock": 35},
    )

    assert response.status_code == 200
    assert response.json()["price"] == 2500
    assert response.json()["in_stock"] == 35
    assert response.json()["name"] == "Basmati rice 5kg"


def test_update_missing_product_returns_not_found():
    response = client.patch("/products/P999", json={"price": 100})

    assert response.status_code == 404


def test_delete_out_of_stock_product_returns_no_content():
    response = client.delete("/products/P102")

    assert response.status_code == 204
    assert client.get("/products/P102").status_code == 404


def test_delete_product_with_stock_returns_conflict():
    response = client.delete("/products/P101")

    assert response.status_code == 409
    assert "40 items still in stock" in response.json()["detail"]


def test_summary_returns_inventory_totals():
    response = client.get("/summary")

    assert response.status_code == 200
    assert response.json() == {
        "product_count": 4,
        "stock_value": 203400,
        "by_category": {"rice": 2, "oil": 1, "spices": 1},
    }
