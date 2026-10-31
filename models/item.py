"""Item Module"""
from datetime import date

class Item:
    """Item Class"""
    def __init__ (self, item_id, name, price, stock):
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        self.item_id = item_id
        self.name = name
        self._price = price
        self._stock = stock


    @property
    def price(self):
        """Price function"""
        return self._price

    @price.setter
    def price (self, value):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value

    @property
    def stock(self):
        """Stock function"""
        return self._stock

    def reduce_stock (self, quantity):
        """Reduces stock"""
        if quantity <=0:
            raise ValueError("Quantity must be at least 1")
        if quantity > self._stock:
            raise ValueError(f"Only {self._stock} left in stock")
        self._stock -= quantity

    def restock(self, quantity):
        """Restocks inventory"""
        if quantity <= 0:
            raise ValueError("Quantity must be at least 1")
        self._stock = quantity


class PerishableItem(Item):
    """A product that expires."""

    def __init__(self, item_id, name, price, stock, expiry_date):
        super().__init__(item_id, name, price, stock)
        self.expiry_date = expiry_date   # a date object

    def is_expired(self):
        """Checks if an item as expired"""
        return date.today() > self.expiry_date

    def reduce_stock(self, quantity):
        if self.is_expired():
            raise ValueError(f"{self.name} has expired and cannot be sold")
        super().reduce_stock(quantity)
