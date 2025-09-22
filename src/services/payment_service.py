from typing import Dict, Optional
from datetime import datetime
import src.dao.payment_dao as payment_dao
import src.dao.order_dao as order_dao

class PaymentError(Exception):
    pass

def pay_order(order_id: int, method: str) -> Dict:
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise PaymentError("Order not found")
    if order["status"] != "PLACED":
        raise PaymentError("Only PLACED orders can be paid")

    # Create payment record
    payment = payment_dao.create_payment(order_id, order["total_amount"], method)
    
    # Mark order as COMPLETED
    order_dao.update_order_status(order_id, "COMPLETED")
    
    return payment

def refund_order(order_id: int) -> Dict:
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise PaymentError("Order not found")
    if order["status"] != "CANCELLED":
        raise PaymentError("Only CANCELLED orders can be refunded")

    payment = payment_dao.mark_payment_refunded(order_id)
    return payment
