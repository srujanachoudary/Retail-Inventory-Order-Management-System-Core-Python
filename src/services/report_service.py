from src.dao import order_dao, product_dao, customer_dao
from datetime import datetime, timedelta
def top_selling_products(limit: int = 5):
    resp = product_dao._sb().table("order_items")\
        .select("prod_id, sum(quantity) as total_qty")\
        .group("prod_id")\
        .order("total_qty", desc=True)\
        .limit(limit)\
        .execute()
    data = resp.data or []
    for d in data:
        prod = product_dao.get_product_by_id(d["prod_id"])
        d["product_name"] = prod["name"] if prod else "Unknown"
    return data

def total_revenue_last_month():
    now = datetime.utcnow()
    start = datetime(now.year, now.month-1, 1)
    end = datetime(now.year, now.month, 1)
    resp = order_dao._sb().table("orders")\
        .select("sum(total_amount)")\
        .eq("status", "COMPLETED")\
        .gte("order_date", start.isoformat())\
        .lt("order_date", end.isoformat())\
        .execute()
    return resp.data[0]["sum"] if resp.data else 0

def orders_per_customer():
    resp = order_dao._sb().table("orders")\
        .select("cust_id, count(order_id) as total_orders")\
        .group("cust_id")\
        .execute()
    data = resp.data or []
    for d in data:
        cust = customer_dao.get_customer_by_id(d["cust_id"])
        d["customer_name"] = cust["name"] if cust else "Unknown"
    return data

def customers_more_than_n_orders(n: int = 2):
    resp = order_dao._sb().table("orders")\
        .select("cust_id, count(order_id) as total_orders")\
        .group("cust_id")\
        .having("count(order_id)", ">", n)\
        .execute()
    data = resp.data or []
    for d in data:
        cust = customer_dao.get_customer_by_id(d["cust_id"])
        d["customer_name"] = cust["name"] if cust else "Unknown"
    return data
