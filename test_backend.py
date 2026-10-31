"""Test Module"""
from datetime import date, timedelta
from models.inventory import Inventory
from models.item import Item
from models.cart import ShoppingCart
from models.item import PerishableItem
from models.payment import CardPayment, CashPayment, MobileMoneyPayment
from utils.receipts import stream_receipt_lines

# Item Class Testing
pen = Item(1, "Pen", 150, 10)
print(pen.name, pen.price, pen.stock)

pen.reduce_stock(3)
print(pen.stock)

try:
    pen.reduce_stock(50)
except ValueError as e:
    print("Caught:", e)

try:
    pen.price = -20
except ValueError as e:
    print("Caught:", e)

try:
    pen.stock = 999
except AttributeError as e:
    print("Caught:", e)

print("------")
# Inventory Class Testing
inv = Inventory()
print(len(inv.all_items()))

inv.add_item(Item("111", "Eraser", 0.50, 40))
print(len(inv.all_items()))

inv.update_price("101", 3.00)
print(inv.get_item("101").price)

inv.remove_item("111")
print(len(inv.all_items()))

inv.restock("101", 20)
print(inv.get_item("101").stock)


try:
    inv.get_item("999")
except ValueError as e:
    print("Caught:", e)

print("------")
# Error Catching Test
for bad in [
    ("200", "", 1.0, 5),
    ("201", "Ruler", -1.0, 5),
    ("202", "Ruler", 1.0, -5),
]:
    try:
        Item(*bad)
    except ValueError as e:
        print("Caught:", e)

try:
    inv.add_item(Item("101", "Marker", 1.0, 5))
except ValueError as e:
    print("Caught:", e)

try:
    inv.add_item(Item("300", "notebook", 1.0, 5))
except ValueError as e:
    print("Caught:", e)


print("------")
print("Cart Testing")

# Cart Testing
inv = Inventory()
cart = ShoppingCart()

cart.add_item(inv.get_item("101"), 2)
cart.add_item(inv.get_item("110"), 2)
cart.add_item(inv.get_item("101"), 1)

print(cart.view_cart())
print(cart.subtotal())
print(cart.discount())
print(cart.calculate_total())

try:
    cart.add_item(inv.get_item("110"), 50)
except ValueError as e:
    print("Caught:", e)

cart.remove_item("101", 1)
print(cart.calculate_total())

try:
    cart.remove_item("101", 10)
except ValueError as e:
    print("Caught:", e)

summary = cart.checkout(CashPayment(100))
print(summary["total"])
print(inv.get_item("101").stock)
print(inv.get_item("110").stock)
print(cart.is_empty())

try:
    cart.checkout(CashPayment(100))
except ValueError as e:
    print("Caught:", e)


print("------")
# Sorting Testing
inv = Inventory()

print("Cheapest first:")
for item in inv.sorted_by_price():
    print(" ", item.name, item.price)

print("Most expensive first:")
for item in inv.sorted_by_price(descending=True):
    print(" ", item.name, item.price)

print("Low stock (below 10):")
for item in inv.low_stock():
    print(" ", item.name, item.stock)

print("------")
# Recipts Testing
# Generator Testing
inv = Inventory()
cart = ShoppingCart()
cart.add_item(inv.get_item("101"), 3)
cart.add_item(inv.get_item("110"), 2)

summary = cart.checkout(CashPayment(100))

for receipt_line in stream_receipt_lines(summary):
    print(receipt_line)


print("------")
# Testing logger

inv = Inventory()
cart = ShoppingCart()
cart.add_item(inv.get_item("102"), 4)
cart.checkout(CashPayment(100))

try:
    cart.checkout(CashPayment(100))
except ValueError as e:
    print("Caught:", e)



print("------")
# Payment Testing
methods = [
    CashPayment(50),
    CardPayment("1234 5678 9012 3456"),
    MobileMoneyPayment("08012345678"),
]

for payment in methods:
    print(payment.process_payment(22.50))

try:
    CashPayment(10).process_payment(22.50)
except ValueError as e:
    print("Caught:", e)
try:
    CardPayment("123").process_payment(22.50)
except ValueError as e:
    print("Caught:", e)



# Subclass Testing
print("------")
bread = PerishableItem("201", "Bread", 2.00, 10, date.today() + timedelta(days=2))
old_milk = PerishableItem("202", "Milk", 3.00, 5, date.today() - timedelta(days=1))

bread.reduce_stock(2)
print(bread.stock)

try:
    old_milk.reduce_stock(1)
except ValueError as e:
    print("Caught:", e)

inv = Inventory()
inv.add_item(bread)
cart = ShoppingCart()
cart.add_item(inv.get_item("201"), 3)
print(cart.subtotal())
