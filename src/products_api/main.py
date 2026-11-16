from fastapi import FastAPI, HTTPException, status

from products_api.models import (
    Category,
    NewProduct,
    Product,
    ProductUpdate,
    Summary,
)

app = FastAPI()

products = {
    "P101": {
        "id": "P101",
        "name": "Basmati rice 5kg",
        "price": 2400,
        "category": "rice",
        "in_stock": 40,
    },
    "P102": {
        "id": "P102",
        "name": "Cooking oil 1L",
        "price": 650,
        "category": "oil",
        "in_stock": 0,
    },
    "P103": {
        "id": "P103",
        "name": "Red chilli powder 200g",
        "price": 320,
        "category": "spices",
        "in_stock": 120,
    },
    "P104": {
        "id": "P104",
        "name": "Sella rice 10kg",
        "price": 4600,
        "category": "rice",
        "in_stock": 15,
    },
}

next_id = 105


def find_product(product_id: str):
    product = products.get(product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found",
        )

    return product


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products", response_model=list[Product])
def list_products(
    category: Category | None = None,
    max_price: int | None = None,
    limit: int = 10,
):
    results = list(products.values())

    if category:
        results = [
            product
            for product in results
            if product["category"] == category
        ]

    if max_price is not None:
        results = [
            product
            for product in results
            if product["price"] <= max_price
        ]

    return results[:limit]


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: str):
    return find_product(product_id)


@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: NewProduct):
    global next_id

    product_id = f"P{next_id}"

    new_product = {
        "id": product_id,
        **product.model_dump(),
    }

    products[product_id] = new_product

    next_id += 1

    return new_product


@app.patch("/products/{product_id}", response_model=Product)
def update_product(
    product_id: str,
    updates: ProductUpdate,
):
    product = find_product(product_id)

    for key, value in updates.model_dump(
        exclude_unset=True
    ).items():
        product[key] = value

    return product


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(product_id: str):
    product = find_product(product_id)

    if product["in_stock"] > 0:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot delete {product_id}. "
                f"{product['in_stock']} items still in stock."
            ),
        )

    del products[product_id]


@app.get("/summary", response_model=Summary)
def summary():
    counts = {}

    stock_value = 0

    for product in products.values():
        stock_value += (
            product["price"] * product["in_stock"]
        )

        category = product["category"]

        counts[category] = counts.get(category, 0) + 1

    return {
        "product_count": len(products),
        "stock_value": stock_value,
        "by_category": counts,
    }