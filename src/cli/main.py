import argparse
import json
from src.services import product_service, customer_service,order_service
from src.dao import product_dao, customer_dao, order_dao 

# ------------------- Product Commands -------------------

def cmd_product_add(args):
    try:
        p = product_service.add_product(args.name, args.sku, args.price, args.stock, args.category)
        print("Created product:")
        print(json.dumps(p, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_product_list(args):
    ps = product_dao.list_products(limit=100)
    print(json.dumps(ps, indent=2, default=str))

# ------------------- Customer Commands -------------------

def cmd_customer_add(args):
    try:
        c = customer_service.add_customer(args.name, args.email, args.phone, args.city)
        print("Created customer:")
        print(json.dumps(c, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_update(args):
    try:
        updated = customer_service.update_customer(args.id, phone=args.phone, city=args.city)
        print("Updated customer:")
        print(json.dumps(updated, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_delete(args):
    try:
        deleted = customer_service.delete_customer(args.id)
        print("Deleted customer:")
        print(json.dumps(deleted, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_list(args):
    try:
        customers = customer_dao.list_customers(limit=100)
        print(json.dumps(customers, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_customer_search(args):
    try:
        results = customer_dao.search_customers(email=args.email, city=args.city)
        print(json.dumps(results, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

# ------------------- Order Commands ------------------

def cmd_order_create(args):
    items = []
    for item in args.item:
        try:
            pid, qty = item.split(":")
            items.append({"prod_id": int(pid), "quantity": int(qty)})
        except Exception:
            print("Invalid item format:", item)
            return
    try:
        ord = order_service.create_order(args.customer, items)
        print("Order created:")
        print(json.dumps(ord, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_show(args):
    try:
        o = order_service.get_order_details(args.order)
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)

def cmd_order_cancel(args):
    try:
        o = order_service.cancel_order(args.order)
        print("Order cancelled (updated):")
        print(json.dumps(o, indent=2, default=str))
    except Exception as e:
        print("Error:", e)
def cmd_payment_pay(args):
    from src.services import payment_service
    try:
        result = payment_service.pay(args.order, args.method)
        print("Payment processed:")
        print(result)
    except Exception as e:
        print("Error:", e)

def cmd_payment_refund(args):
    from src.services import payment_service
    try:
        result = payment_service.refund(args.order)
        print("Payment refunded:")
        print(result)
    except Exception as e:
        print("Error:", e)


# ------------------- Parser -------------------

def build_parser():
    parser = argparse.ArgumentParser(prog="retail-cli")
    sub = parser.add_subparsers(dest="cmd")

    # ---- Product ----
    p_prod = sub.add_parser("product", help="product commands")
    pprod_sub = p_prod.add_subparsers(dest="action")

    addp = pprod_sub.add_parser("add")
    addp.add_argument("--name", required=True)
    addp.add_argument("--sku", required=True)
    addp.add_argument("--price", type=float, required=True)
    addp.add_argument("--stock", type=int, default=0)
    addp.add_argument("--category", default=None)
    addp.set_defaults(func=cmd_product_add)

    listp = pprod_sub.add_parser("list")
    listp.set_defaults(func=cmd_product_list)

    # ---- Customer ----
    pcust = sub.add_parser("customer", help="customer commands")
    pcust_sub = pcust.add_subparsers(dest="action")

    # add
    addc = pcust_sub.add_parser("add")
    addc.add_argument("--name", required=True)
    addc.add_argument("--email", required=True)
    addc.add_argument("--phone", required=True)
    addc.add_argument("--city", default=None)
    addc.set_defaults(func=cmd_customer_add)

    # update
    updatec = pcust_sub.add_parser("update")
    updatec.add_argument("--id", type=int, required=True)
    updatec.add_argument("--phone", default=None)
    updatec.add_argument("--city", default=None)
    updatec.set_defaults(func=cmd_customer_update)

    # delete
    delc = pcust_sub.add_parser("delete")
    delc.add_argument("--id", type=int, required=True)
    delc.set_defaults(func=cmd_customer_delete)

    # list
    listc = pcust_sub.add_parser("list")
    listc.set_defaults(func=cmd_customer_list)

    # search
    searchc = pcust_sub.add_parser("search")
    searchc.add_argument("--email", default=None)
    searchc.add_argument("--city", default=None)
    searchc.set_defaults(func=cmd_customer_search)

    # ---- Order (Commented) ----
    porder = sub.add_parser("order", help="order commands")
    porder_sub = porder.add_subparsers(dest="action")

    createo = porder_sub.add_parser("create")
    createo.add_argument("--customer", type=int, required=True)
    createo.add_argument("--item", required=True, nargs="+", help="prod_id:qty (repeatable)")
    createo.set_defaults(func=cmd_order_create)
    #show
    showo = porder_sub.add_parser("show")
    showo.add_argument("--order", type=int, required=True)
    showo.set_defaults(func=cmd_order_show)
    #cancel
    cano = porder_sub.add_parser("cancel")
    cano.add_argument("--order", type=int, required=True)
    cano.set_defaults(func=cmd_order_cancel)
    # ---- Payment ----
    ppay = sub.add_parser("payment", help="payment commands")
    ppay_sub = ppay.add_subparsers(dest="action")

    # pay command
    pay_cmd = ppay_sub.add_parser("pay")
    pay_cmd.add_argument("--order", type=int, required=True)
    pay_cmd.add_argument("--method", type=str, required=True, choices=["Cash", "Card", "UPI"])
    pay_cmd.set_defaults(func=cmd_payment_pay)

    # refund command
    refund_cmd = ppay_sub.add_parser("refund")
    refund_cmd.add_argument("--order", type=int, required=True)
    refund_cmd.set_defaults(func=cmd_payment_refund)

    return parser

# ------------------- Main -------------------

def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
