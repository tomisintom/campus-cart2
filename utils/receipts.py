"""Receipt module"""


def stream_receipt_lines(summary):
    """Yield the receipt one line at a time.
    """
    yield "=" * 50
    yield "YOUR RECEIPT"
    yield "-" * 50

    for line in summary["lines"]:
        yield f"{line['name']:<22} x{line['qty']:<4} ${line['subtotal']:>8.2f}"

    yield "-" * 50
    yield f"{'Subtotal:':<28} ${summary['subtotal']:>8.2f}"

    if summary["discount"] > 0:
        yield f"{'Discount (10%):':<28} -${summary['discount']:>7.2f}"

    yield f"{'TOTAL:':<28} ${summary['total']:>8.2f}"
    yield "=" * 50
    yield "Thank you for your patronage. See you again!"

def cart_table(cart):
    """Return the cart as an ASCII table (text). It does not print."""
    if cart.is_empty():
        return "Your cart is empty. Please add items from the catalogue."

    border = "+" + "-" * 8 + "+" + "-" * 26 + "+" + "-" * 10 + "+" + "-" * 14 + "+"

    rows = [
        "YOUR SHOPPING CART",
        border,
        f"| {'ID':<6} | {'PRODUCT':<24} | {'QTY':>8} | {'SUBTOTAL':>12} |",
        border,
    ]

    for line in cart.view_cart():
        subtotal = f"${line['subtotal']:.2f}"
        rows.append(
            f"| {line['item_id']:<6} | {line['name'][:24]:<24} "
            f"| {line['qty']:>8} | {subtotal:>12} |"
        )

    rows.append(border)

    def total_row(label, amount):
        return f"| {'':<6} | {'':<24} | {label:>8} | {amount:>12} |"

    rows.append(total_row("SUBTOTAL", f"${cart.subtotal():.2f}"))
    if cart.discount() > 0:
        rows.append(total_row("DISCOUNT", f"-${cart.discount():.2f}"))
    rows.append(total_row("TOTAL", f"${cart.calculate_total():.2f}"))
    rows.append(border)

    return "\n".join(rows)
