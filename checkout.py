"""
Checkout Module

Connects the cart, inventory and logger modules. The @log_transaction
decorator records every checkout attempt to transactions.txt.
"""

from inventory import check_stock, update_stock, calc_price
from logger import log_transaction


@log_transaction()
def checkout(cart, inventory):
    """Process the cart: validate stock, price it, deduct stock, clear the cart.

    Args:
        cart (list): Cart items (dicts with item_id, name, price, quantity).
        inventory (dict): The main inventory data structure.

    Returns:
        tuple: (success: bool, message: str, total: float)
    """
    if not cart:
        return False, "Cart is empty.", 0.0

    # 1. Validate everything first so a failure never leaves a half-processed order
    for item in cart:
        item_id = item.get("item_id")
        if item_id is None or item_id not in inventory:
            return False, f"'{item['name']}' is not in the inventory.", 0.0
        available = check_stock(inventory, item_id)
        if item["quantity"] > available:
            return (
                False,
                f"Not enough stock for '{item['name']}' "
                f"(requested {item['quantity']}, available {available}).",
                0.0,
            )

    # 2. Price the order (discount applies when the subtotal exceeds $20)
    subtotal = sum(item["price"] * item["quantity"] for item in cart)
    total = round(
        sum(calc_price(item["price"], order_total=subtotal) * item["quantity"]
            for item in cart),
        2,
    )

    # 3. Deduct stock
    for item in cart:
        update_stock(inventory, item["item_id"], -item["quantity"])

    # 4. Empty the cart (the logger already snapshotted it)
    cart.clear()
    return True, "Payment successful.", total


if __name__ == "__main__":
    demo_inventory = {
        "101": {"name": "Notebook", "price": 2.50, "stock": 15},
        "102": {"name": "Campus Hoodie", "price": 25.00, "stock": 3},
    }
    demo_cart = [
        {"item_id": "101", "name": "Notebook", "price": 2.50, "quantity": 2},
        {"item_id": "102", "name": "Campus Hoodie", "price": 25.00, "quantity": 1},
    ]
    print(checkout(demo_cart, demo_inventory))
    print(checkout([{"item_id": "102", "name": "Campus Hoodie",
                     "price": 25.00, "quantity": 9}], demo_inventory))
    print(demo_inventory)