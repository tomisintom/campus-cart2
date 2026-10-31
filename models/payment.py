"""Payment module"""


class Payment:
    """Payment Class"""

    method_name = "Payment"

    def process_payment(self, amount):
        """Process Payment"""
        raise NotImplementedError("Each payment method must define this")

    def _check_amount(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")


class CashPayment(Payment):
    """Pay with cash, and get change back."""

    method_name = "Cash"

    def __init__(self, amount_given):
        self.amount_given = amount_given

    def process_payment(self, amount):
        self._check_amount(amount)
        if self.amount_given < amount:
            raise ValueError(
                f"Not enough cash. Total is {amount:.2f}, "
                f"you gave {self.amount_given:.2f}"
            )
        return {
            "status": "paid",
            "method": self.method_name,
            "amount": amount,
            "change": round(self.amount_given - amount, 2),
        }


class CardPayment(Payment):
    """Pay with a card."""

    method_name = "Card"

    def __init__(self, card_number):
        self.card_number = card_number

    def process_payment(self, amount):
        self._check_amount(amount)
        digits = self.card_number.replace(" ", "")
        if not digits.isdigit() or len(digits) != 16:
            raise ValueError("Card number must be 16 digits")
        return {
            "status": "paid",
            "method": self.method_name,
            "amount": amount,
            "reference": "CARD-" + digits[-4:],
        }


class MobileMoneyPayment(Payment):
    """Pay with mobile money."""

    method_name = "Mobile Money"

    def __init__(self, phone_number):
        self.phone_number = phone_number

    def process_payment(self, amount):
        self._check_amount(amount)
        phone = self.phone_number.replace(" ", "")
        if not phone.isdigit() or len(phone) != 11:
            raise ValueError("Phone number must be 11 digits")
        return {
            "status": "paid",
            "method": self.method_name,
            "amount": amount,
            "reference": "MM-" + phone[-4:],
        }
