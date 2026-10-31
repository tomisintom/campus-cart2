"""
Campus Cart - main.py

Runs the CLI using the inventory, cart, checkout and logger modules.
Admin access needs the ADMIN_PASSWORD environment variable to be set.
"""

import copy
import os

from inventory import (
    add_new_item,
    check_stock,
    delete_item,
    display_low_stock_report,
    display_sorted_catalog,
    verify_and_add_stock,
)
from cart import add_item, remove_item, stream_receipt_lines
from checkout import checkout

inventory = {
    "101": {"name": "Notebook", "price": 2.50, "stock": 15},
    "102": {"name": "Ballpoint Pen", "price": 1.20, "stock": 50},
    "103": {"name": "Mechanical Pencil", "price": 3.00, "stock": 30},
    "104": {"name": "Highlighter Set", "price": 4.50, "stock": 20},
    "105": {"name": "Sticky Note", "price": 1.80, "stock": 45},
    "106": {"name": "Paperclips Pack", "price": 0.99, "stock": 100},
    "107": {"name": "Three-Ring Binder", "price": 5.25, "stock": 12},
    "108": {"name": "Scissors", "price": 3.50, "stock": 25},
    "109": {"name": "Glue Stick", "price": 1.10, "stock": 60},
    "110": {"name": "Stapler", "price": 8.75, "stock": 8},
}
cart = []

while True:
    print("\n=== WELCOME TO CAMPUS CART ===")
    print("1 = I am a customer")
    print("2 = I am the admin")
    print("# = Exit")
    choice = input("Enter an option: ").strip()

    # ---------------------------- CUSTOMER ----------------------------
    if choice == "1":
        while True:
            print("\n--- How can I help you today? ---")
            print("1 = Display catalogue")
            print("2 = Add to cart")
            print("3 = View cart")
            print("4 = Remove from cart")
            print("5 = Checkout")
            print("0 = Exit Menu")
            option = input("Enter an option: ").strip()

            if option == "1":
                display_sorted_catalog(inventory)

            elif option == "2":
                query = input("Enter the item name or ID: ").strip().lower()
                item_id = None
                for product_id, details in inventory.items():
                    if query == product_id or query == details["name"].lower():
                        item_id = product_id

                if item_id is None:
                    print("Item not available, check back later.")
                else:
                    qty_text = input("How many? ").strip()
                    if not qty_text.isdigit() or int(qty_text) <= 0:
                        print("Quantity must be a whole number greater than zero.")
                    else:
                        qty = int(qty_text)
                        in_cart = 0
                        for item in cart:
                            if item["item_id"] == item_id:
                                in_cart = item["quantity"]

                        if in_cart + qty > check_stock(inventory, item_id):
                            print("Not enough stock available.")
                        else:
                            product = inventory[item_id]
                            add_item(cart, product["name"], product["price"], qty, item_id)
                            print(f"{qty} x {product['name']} added to cart.")

            elif option == "3":
                if not cart:
                    print("Your cart is empty.")
                else:
                    print()
                    for line in stream_receipt_lines(cart):
                        print(line)

            elif option == "4":
                item_id = input("Enter the ID of the item to remove: ").strip()
                qty_text = input("How many to remove? ").strip()
                if not qty_text.isdigit() or int(qty_text) <= 0:
                    print("Quantity must be a whole number greater than zero.")
                else:
                    success, message, removed = remove_item(cart, item_id, int(qty_text))
                    print(message)

            elif option == "5":
                if not cart:
                    print("Your cart is empty. Please add items before checking out.")
                else:
                    order = copy.deepcopy(cart)  # checkout() empties the cart
                    success, message, total = checkout(cart, inventory)
                    if success:
                        print("\n=== YOUR RECEIPT ===")
                        for line in stream_receipt_lines(order):
                            print(line)
                        print(f"Total (after discounts & tax): ${total:.2f}")
                        print("Thank you for your patronage. See you again!")
                    else:
                        print(f"Checkout failed: {message}")

            elif option == "0":
                break
            else:
                print("Enter a valid option.")

    # ------------------------------ ADMIN -----------------------------
    elif choice == "2":
        admin_password = os.environ.get("ADMIN_PASSWORD")
        if not admin_password:
            print("ADMIN PASSWORD NOT SET. Set the ADMIN_PASSWORD environment variable and restart.")
        elif input("Admin password: ") != admin_password:
            print("ACCESS DENIED! Wrong password.")
        else:
            print("Welcome back, Admin.")
            while True:
                print("\n--- Admin Menu ---")
                print("1 = Display inventory")
                print("2 = Low stock report")
                print("3 = Restock a product")
                print("4 = Add new product")
                print("5 = Delete a product")
                print("0 = Exit Menu")
                option = input("Enter an option: ").strip()

                if option == "1":
                    display_sorted_catalog(inventory)

                elif option == "2":
                    limit_text = input("Show items with stock below: ").strip()
                    if limit_text.isdigit():
                        display_low_stock_report(inventory, int(limit_text))
                    else:
                        print("Enter a whole number.")

                elif option == "3":
                    item_id = input("Enter the product ID: ").strip()
                    qty_text = input("How many units to add? ").strip()
                    if not qty_text.isdigit() or int(qty_text) <= 0:
                        print("Enter a whole number greater than zero.")
                    else:
                        print(verify_and_add_stock(inventory, item_id, int(qty_text))[1])

                elif option == "4":
                    item_id = input("New product ID: ").strip()
                    name = input("Product name: ").strip()
                    try:
                        price = float(input("Price: $"))
                        stock = int(input("Stock quantity: "))
                    except ValueError:
                        print("Price must be a number and stock a whole number.")
                        continue
                    if not name or price <= 0 or stock < 0:
                        print("Name can't be empty, price must be above 0 and stock can't be negative.")
                    else:
                        print(add_new_item(inventory, item_id, name, price, stock)[1])

                elif option == "5":
                    item_id = input("Enter the product ID to delete: ").strip()
                    print(delete_item(inventory, item_id)[1])

                elif option == "0":
                    break
                else:
                    print("Enter a valid option.")

    elif choice == "#":
        print("Goodbye!")
        break
    else:
        print("Enter a valid option.")