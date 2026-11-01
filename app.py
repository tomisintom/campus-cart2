import os
import time
from datetime import date, timedelta

import streamlit as st

from models.inventory import Inventory
from models.item import Item, PerishableItem
from models.cart import ShoppingCart
from models.payment import CashPayment, CardPayment, MobileMoneyPayment
from utils.receipts import cart_table, stream_receipt_lines
from utils.logger import LOG_FILE

st.set_page_config(page_title="CampusCart", page_icon="🛒", layout="wide")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


# Memory: created once, kept between clicks

if "inventory" not in st.session_state:
    st.session_state.inventory = Inventory()
if "cart" not in st.session_state:
    st.session_state.cart = ShoppingCart()

st.session_state.setdefault("flash", [])
st.session_state.setdefault("receipt", None)
st.session_state.setdefault("receipt_streamed", False)
st.session_state.setdefault("admin_ok", False)

inventory = st.session_state.inventory
cart = st.session_state.cart



# Messages (shown at the top of the next run)

def flash(kind, message):
    st.session_state.flash.append((kind, message))


def show_flash():
    for kind, message in st.session_state.flash:
        if kind == "toast":
            st.toast(message, icon="🛒")
        elif kind == "success":
            st.success(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.error(message)
    st.session_state.flash = []



# Button actions (callbacks). They call the models and catch errors.

def add_to_cart(item_id):
    item = st.session_state.inventory.get_item(item_id)
    qty = int(st.session_state[f"qty_{item_id}"])
    try:
        st.session_state.cart.add_item(item, qty)
        flash("toast", f"{qty} x {item.name} added to cart")
    except ValueError as error:
        flash("warning", str(error))


def remove_one(item_id):
    try:
        st.session_state.cart.remove_item(item_id, 1)
    except ValueError as error:
        flash("warning", str(error))


def remove_line(item_id):
    try:
        st.session_state.cart.remove_item(item_id)
    except ValueError as error:
        flash("warning", str(error))


def pay_now():
    method = st.session_state.pay_method
    try:
        if method == "Cash":
            payment = CashPayment(st.session_state.cash_given)
        elif method == "Card":
            payment = CardPayment(st.session_state.card_no)
        else:
            payment = MobileMoneyPayment(st.session_state.phone_no)
        summary = st.session_state.cart.checkout(payment)
    except ValueError as error:
        flash("error", f"Payment failed: {error}")
        return

    st.session_state.receipt = summary
    st.session_state.receipt_streamed = False
    flash("success", "Payment successful! Your receipt is below.")


def close_receipt():
    st.session_state.receipt = None


def logout():
    st.session_state.admin_ok = False

def go_to(page):
    st.session_state.page = page


def cart_count():
    return sum(line["qty"] for line in cart.view_cart())



# CUSTOMER SCREEN

def render_card(item):
    expired = isinstance(item, PerishableItem) and item.is_expired()
    unavailable = expired or item.stock == 0

    with st.container(border=True):
        st.markdown(f"#### 📦 {item.name}")
        st.caption(f"ID: {item.item_id}")
        st.markdown(f"### ${item.price:.2f}")

        if expired:
            st.error("Expired")
        elif item.stock == 0:
            st.error("Out of stock")
        elif item.stock < 10:
            st.warning(f"Only {item.stock} left")
        else:
            st.caption(f"{item.stock} in stock")

        if isinstance(item, PerishableItem):
            st.caption(f"Expires: {item.expiry_date:%d %b %Y}")

        st.number_input(
            "Quantity", min_value=1, value=1, step=1,
            key=f"qty_{item.item_id}", disabled=unavailable,
        )
        st.button(
            "Add to cart", key=f"add_{item.item_id}",
            on_click=add_to_cart, args=(item.item_id,),
            disabled=unavailable, use_container_width=True,
        )


def render_catalog():
    st.subheader("🛍️ Catalogue")

    st.button(f"🛒 View cart ({cart_count()})", on_click=go_to, args=("cart",))

    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search products", placeholder="e.g. pen")
    sort_by = c2.selectbox(
        "Sort by", ["Name (A-Z)", "Price: low to high", "Price: high to low"]
    )

    if sort_by == "Name (A-Z)":
        items = inventory.sorted_by_name()
    elif sort_by == "Price: low to high":
        items = inventory.sorted_by_price()
    else:
        items = inventory.sorted_by_price(descending=True)

    if search:
        items = list(filter(lambda i: search.lower() in i.name.lower(), items))

    if not items:
        st.info("No products match your search.")
        return

    per_row = 4
    for start in range(0, len(items), per_row):
        columns = st.columns(per_row)
        for column, item in zip(columns, items[start:start + per_row]):
            with column:
                render_card(item)


def render_receipt():
    summary = st.session_state.receipt
    if not summary:
        return

    st.subheader("🧾 Receipt")
    box = st.empty()

    if st.session_state.receipt_streamed:
        box.code("\n".join(stream_receipt_lines(summary)), language=None)
    else:
        text = ""
        for line in stream_receipt_lines(summary):   # the generator, one line at a time
            text += line + "\n"
            box.code(text, language=None)
            time.sleep(0.08)
        st.session_state.receipt_streamed = True

    payment = summary["payment"]
    st.caption(f"Paid with {payment['method']}")
    if "change" in payment:
        st.info(f"Change: ${payment['change']:.2f}")
    st.button("Close receipt", on_click=close_receipt)
    st.divider()


def render_cart_panel():
    st.subheader("🛒 Your cart")

    removed = cart.remove_unavailable()
    if removed:
        st.warning("Removed from your cart (no longer available): " + ", ".join(removed))

    if cart.is_empty():
        st.info("Your cart is empty. Add items from the catalogue.")
        st.button("Start shopping", on_click=go_to, args=("shop",))
        return

    st.code(cart_table(cart), language=None)

    for line in cart.view_cart():
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"{line['name']} × {line['qty']}")
        c2.button("−1", key=f"minus_{line['item_id']}",
                  on_click=remove_one, args=(line["item_id"],))
        c3.button("✖", key=f"del_{line['item_id']}",
                  on_click=remove_line, args=(line["item_id"],))

    st.divider()
    st.subheader("💳 Checkout")
    st.metric("Amount to pay", f"${cart.calculate_total():.2f}")
    if cart.discount() > 0:
        st.caption(f"10% discount applied (-${cart.discount():.2f})")

    method = st.selectbox("Payment method", ["Cash", "Card", "Mobile Money"],
                          key="pay_method")
    if method == "Cash":
        st.number_input("Amount given ($)", min_value=0.0, step=1.0, key="cash_given")
    elif method == "Card":
        st.text_input("Card number (16 digits)", key="card_no")
    else:
        st.text_input("Phone number (11 digits)", key="phone_no")

    st.button("Pay now", type="primary", on_click=pay_now, use_container_width=True)



