from typing import List, Dict, Optional
from src.config import get_supabase

def _sb():
    return get_supabase()

def create_order_row(cust_id: int, total_amount: float) -> Optional[Dict]:
    """Insert order and return inserted row"""
    payload = {"cust_id": cust_id, "total_amount": total_amount, "status": "PLACED"}
    _sb().table("orders").insert(payload).execute()
    # fetch the inserted row by cust_id & status PLACED (latest)
    resp = (
        _sb()
        .table("orders")
        .select("*")
        .eq("cust_id", cust_id)
        .eq("status", "PLACED")
        .order("order_id", desc=True)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None

def add_order_items(order_id: int, items: List[Dict]):
    """
    Insert multiple items into order_items table.
    Each item must include 'prod_id', 'quantity', and 'price'.
    """
    payloads = [
        {
            "order_id": order_id,
            "prod_id": item["prod_id"],
            "quantity": item["quantity"],
            "price": item["price"]  # Make sure price is included
        }
        for item in items
    ]
    _sb().table("order_items").insert(payloads).execute()

def get_order_by_id(order_id: int) -> Optional[Dict]:
    resp = _sb().table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def list_orders_by_customer(cust_id: int) -> List[Dict]:
    resp = _sb().table("orders").select("*").eq("cust_id", cust_id).execute()
    return resp.data or []

def update_order_status(order_id: int, status: str) -> Optional[Dict]:
    _sb().table("orders").update({"status": status}).eq("order_id", order_id).execute()
    return get_order_by_id(order_id)
