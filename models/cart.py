"""Cart Module"""
from utils.logger import log_transaction

class ShoppingCart:
    """The customer's cart"""

    DISCOUNT_THRESHOLD = 20
    DISCOUNT_RATE = 0.10

    def __init__(self):
        self._lines = {}

    def add_item(self, item, quantity):
        """Adds items to cart"""
        if quantity <= 0:
            raise ValueError("Qunatity must be at least 1")

        current_cart = 0
        if item.item_id in self._lines:
            current_cart = self._lines[item.item_id][1]

        new_quantity = current_cart + quantity
        if new_quantity > item.stock:
            raise ValueError (
                f"Only {item.stock} {item.name}(s) available"
                f"You already have {current_cart} in your cart"
            )
        self._lines[item.item_id] = (item, new_quantity)

    def remove_item(self, item_id, quantity=None):
        """Removes items from cart"""
        if item_id not in self._lines:
            raise ValueError("This item is not in your cart")

        item, current = self._lines[item_id]

        if quantity is None:
            del self._lines[item_id]
            return

        if quantity <= 0:
            raise ValueError("Quantity must be at least 1")

        if quantity > current:
            raise ValueError (
                f" You only have {current} {item.name}(s) in your cart"
            )

        if quantity == current:
            del self._lines[item_id]
        else:
            self._lines[item_id] = (item, current - quantity)

    def view_cart(self):
        """Displays cart"""
        result = []
        for item, quantity in self._lines.values():
            result.append(
                {
                    "item_id": item.item_id,
                    "name": item.name,
                    "price": item.price,
                    "qty": quantity,
                    "subtotal": round(item.price * quantity, 2),
                }
            )
        return result

    def is_empty(self):
        """Checks if the cart is empty"""
        return not self._lines

    def remove_unavailable(self):
        """Drop items that can no longer be sold. Returns their names."""
        removed = []
        for item_id, (item, _) in list(self._lines.items()):
            try:
                item.check_sellable()
            except ValueError:
                removed.append(item.name)
                del self._lines[item_id]
        return removed

    def subtotal(self):
        """Price before discount"""
        return round(sum(line["subtotal"] for line in self.view_cart()), 2)

    def discount(self):
        """Adds discount"""
        sub = self.subtotal()
        if sub > self.DISCOUNT_THRESHOLD:
            return round(sub * self.DISCOUNT_RATE, 2)
        return 0.0

    def calculate_total(self):
        """Price after discount."""
        return round(self.subtotal() - self.discount(), 2)

    @log_transaction
    def checkout(self, payment):
        """Check stock, take payment, then reduce stock."""
        if not self._lines:
            raise ValueError("Your cart is empty")


        for item, quantity in self._lines.values():
            item.check_sellable()
            if quantity > item.stock:
                raise ValueError(
                    f"Not enough stock for {item.name}. Only {item.stock} left"
                )


        total = self.calculate_total()
        payment_result = payment.process_payment(total)


        summary = {
            "lines": self.view_cart(),
            "subtotal": self.subtotal(),
            "discount": self.discount(),
            "total": total,
            "payment": payment_result,
        }
        for item, quantity in self._lines.values():
            item.reduce_stock(quantity)

        self._lines.clear()
        return summary