# ADMIN SCREEN

def pick_item(label, key):
    ids = [i.item_id for i in inventory.all_items()]
    if not ids:
        st.info("The inventory is empty.")
        return None
    return st.selectbox(
        label, ids, key=key,
        format_func=lambda x: f"{x} - {inventory.get_item(x).name}",
    )


def admin_gate():
    if st.session_state.admin_ok:
        return True

    st.header("🔒 Admin login")
    if not ADMIN_PASSWORD:
        st.warning(
            "ADMIN PASSWORD NOT SET. Set the ADMIN_PASSWORD environment "
            "variable and restart the app."
        )
        return False

    password = st.text_input("Admin password", type="password")
    if st.button("Log in"):
        if password == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.rerun()
        else:
            st.error("ACCESS DENIED! Wrong password.")
    return False


def render_admin():
    top1, top2 = st.columns([5, 1])
    top1.header("🛠️ Admin dashboard")
    top2.button("Log out", on_click=logout)

    section = st.radio(
        "Menu",
        ["View inventory", "Add product", "Update price", "Restock",
         "Remove product", "Customer cart", "Transaction log"],
        horizontal=True, key="admin_section",
    )
    st.divider()

    if section == "View inventory":
        rows = [
            {
                "ID": i.item_id,
                "Name": i.name,
                "Price ($)": i.price,
                "Stock": i.stock,
                "Type": "Perishable" if isinstance(i, PerishableItem) else "Standard",
            }
            for i in inventory.all_items()
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        threshold = st.number_input("Low-stock threshold", min_value=1, value=10, step=1)
        low = inventory.low_stock(threshold)
        if low:
            st.warning("Low stock: " + ", ".join(f"{i.name} ({i.stock})" for i in low))
        else:
            st.success("Nothing is below the threshold.")

    elif section == "Add product":
        with st.form("add_product", clear_on_submit=True):
            c1, c2 = st.columns(2)
            item_id = c1.text_input("Product ID")
            name = c2.text_input("Product name")
            price = c1.number_input("Price ($)", min_value=0.01, step=0.5, format="%.2f")
            stock = c2.number_input("Stock", min_value=0, step=1)
            perishable = st.checkbox("Perishable (has an expiry date)")
            expiry = st.date_input("Expiry date (used only if perishable)",
                                   value=date.today() + timedelta(days=7))
            submitted = st.form_submit_button("Add product")

        if submitted:
            try:
                item_id = item_id.strip()
                if not item_id:
                    raise ValueError("Product ID cannot be empty")
                if perishable:
                    new_item = PerishableItem(item_id, name, price, int(stock), expiry)
                else:
                    new_item = Item(item_id, name, price, int(stock))
                inventory.add_item(new_item)
                flash("success", f"{new_item.name} added successfully.")
                st.rerun()
            except ValueError as error:
                st.error(f"Could not add product: {error}")

    elif section == "Update price":
        item_id = pick_item("Product", "price_pick")
        if item_id:
            current = inventory.get_item(item_id).price
            new_price = st.number_input("New price ($)", min_value=0.01,
                                        value=float(current), step=0.5, format="%.2f")
            if st.button("Update price"):
                try:
                    inventory.update_price(item_id, new_price)
                    flash("success", "Price updated successfully.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    elif section == "Restock":
        item_id = pick_item("Product", "restock_pick")
        if item_id:
            st.caption(f"Current stock: {inventory.get_item(item_id).stock}")
            quantity = st.number_input("Units to add", min_value=1, step=1)
            if st.button("Restock"):
                try:
                    inventory.restock(item_id, int(quantity))
                    flash("success", "Stock updated successfully.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    elif section == "Remove product":
        item_id = pick_item("Product", "remove_pick")
        if item_id:
            sure = st.checkbox("Yes, remove this product permanently")
            if st.button("Remove product", disabled=not sure):
                try:
                    inventory.remove_item(item_id)
                    flash("success", "Product removed.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

    elif section == "Customer cart":
        st.code(cart_table(cart), language=None)

    else:
        st.subheader("Transaction log")
        if not os.path.exists(LOG_FILE):
            st.info("No transactions yet.")
        else:
            with open(LOG_FILE, encoding="utf-8") as file:
                text = file.read()
            query = st.text_input("Search (for example a Transaction ID)")
            entries = [b for b in text.split("\n\n") if b.strip()]
            if query:
                entries = [b for b in entries if query.lower() in b.lower()]
            st.caption(f"{len(entries)} entries, newest first")
            st.code("\n\n".join(reversed(entries)), language=None)
            st.download_button("Download log", text, file_name="transactions.txt")




# PAGE LAYOUT
st.session_state.setdefault("page", "shop")

with st.sidebar:
    st.title("🛒 CampusCart")
    mode = st.radio("I am a...", ["Customer", "Admin"])

    if mode == "Customer":
        st.divider()
        st.radio(
            "Go to",
            ["shop", "cart"],
            key="page",
            format_func=lambda p: (
                "🛍️ Shop" if p == "shop"
                else f"🛒 Cart & Checkout ({cart_count()})"
            ),
        )
    st.caption("Campus stationery shop")

show_flash()

if mode == "Customer":
    if st.session_state.page == "shop":
        render_catalog()
    else:
        st.button("← Back to shop", on_click=go_to, args=("shop",))
        render_receipt()
        render_cart_panel()
else:
    if admin_gate():
        render_admin()