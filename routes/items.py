from flask import Blueprint, request, jsonify, render_template
from models import db, Item, Category
from utils.helpers import format_currency

bp = Blueprint("items", __name__, url_prefix="/items")


# 🧾 List all items
@bp.route("/", methods=["GET"])
def list_items():
    items = Item.query.all()
    data = [
        {
            "id": i.id,
            "barcode": i.barcode,
            "name": i.name,
            "category": i.category.name if i.category else "Uncategorized",
            "price": format_currency(i.price),
            "quantity": i.quantity
        }
        for i in items
    ]
    return jsonify(data), 200


# ➕ Add new item
@bp.route("/add", methods=["POST"])
def add_item():
    data = request.get_json() or request.form
    barcode = data.get("barcode")
    name = data.get("name")
    category_id = data.get("category_id")
    price = float(data.get("price", 0))
    quantity = int(data.get("quantity", 0))

    if not all([barcode, name, price]):
        return jsonify({"error": "Missing required fields"}), 400

    # Prevent duplicate barcodes
    if Item.query.filter_by(barcode=barcode).first():
        return jsonify({"error": "Item already exists"}), 409

    item = Item(
        barcode=barcode,
        name=name,
        category_id=category_id,
        price=price,
        quantity=quantity
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({"message": "Item added successfully", "item_id": item.id}), 201


# ✏️ Update item
@bp.route("/update/<int:item_id>", methods=["PUT", "POST"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json() or request.form
    item.name = data.get("name", item.name)
    item.barcode = data.get("barcode", item.barcode)
    item.price = float(data.get("price", item.price))
    item.quantity = int(data.get("quantity", item.quantity))
    category_id = data.get("category_id")
    if category_id:
        item.category_id = category_id

    db.session.commit()
    return jsonify({"message": "Item updated successfully"}), 200


# ❌ Delete item
@bp.route("/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"}), 200


# 🔍 Lookup item by barcode
@bp.route("/lookup/<barcode>", methods=["GET"])
def lookup_item(barcode):
    item = Item.query.filter_by(barcode=barcode).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({
        "id": item.id,
        "barcode": item.barcode,
        "name": item.name,
        "category": item.category.name if item.category else "Uncategorized",
        "price": item.price,
        "quantity": item.quantity
    }), 200


# 🧱 Page route (for UI)
@bp.route("/manage", methods=["GET"])
def manage_items_page():
    categories = Category.query.all()
    return render_template("items.html", categories=categories)

# 🛒 Checkout route
@bp.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json() or {}
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "Cart is empty"}), 400

    total = 0
    receipt_lines = []
    adjusted_cart = []

    for i in items:
        barcode = i.get("barcode")
        qty = int(i.get("qty", 0))
        item_in_db = Item.query.filter_by(barcode=barcode).first()

        if not item_in_db:
            continue  # skip unknown items

        # Cap quantity to available stock
        actual_qty = min(qty, item_in_db.quantity)
        if actual_qty <= 0:
            continue  # skip if out of stock

        price = float(item_in_db.price)
        name = item_in_db.name
        line_total = actual_qty * price
        total += line_total
        receipt_lines.append(f"<li>{name} x{actual_qty} = {line_total:.2f} KSh</li>")

        # Reduce stock
        item_in_db.quantity -= actual_qty
        adjusted_cart.append({"barcode": barcode, "qty": actual_qty, "name": name, "price": price})

    if not adjusted_cart:
        return jsonify({"error": "All items are out of stock or invalid"}), 400

    db.session.commit()

    # Generate receipt HTML
    receipt_html = "<h2>FidPOS Receipt</h2><ul>"
    receipt_html += "".join(receipt_lines)
    receipt_html += f"</ul><strong>Total: {total:.2f} KSh</strong>"

    return jsonify({"receiptHtml": receipt_html, "itemsProcessed": adjusted_cart, "total": total}), 200
