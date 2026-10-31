"""Decorators module"""
import os
import time
import uuid
from datetime import datetime
from functools import wraps

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FOLDER = os.path.join(PROJECT_FOLDER, "logs")
LOG_FILE = os.path.join(LOG_FOLDER, "transactions.txt")

THICK = "=" * 50
THIN = "-" * 50


def _write_log(block):
    """Add one finished log entry, followed by a blank line."""
    os.makedirs(LOG_FOLDER, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(block + "\n\n")


def _header(transaction_id, now, status, message):
    """The top part of every entry (same for success and failure)."""
    return [
        THICK,
        f"Transaction ID : {transaction_id}",
        f"Date           : {now:%Y-%m-%d}",
        f"Time           : {now:%H:%M:%S}",
        f"Status         : {status}",
        f"Message        : {message}",
        THIN,
    ]


def log_transaction(func):
    """Record every checkout (success or failure) in a text file."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        transaction_id = uuid.uuid4().hex[:8].upper()
        now = datetime.now()
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
        except Exception as error:
            elapsed = time.perf_counter() - start
            lines = _header(transaction_id, now, "FAILED", str(error))
            lines.append(f"Processing Time: {elapsed:.4f}s")
            lines.append(THICK)
            _write_log("\n".join(lines))
            raise

        elapsed = time.perf_counter() - start

        lines = _header(transaction_id, now, "SUCCESS", "Payment successful.")
        lines.append("Items Bought:")
        for line in result["lines"]:
            lines.append(
                f"  [{line['item_id']}] {line['name']} | "
                f"{line['qty']} x ${line['price']:.2f} = ${line['subtotal']:.2f}"
            )
        lines.append(THIN)

        units = sum(line["qty"] for line in result["lines"])
        lines.append(f"Unique Items   : {len(result['lines'])}")
        lines.append(f"Total Units    : {units}")
        lines.append(f"Subtotal       : ${result['subtotal']:.2f}")
        if result["discount"] > 0:
            lines.append(f"Discount       : -${result['discount']:.2f}")
        lines.append(f"Total (final)  : ${result['total']:.2f}")

        payment = result["payment"]
        lines.append(f"Payment Method : {payment['method']}")
        if "reference" in payment:
            lines.append(f"Reference      : {payment['reference']}")
        if "change" in payment:
            lines.append(f"Change Given   : ${payment['change']:.2f}")

        lines.append(f"Processing Time: {elapsed:.4f}s")
        lines.append(THICK)

        _write_log("\n".join(lines))
        return result

    return wrapper