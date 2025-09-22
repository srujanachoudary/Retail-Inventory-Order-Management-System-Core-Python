from typing import List, Dict
import src.dao.product_dao as product_dao
import src.dao.customer_dao as customer_dao
import src.dao.order_dao as order_dao

class OrderError(Exception):
    pass

def create_order(customer_id: int, items: List[Dict]) -> Dict:
    # 1. Check customer exists
    customer = customer_dao.get_customer_by_id(customer_id)
    if not customer:
        raise OrderError("Customer not found")

    # 2. Prepare items with price and calculate total
    total_amount = 0
    items_with_price = []
    for item in items:
        prod = product_dao.get_product_by_id(item["prod_id"])
        if not prod:
            raise OrderError(f"Product {item['prod_id']} not found")
        if (prod.get("stock") or 0) < item["quantity"]:
            raise OrderError(f"Not enough stock for product {prod['name']}")
        item_with_price = {
            "prod_id": item["prod_id"],
            "quantity": item["quantity"],
            "price": prod["price"]
        }
        items_with_price.append(item_with_price)
        total_amount += prod["price"] * item["quantity"]

    # 3. Deduct stock
    for item in items_with_price:
        prod = product_dao.get_product_by_id(item["prod_id"])
        new_stock = prod["stock"] - item["quantity"]
        product_dao.update_product(prod["prod_id"], {"stock": new_stock})

    # 4. Insert order
    order_row = order_dao.create_order_row(customer_id, total_amount)
    order_id = order_row["order_id"]

    # 5. Insert order items
    order_dao.add_order_items(order_id, items_with_price)

    return get_order_details(order_id)

def get_order_details(order_id: int) -> Dict:
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise OrderError("Order not found")

    customer = customer_dao.get_customer_by_id(order["cust_id"])
    items = _get_order_items(order_id)
    return {
        "order": order,
        "customer": customer,
        "items": items
    }

def _get_order_items(order_id: int) -> List[Dict]:
    resp = order_dao._sb().table("order_items").select("*").eq("order_id", order_id).execute()
    data = resp.data or []
    for d in data:
        prod = product_dao.get_product_by_id(d["prod_id"])
        d["product_name"] = prod["name"] if prod else "Unknown"
        d["price"] = prod["price"] if prod else 0
    return data

def cancel_order(order_id: int) -> Dict:
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise OrderError("Order not found")
    if order["status"] != "PLACED":
        raise OrderError("Only orders with status PLACED can be cancelled")

    # Restore stock
    items = _get_order_items(order_id)
    for item in items:
        prod = product_dao.get_product_by_id(item["prod_id"])
        product_dao.update_product(prod["prod_id"], {"stock": prod["stock"] + item["quantity"]})

    return order_dao.update_order_status(order_id, "CANCELLED")
