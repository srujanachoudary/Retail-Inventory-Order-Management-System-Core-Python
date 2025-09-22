from typing import Optional, Dict
from src.config import get_supabase

def _sb():
    return get_supabase()

def create_payment(order_id: int, amount: float) -> Optional[Dict]:
    payload = {"order_id": order_id, "amount": amount, "status": "PENDING"}
    _sb().table("payments").insert(payload).execute()
    resp = _sb().table("payments").select("*").eq("order_id", order_id).eq("status", "PENDING").order("payment_id", desc=True).limit(1).execute()
    return resp.data[0] if resp.data else None

def update_payment(payment_id: int, fields: Dict) -> Optional[Dict]:
    _sb().table("payments").update(fields).eq("payment_id", payment_id).execute()
    resp = _sb().table("payments").select("*").eq("payment_id", payment_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def get_payment_by_order(order_id: int) -> Optional[Dict]:
    resp = _sb().table("payments").select("*").eq("order_id", order_id).order("payment_id", desc=True).limit(1).execute()
    return resp.data[0] if resp.data else None
