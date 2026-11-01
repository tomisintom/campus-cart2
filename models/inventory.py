"""Inventory Module"""
from models.item import Item

class Inventory:
    """Inventory class"""
    def __init__(self):
        self._items = {}

        starting_data = {
            "101": ("Notebook", 2.50, 15),
            "102": ("Ballpoint Pen", 1.20, 50),
            "103": ("Mechanical Pencil", 3.00, 30),
            "104": ("Highlighter Set", 4.50, 20),
            "105": ("Sticky Note", 1.80, 45),
            "106": ("Paperclips Pack", 0.99, 100),
            "107": ("Three-Ring Binder", 5.25, 12),
            "108": ("Scissors", 3.50, 25),
            "109": ("Glue Stick", 1.10, 60),
            "110": ("Stapler", 8.75, 8),
        }


        for item_id, (name, price, stock) in starting_data.items():
            self._items[item_id] = Item(item_id, name, price, stock)

    def add_item(self, item):
        """Adds item to inventory"""
        if item.item_id in self._items:
            raise ValueError("The product ID already exists")

        for existing in self._items.values():
            if existing.name.lower() == item.name.lower():
                raise ValueError("A product with that name already exists")

        self._items[item.item_id] = item

    def remove_item(self, item_id):
        """Remove a product."""
        item = self.get_item(item_id)
        item.discontinue()
        del self._items[item_id]

    def get_item(self, item_id):
        """Gets item from inventory"""
        if item_id not in self._items:
            raise ValueError("Product ID not found")
        return self._items[item_id]

    def update_price(self, item_id, new_price):
        """Updates price of item"""
        self.get_item(item_id).price = new_price

    def restock(self, item_id, quantity):
        """Restock function"""
        self.get_item(item_id).restock(quantity)

    def all_items(self):
        """Returns all items"""
        return list(self._items.values())

    def sorted_by_price(self, descending=False):
        """Sorts products by price"""
        return sorted(
            self._items.values(),  key = lambda item: item.price, reverse=descending
        )

    def sorted_by_name(self):
        """Sorts products by name"""
        return sorted(self._items.values(), key=lambda item: item.name.lower())

    def low_stock(self, threshold=10):
        """Products with stock below the threshold."""
        return list(filter(lambda item: item.stock < threshold, self._items.values()))
