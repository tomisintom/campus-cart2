"""
Logger Module

Provides a decorator that records transaction details to a text file
at the point of checkout in Campus Cart.
"""

import copy
import functools
import uuid
from datetime import datetime

DEFAULT_LOG_FILE = "transactions.txt"
LINE_WIDTH = 60


def _compute_subtotal(cart):
    """Sum price * quantity for every item in a cart snapshot."""
    return sum(item["price"] * item["quantity"] for item in cart)


def _format_entry(txn_id, now, cart, subtotal, total, status, message, duration):
    """Build the text block written to the log file for one transaction."""
    lines = [
        "=" * LINE_WIDTH,
        f"Transaction ID : {txn_id}",
        f"Date           : {now.strftime('%Y-%m-%d')}",
        f"Time           : {now.strftime('%H:%M:%S')}",
        f"Status         : {status}",
        f"Message        : {message}",
        "-" * LINE_WIDTH,
        "Items Bought:",
    ]

    if cart:
        for item in cart:
            line_total = item["price"] * item["quantity"]
            item_id = item.get("item_id") or "N/A"
            lines.append(
                f"  [{item_id}] {item['name']} | "
                f"{item['quantity']} x ${item['price']:.2f} = ${line_total:.2f}"
            )
    else:
        lines.append("  (cart was empty)")

    total_text = f"${total:.2f}" if isinstance(total, (int, float)) else "N/A"
    units = sum(item["quantity"] for item in cart)

    lines += [
        "-" * LINE_WIDTH,
        f"Unique Items   : {len(cart)}",
        f"Total Units    : {units}",
        f"Subtotal       : ${subtotal:.2f}",
        f"Total (final)  : {total_text}",
        f"Processing Time: {duration:.4f}s",
        "=" * LINE_WIDTH,
        "",
    ]
    return "\n".join(lines)


def _write_entry(log_file, entry):
    """Append an entry to the log file (created if it doesn't exist)."""
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


def log_transaction(log_file=DEFAULT_LOG_FILE):
    """Decorator factory: logs every call of a checkout function to a txt file.

    Args:
        log_file (str): Path of the log file. Defaults to 'transactions.txt'.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Locate the cart and snapshot it BEFORE checkout can modify/clear it
            cart = kwargs.get("cart", args[0] if args else [])
            cart_snapshot = copy.deepcopy(cart)
            subtotal = _compute_subtotal(cart_snapshot)

            txn_id = uuid.uuid4().hex[:8].upper()
            start = datetime.now()
            total = None

            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                duration = (datetime.now() - start).total_seconds()
                entry = _format_entry(
                    txn_id, start, cart_snapshot, subtotal, None, "ERROR",
                    f"{type(exc).__name__}: {exc}", duration,
                )
                _write_entry(log_file, entry)
                raise  # let the app handle the failure as usual

            duration = (datetime.now() - start).total_seconds()

            # Unpack (success, message[, total])
            success, message = result[0], result[1]
            if len(result) > 2:
                total = result[2]

            status = "SUCCESS" if success else "FAILED"
            entry = _format_entry(
                txn_id, start, cart_snapshot, subtotal, total, status,
                message, duration,
            )
            _write_entry(log_file, entry)
            return result

        return wrapper

    return decorator


if __name__ == "__main__":
    # Demo: simulate checkouts and write them to a test log file
    demo_log = "demo_transactions.txt"

    @log_transaction(log_file=demo_log)
    def checkout(cart, inventory):
        subtotal = _compute_subtotal(cart)
        if not cart:
            return False, "Cart is empty.", 0.0
        discount = 0.10 if subtotal > 20 else 0.0
        total = round(subtotal * (1 - discount) * 1.075, 2)
        cart.clear()  # checkout empties the cart; the log still keeps the items
        return True, "Payment successful.", total

    sample_cart = [
        {"item_id": "101", "name": "Notebook", "price": 2.50, "quantity": 3},
        {"item_id": "102", "name": "Campus Hoodie", "price": 25.00, "quantity": 1},
    ]
    print(checkout(sample_cart, inventory={}))
    print(checkout([], inventory={}))
    print(f"\nLog written to {demo_log}:\n")
    with open(demo_log, encoding="utf-8") as f:
        print(f.read())